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
  echo "نحوه استفاده: build-scripts/build_macos.sh <نسخه>"
  echo "مثال: build-scripts/build_macos.sh v0.2.0"
  exit 1
fi

# تعریف مسیر پوشه releases برای ذخیره خروجی نهایی
RELEASES_DIR="releases"

echo "شروع فرآیند ساخت پکیج macOS برای نسخه: $VERSION"

# 1. بررسی پیش نیازها
echo "بررسی پیش نیازها..."
command -v python3 >/dev/null 2>&1 || { echo >&2 "خطا: python3 نصب نیست."; exit 1; }
command -v pip >/dev/null 2>&1 || { echo >&2 "خطا: pip نصب نیست."; exit 1; }
command -v pyinstaller >/dev/null 2>&1 || { echo >&2 "خطا: pyinstaller نصب نیست. با 'pip install pyinstaller' نصب کنید."; exit 1; }
command -v pkgbuild >/dev/null 2>&1 || { echo >&2 "خطا: pkgbuild یافت نشد. ابزارهای خط فرمان Xcode را با 'xcode-select --install' نصب کنید."; exit 1; }
command -v rsync >/dev/null 2>&1 || { echo >&2 "خطا: rsync نصب نیست."; exit 1; }
echo "پیش نیازها بررسی شدند."

# 2. نصب وابستگی های پایتون
echo "نصب وابستگی های پایتون..."
# اختیاری: ایجاد و فعال سازی محیط مجازی (اگر نیاز دارید)
# python3 -m venv venv_build
# source venv_build/bin/activate
pip install -r requirements.txt
echo "وابستگی ها نصب شدند."

# 3. ساخت پوشه اجرایی با PyInstaller (--onedir برای macOS)
echo "ساخت پوشه اجرایی با PyInstaller..."
pyinstaller --onedir git_cmsg.py
echo "ساخت PyInstaller کامل شد."

# 4. ایجاد ساختار پکیج و کپی فایل ها
echo "ایجاد ساختار پکیج و کپی فایل ها..."
PACKAGING_DIR="packaging"
PAYLOAD_DIR="$PACKAGING_DIR/payload"
SCRIPTS_DIR="$PACKAGING_DIR/scripts" # پوشه اسکریپت ها
INSTALL_LIB_DIR="$PAYLOAD_DIR/usr/local/lib/git-cmsg" # مسیر نصب در سیستم مقصد
INSTALL_BIN_DIR="$PAYLOAD_DIR/usr/local/bin" # مسیر ایجاد symbolic link در سیستم مقصد

# پاکسازی پوشه packaging قبلی (اگر وجود دارد)
rm -rf "$PACKAGING_DIR"

# ایجاد دایرکتوری های لازم در ساختار پکیج
mkdir -p "$INSTALL_LIB_DIR"
mkdir -p "$SCRIPTS_DIR" # *** اطمینان از ایجاد پوشه اسکریپت ها ***
mkdir -p "$INSTALL_BIN_DIR"

# کپی کردن کل محتوای پوشه dist/git_cmsg به پوشه مقصد در ساختار پکیج با rsync
rsync -a dist/git_cmsg/ "$INSTALL_LIB_DIR/"

echo "ساختار پکیج ایجاد و فایل ها کپی شدند."

# --- 5. ایجاد اسکریپت های preinstall و postinstall در پوشه موقتی scripts ---
echo "Creating preinstall and postinstall scripts in temporary scripts directory..."

# تعریف مسیر اسکریپت ها در پوشه موقتی packaging/scripts
PREINSTALL_SCRIPT="$SCRIPTS_DIR/preinstall"
POSTINSTALL_SCRIPT="$SCRIPTS_DIR/postinstall"

# *** شروع: ایجاد فایل اسکریپت preinstall با استفاده از محتوای بالا ***
echo "Writing preinstall script content to $PREINSTALL_SCRIPT..."
cat <<EOF > "$PREINSTALL_SCRIPT"
#!/bin/bash

# preinstall script for Git-CMSG macOS package

