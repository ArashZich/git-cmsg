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
command -v rsync >/dev/null 2>&1 || { echo >&2 "خطا: rsync نصب نیست."; exit 1; } # rsync معمولا روی macOS از قبل نصب است
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

# 4. ایجاد ساختار پکیج و کپی فایل ها (مطابق اصلاحات قبلی)
echo "ایجاد ساختار پکیج و کپی فایل ها..."
PACKAGING_DIR="packaging"
PAYLOAD_DIR="$PACKAGING_DIR/payload"
SCRIPTS_DIR="$PACKAGING_DIR/scripts"
INSTALL_LIB_DIR="$PAYLOAD_DIR/usr/local/lib/git-cmsg" # مسیر نصب در سیستم مقصد
INSTALL_BIN_DIR="$PAYLOAD_DIR/usr/local/bin" # مسیر ایجاد symbolic link در سیستم مقصد

# پاکسازی پوشه packaging قبلی (اگر وجود دارد)
rm -rf "$PACKAGING_DIR"

# ایجاد دایرکتوری های لازم در ساختار پکیج
mkdir -p "$INSTALL_LIB_DIR"
mkdir -p "$SCRIPTS_DIR"
mkdir -p "$INSTALL_BIN_DIR"

# کپی کردن کل محتوای پوشه dist/git_cmsg به پوشه مقصد در ساختار پکیج با rsync
rsync -a dist/git_cmsg/ "$INSTALL_LIB_DIR/"

echo "ساختار پکیج ایجاد و فایل ها کپی شدند."

# 5. ایجاد اسکریپت postinstall برای ایجاد symbolic link
echo "ایجاد اسکریپت postinstall..."
POSTINSTALL_SCRIPT="$SCRIPTS_DIR/postinstall"
cat <<EOF > "$POSTINSTALL_SCRIPT"
#!/bin/sh
# اسکریپت پس از نصب برای Git-CMSG (macOS)

# مسیر نصب برنامه (باید با INSTALL_LIB_DIR در اسکریپت ساخت هماهنگ باشد)
INSTALL_DIR="/usr/local/lib/git-cmsg"
# مسیر فایل اجرایی اصلی داخل پوشه نصب
EXECUTABLE="\$INSTALL_DIR/git_cmsg"
# مسیر جایی که می خواهیم symbolic link را ایجاد کنیم
LINK_PATH="/usr/local/bin/git-cmsg"

# اطمینان از اجرایی بودن فایل اصلی
chmod +x "\$EXECUTABLE"

# ایجاد symbolic link در مسیر bin
# ابتدا لینک قبلی را (اگر وجود دارد) حذف می کنیم
if [ -L "\$LINK_PATH" ]; then
  rm "\$LINK_PATH"
fi
# سپس لینک جدید را ایجاد می کنیم
ln -s "\$EXECUTABLE" "\$LINK_PATH"

exit 0
EOF

chmod +x "$POSTINSTALL_SCRIPT" # اجرایی کردن اسکریپت
echo "اسکریپت postinstall ایجاد و اجرایی شد."

# --- 6. ایجاد پوشه releases و ساخت پکیج .pkg ---
echo "ساخت پکیج .pkg و ذخیره در پوشه releases..."

# ایجاد پوشه releases اگر وجود ندارد
mkdir -p "$RELEASES_DIR"

# ${VERSION#v} برای حذف حرف 'v' از ابتدای رشته نسخه
pkgbuild --root "$PAYLOAD_DIR" \
         --scripts "$SCRIPTS_DIR" \
         --identifier com.arashzich.git-cmsg \
         --version ${VERSION#v} \
         --install-location / \
         "$RELEASES_DIR/git-cmsg-${VERSION#v}.pkg" # مسیر خروجی به داخل پوشه releases تغییر یافت

echo "پکیج .pkg ساخته شد."

# 7. پاکسازی فایل های موقت
echo "پاکسازی فایل های موقت ساخت..."
rm -rf build/
rm -rf dist/
rm -rf "$PACKAGING_DIR" # پاکسازی پوشه packaging
# غیرفعال کردن محیط مجازی اگر استفاده شد
# deactivate
echo "پاکسازی کامل شد."

echo "فرآیند ساخت پکیج macOS به پایان رسید."
echo "پکیج (.pkg) در پوشه '$RELEASES_DIR' در ریشه پروژه قرار دارد."