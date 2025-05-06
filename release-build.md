# راهنمای ساخت پکیج‌های نصبی برای Git-CMSG

این راهنما مراحل ساخت پکیج‌های نصبی Git-CMSG را برای سیستم‌عامل‌های مختلف توضیح می‌دهد.

## فهرست مطالب

- [پیش‌نیازها](#پیش‌نیازها)
- [ساخت پکیج برای macOS (فایل .pkg)](#ساخت-پکیج-برای-macos-فایل-pkg)
- [ساخت پکیج برای لینوکس دبیان/اوبونتو (فایل .deb)](#ساخت-پکیج-برای-لینوکس-دبیاناوبونتو-فایل-deb)
- [ساخت پکیج برای لینوکس فدورا/RHEL (فایل .rpm)](#ساخت-پکیج-برای-لینوکس-فدوراrhel-فایل-rpm)
- [رفع مشکلات احتمالی](#رفع-مشکلات-احتمالی)

## پیش‌نیازها

قبل از شروع، از وجود موارد زیر اطمینان حاصل کنید:

### پیش‌نیازهای عمومی
- پایتون ۳.۶ یا بالاتر
- PyInstaller (نصب با دستور `pip install pyinstaller`)
- مخزن گیت با تمام فایل‌های پروژه

### پیش‌نیازهای مخصوص هر سیستم‌عامل

#### macOS
- سیستم‌عامل macOS
- ابزارهای خط فرمان (`xcode-select --install`)

#### لینوکس (دبیان/اوبونتو)
- ابزار `fpm` برای ساخت پکیج
- روبی و ابزارهای توسعه

#### لینوکس (فدورا/RHEL)
- ابزار `fpm` برای ساخت پکیج
- روبی و ابزارهای توسعه
- پکیج `rpm-build`

## ساخت پکیج برای macOS (فایل .pkg)

برای ساخت پکیج نصبی macOS، مراحل زیر را دنبال کنید:

### ۱. ساخت فایل اجرایی با PyInstaller

```bash
# فعال‌سازی محیط مجازی در صورت استفاده
source venv/bin/activate

# ساخت فایل اجرایی
pyinstaller --onefile git_cmsg.py
```

### ۲. ایجاد ساختار پکیج

```bash
# ایجاد ساختار پوشه‌ها برای پکیج
mkdir -p packaging/payload/usr/local/bin
mkdir -p packaging/scripts

# کپی فایل اجرایی به مکان مناسب
cp dist/git_cmsg packaging/payload/usr/local/bin/git-cmsg
chmod +x packaging/payload/usr/local/bin/git-cmsg
```

### ۳. ایجاد اسکریپت پس از نصب

فایل `packaging/scripts/postinstall` را با محتوای زیر ایجاد کنید:

```bash
#!/bin/sh
# اسکریپت پس از نصب

# اطمینان از اجرایی بودن فایل
chmod +x /usr/local/bin/git-cmsg

exit 0
```

به این اسکریپت دسترسی اجرا بدهید:
```bash
chmod +x packaging/scripts/postinstall
```

### ۴. ساخت پکیج با pkgbuild

```bash
pkgbuild --root packaging/payload \
         --scripts packaging/scripts \
         --identifier com.arashzich.git-cmsg \
         --version 0.1.0 \
         --install-location / \
         git-cmsg-0.1.0.pkg
```

پس از اجرای این دستور، فایل `git-cmsg-0.1.0.pkg` ساخته می‌شود که می‌توانید آن را برای نصب توزیع کنید.

## ساخت پکیج برای لینوکس دبیان/اوبونتو (فایل .deb)

### ۱. نصب FPM

ابتدا FPM را نصب کنید:

```bash
# در اوبونتو/دبیان
sudo apt-get update
sudo apt-get install ruby ruby-dev build-essential
sudo gem install fpm
```

### ۲. ساخت فایل اجرایی با PyInstaller

```bash
# فعال‌سازی محیط مجازی در صورت استفاده
source venv/bin/activate

# ساخت فایل اجرایی
pyinstaller --onefile git_cmsg.py
```

### ۳. ساخت پکیج .deb با FPM

```bash
fpm -s dir -t deb \
    -n git-cmsg \
    -v 0.1.0 \
    --description "ابزار پیام‌های کامیت گیت" \
    --maintainer "arashzich1992@gmail.com" \
    --vendor "ArashZich" \
    --license "GPL-3.0" \
    --depends "python3 >= 3.6" \
    --depends "git" \
    dist/git_cmsg=/usr/bin/git-cmsg
```

این دستور یک فایل `git-cmsg_0.1.0_amd64.deb` ایجاد می‌کند که می‌توانید آن را توزیع کنید.

## ساخت پکیج برای لینوکس فدورا/RHEL (فایل .rpm)

### ۱. نصب FPM و پیش‌نیازهای آن

```bash
# در فدورا
sudo dnf install ruby ruby-devel gcc make rpm-build
sudo gem install fpm
```

### ۲. ساخت فایل اجرایی با PyInstaller

```bash
# فعال‌سازی محیط مجازی در صورت استفاده
source venv/bin/activate

# ساخت فایل اجرایی
pyinstaller --onefile git_cmsg.py
```

### ۳. ساخت پکیج .rpm با FPM

```bash
fpm -s dir -t rpm \
    -n git-cmsg \
    -v 0.1.0 \
    --description "ابزار پیام‌های کامیت گیت" \
    --maintainer "arashzich1992@gmail.com" \
    --vendor "ArashZich" \
    --license "GPL-3.0" \
    --depends "python3 >= 3.6" \
    --depends "git" \
    dist/git_cmsg=/usr/bin/git-cmsg
```

این دستور یک فایل `git-cmsg-0.1.0-1.x86_64.rpm` ایجاد می‌کند که می‌توانید آن را توزیع کنید.

## رفع مشکلات احتمالی

### مشکل: فایل اجرایی در مسیر PATH قرار نمی‌گیرد

اگر بعد از نصب، دستور `git-cmsg` در ترمینال کار نمی‌کند:

1. اطمینان حاصل کنید که فایل اجرایی در مسیر صحیح (`/usr/bin` یا `/usr/local/bin`) نصب شده است
2. پرمیشن‌های فایل را بررسی کنید و از اجرایی بودن آن مطمئن شوید:
   ```bash
   sudo chmod +x /usr/bin/git-cmsg
   ```
3. ترمینال را مجدداً باز کنید تا تغییرات اعمال شود

### مشکل: خطا در ساخت پکیج .rpm

اگر با خطای `Need executable 'rpmbuild' to convert dir to rpm` مواجه شدید:
```bash
sudo dnf install rpm-build
```

### مشکل: فایل PyInstaller برای macOS universal2 کار نمی‌کند

برای macOS، از ساخت فایل‌های universal2 خودداری کنید و به جای آن، فقط برای معماری فعلی (ARM64 یا Intel) بسازید.

---

برای هر سؤال یا مشکلی در مورد فرآیند ساخت پکیج، به صفحه مشکلات گیت‌هاب پروژه مراجعه کنید یا با آدرس arashzich1992@gmail.com تماس بگیرید.