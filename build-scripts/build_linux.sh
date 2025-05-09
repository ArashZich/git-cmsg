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

# 4. ساخت پکیج .deb با FPM
echo "ساخت پکیج .deb..."
# ${VERSION#v} برای حذف حرف 'v' از ابتدای رشته نسخه (مثال: v0.2.0 به 0.2.0)
fpm -s dir -t deb \
    -n git-cmsg \
    -v ${VERSION#v} \
    --description "ابزار پیام‌های کامیت گیت" \
    --maintainer "arashzich1992@gmail.com" \
    --vendor "ArashZich" \
    --license "GPL-3.0" \
    --depends "python3 (>= 3.6)" \
    --depends "git" \
    dist/git_cmsg=/usr/bin/git-cmsg

echo "پکیج .deb ساخته شد."

# 5. ساخت پکیج .rpm با FPM
echo "ساخت پکیج .rpm..."
fpm -s dir -t rpm \
    -n git-cmsg \
    -v ${VERSION#v} \
    --description "ابزار پیام‌های کامیت گیت" \
    --maintainer "arashzich1992@gmail.com" \
    --vendor "ArashZich" \
    --license "GPL-3.0" \
    --depends "python3 >= 3.6" \
    --depends "git" \
    dist/git_cmsg=/usr/bin/git-cmsg

echo "پکیج .rpm ساخته شد."

# 6. پاکسازی فایل های موقت
echo "پاکسازی فایل های موقت ساخت..."
rm -rf build/
rm -rf dist/
# غیرفعال کردن محیط مجازی اگر استفاده شد
# deactivate
echo "پاکسازی کامل شد."

echo "فرآیند ساخت پکیج های لینوکس به پایان رسید."
echo "پکیج ها (.deb, .rpm) در دایرکتوری فعلی قرار دارند."