# This script runs BEFORE the new files are copied.
# Its purpose is to clean up previous installations if they exist.

# Exit immediately if a command exits with a non-zero status.
set -e

# Standard installation paths used by our pkg
# Ensure these match the paths used in build_macos.sh and postinstall
LINK_PATH="/usr/local/bin/git-cmsg"
INSTALL_DIR="/usr/local/lib/git-cmsg" # The main app folder

echo "Git-CMSG preinstall script: Checking for previous installation..."

# Check if the symlink exists and is a symlink, then remove it
if [ -L "$LINK_PATH" ]; then
  echo "Removing old symlink: $LINK_PATH"
  rm "$LINK_PATH"
fi

# Check if the installation directory exists and is a directory, then remove it
if [ -d "$INSTALL_DIR" ]; then
  echo "Removing old installation directory: $INSTALL_DIR"
  rm -rf "$INSTALL_DIR"
fi

echo "Git-CMSG preinstall script: Cleanup complete."

exit 0 # Indicate success to the installer
EOF
# *** پایان: ایجاد فایل اسکریپت preinstall ***


# *** شروع: ایجاد فایل اسکریپت postinstall ***
echo "Writing postinstall script content to $POSTINSTALL_SCRIPT..."
cat <<EOF > "$POSTINSTALL_SCRIPT"
#!/bin/sh
# postinstall script for Git-CMSG (macOS)

# This script runs AFTER the new files are copied.
# Its purpose is to create necessary links or perform final setups.

# Installation directory (must match payload structure and preinstall)
INSTALL_DIR="/usr/local/lib/git-cmsg"
# Path to the main executable inside the installed directory
EXECUTABLE="\$INSTALL_DIR/git_cmsg"
# Path where the symbolic link should be created
LINK_PATH="/usr/local/bin/git-cmsg"

echo "Git-CMSG postinstall script: Creating symlink..."

# Ensure the executable is executable
chmod +x "\$EXECUTABLE"

# Create symbolic link in bin path
# Remove existing link if it exists (preinstall should handle this, but good to be safe)
if [ -L "\$LINK_PATH" ]; then
  rm "\$LINK_PATH"
fi
# Create the new link
ln -s "\$EXECUTABLE" "\$LINK_PATH"

echo "Git-CMSG postinstall script: Symlink created."

exit 0
EOF
# *** پایان: ایجاد فایل اسکریپت postinstall ***


# اجرایی کردن هر دو اسکریپت
chmod +x "$PREINSTALL_SCRIPT"
chmod +x "$POSTINSTALL_SCRIPT"

echo "Preinstall and postinstall scripts created and made executable."

# --- 6. ایجاد پوشه releases و ساخت پکیج .pkg با pkgbuild ---
echo "Building .pkg package and saving to releases directory..."

# ایجاد پوشه releases اگر وجود ندارد
mkdir -p "$RELEASES_DIR"

# ساخت پکیج با pkgbuild
# پارامتر --scripts "$SCRIPTS_DIR" باعث می شود نصاب، اسکریپت های اجرایی با نام های استاندارد
# (مانند preinstall و postinstall) را از این پوشه شناسایی و اجرا کند و آنها را در پکیج نهایی قرار دهد.
# ${VERSION#v} removes the leading 'v' from the version string
pkgbuild --root "$PAYLOAD_DIR" \
         --scripts "$SCRIPTS_DIR" \
         --identifier com.arashzich.git-cmsg \
         --version ${VERSION#v} \
         --install-location / \
         "$RELEASES_DIR/git-cmsg-${VERSION#v}.pkg" # مسیر خروجی به داخل پوشه releases

echo ".pkg package built."

# 7. پاکسازی فایل های موقت
echo "Cleaning up build artifacts..."
rm -rf build/
rm -rf dist/
rm -rf "$PACKAGING_DIR" # پاکسازی پوشه packaging
# غیرفعال کردن محیط مجازی اگر استفاده شد
# deactivate
echo "Cleanup complete."

echo "macOS package build process finished."
echo "Package (.pkg) is in the '$RELEASES_DIR' directory in the project root."