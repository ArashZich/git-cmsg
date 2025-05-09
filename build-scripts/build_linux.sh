#!/bin/bash

# اگر هر دستوری با خطا مواجه شد، بلافاصله خارج شو
set -e

# --- تغییر دایرکتوری کاری به ریشه پروژه ---
# دریافت مسیر دایرکتوری که اسکریپت در آن قرار دارد
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# تغییر دایرکتوری کاری به یک سطح بالاتر (ریشه پروژه)
cd "$SCRIPT_DIR/.."
echo "دایرکتوری کاری به: $(pwd) تغییر یافت."
# --- پایان تغییر دایرکتوری ---

# بررسی وجود نسخه به عنوان ورودی
VERSION=$1
if [ -z "$VERSION" ]; then
  echo "نحوه استفاده: build-scripts/build_linux.sh <نسخه>"
  echo "مثال: build-scripts/build_linux.sh v0.2.0"
  exit 1
fi

# تعریف مسیر پوشه releases برای ذخیره خروجی نهایی
RELEASES_DIR="releases"

echo "شروع فرآیند ساخت پکیج های لینوکس برای نسخه: $VERSION"

# 1. بررسی پیش نیازها
echo "بررسی پیش نیازها..."
command -v python3 >/dev/null 2>&1 || { echo >&2 "خطا: python3 نصب نیست."; exit 1; }
command -v pip >/dev/null 2>&1 || { echo >&2 "خطا: pip نصب نیست."; exit 1; }
command -v pyinstaller >/dev/null 2>&1 || { echo >&2 "خطا: pyinstaller نصب نیست. با 'pip install pyinstaller' نصب کنید."; exit 1; }
command -v fpm >/dev/null 2>&1 || { echo >&2 "خطا: fpm نصب نیست. ruby/ruby-dev و سپس 'sudo gem install fpm' را نصب کنید."; exit 1; }
command -v ruby >/dev/null 2>&1 || { echo >&2 "خطا: ruby نصب نیست."; exit 1; }
command -v gem >/dev/null 2>&1 || { echo >&2 "خطا: gem نصب نیست."; exit 1; }
echo "پیش نیازها بررسی شدند."

# 2. نصب وابستگی های پایتون
echo "نصب وابستگی های پایتون..."
# اختیاری: ایجاد و فعال سازی محیط مجازی (اگر نیاز دارید)
# python3 -m venv venv_build
# source venv_build/bin/activate
pip install -r requirements.txt
echo "وابستگی ها نصب شدند."

# 3. ساخت فایل اجرایی با PyInstaller (--onefile برای لینوکس)
echo "ساخت فایل اجرایی با PyInstaller..."
pyinstaller --onefile git_cmsg.py
echo "ساخت PyInstaller کامل شد."

# --- 4. ایجاد ساختار موقت برای اسکریپت های نصاب لینوکس ---
echo "Creating temporary structure for Linux installer scripts..."
LINUX_PACKAGING_DIR="linux_packaging"
LINUX_SCRIPTS_DIR="$LINUX_PACKAGING_DIR/scripts"

# پاکسازی پوشه موقت قبلی (اگر وجود دارد)
rm -rf "$LINUX_PACKAGING_DIR"

# ایجاد دایرکتوری های لازم
mkdir -p "$LINUX_SCRIPTS_DIR"

# --- 5. ایجاد فایل اسکریپت preinst در پوشه موقت ---
echo "Creating preinst script file in temporary directory..."

# تعریف مسیر فایل preinst در پوشه موقت
PREINST_SCRIPT="$LINUX_SCRIPTS_DIR/preinst"

# نوشتن محتوای اسکریپت preinst (مطابق بخش 1 بالا) در فایل
cat <<EOF > "$PREINST_SCRIPT"
#!/bin/bash

# preinst script for Git-CMSG Linux packages (.deb, .rpm)

# This script runs BEFORE the new package files are installed.
# Its purpose is to clean up potential old files from previous installations
# (e.g., if installed manually or by an older package version).

# Exit immediately if a command exits with a non-zero status.
set -e

# Path to the executable installed by previous versions or manual methods
# This assumes /usr/bin is the standard target directory for our package
EXECUTABLE_PATH="/usr/bin/git-cmsg"

echo "Git-CMSG preinst script: Checking for old executable..."

# Check if the executable exists and is a file, then remove it
if [ -f "$EXECUTABLE_PATH" ]; then
  echo "Removing old executable: $EXECUTABLE_PATH"
  # Use rm directly. Package manager runs preinst with root privileges.
  rm "$EXECUTABLE_PATH"
fi

# Could add cleanup for config files here if they were introduced
# For example:
# CONFIG_DIR="/etc/git-cmsg" # Example config directory
# if [ -d "$CONFIG_DIR" ]; then
#   echo "Removing old config directory: $CONFIG_DIR"
#   rm -rf "$CONFIG_DIR"
# fi

echo "Git-CMSG preinst script: Cleanup complete."

exit 0 # Indicate success to the package manager
EOF

# اجرایی کردن فایل اسکریپت preinst
chmod +x "$PREINST_SCRIPT"

echo "Preinst script created and made executable."

# --- 6. ایجاد پوشه releases و ساخت پکیج های .deb و .rpm با FPM ---
echo "Building packages and saving to releases directory..."

# ایجاد پوشه releases اگر وجود ندارد
mkdir -p "$RELEASES_DIR"

# ساخت پکیج .deb با FPM و ذخیره در releases
echo "Building .deb package..."
# ${VERSION#v} برای حذف حرف 'v' از ابتدای رشته نسخه
fpm -s dir -t deb \
    -n git-cmsg \
    -v ${VERSION#v} \
    --description "ابزار پیام‌های کامیت گیت" \
    --maintainer "arashzich1992@gmail.com" \
    --vendor "ArashZich" \
    --license "GPL-3.0" \
    --depends "python3 (>= 3.6)" \
    --depends "git" \
    --before-install "$PREINST_SCRIPT" \
    dist/git_cmsg=/usr/bin/git-cmsg \
    --output-path "$RELEASES_DIR/" # ذخیره خروجی در پوشه releases

echo ".deb package built."

# ساخت پکیج .rpm با FPM و ذخیره در releases
echo "Building .rpm package..."
fpm -s dir -t rpm \
    -n git-cmsg \
    -v ${VERSION#v} \
    --description "ابزار پیام‌های کامیت گیت" \
    --maintainer "arashzich1992@gmail.com" \
    --vendor "ArashZich" \
    --license "GPL-3.0" \
    --depends "python3 >= 3.6" \
    --depends "git" \
    --before-install "$PREINST_SCRIPT" \
    dist/git_cmsg=/usr/bin/git-cmsg \
    --output-path "$RELEASES_DIR/" # ذخیره خروجی در پوشه releases

echo ".rpm package built."

# 7. پاکسازی فایل های موقت
echo "Cleaning up build artifacts..."
rm -rf build/
rm -rf dist/
rm -rf "$LINUX_PACKAGING_DIR" # *** پاکسازی پوشه موقت اسکریپت های لینوکس ***
# Deactivate venv if used
# deactivate
echo "Cleanup complete."

echo "Linux package build process finished."
echo "Packages (.deb, .rpm) are in the '$RELEASES_DIR' directory in the project root."