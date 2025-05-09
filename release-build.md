# راهنمای ساخت پکیج‌های نصبی برای Git-CMSG

این راهنما مراحل ساخت پکیج‌های نصبی Git-CMSG را برای سیستم‌عامل‌های مختلف توضیح می‌دهد. شما می‌توانید از اسکریپت‌های خودکار بیلد استفاده کنید یا مراحل را به صورت دستی انجام دهید.

## فهرست مطالب

- [پیش‌نیازها](#پیش‌نیازها)
- [ساخت پکیج با استفاده از اسکریپت‌های خودکار](#ساخت-پکیج-با-استفاده-از-اسکریپت‌های-خودکار)
- [ساخت پکیج به صورت دستی برای macOS (فایل .pkg)](#ساخت-پکیج-به-صورت-دستی-برای-macos-فایل-pkg)
- [ساخت پکیج به صورت دستی برای لینوکس دبیان/اوبونتو (فایل .deb)](#ساخت-پکیج-به-صورت-دستی-برای-لینوکس-دبیاناوبونتو-فایل-deb)
- [ساخت پکیج به صورت دستی برای لینوکس فدورا/RHEL (فایل .rpm)](#ساخت-پکیج-به-صورت-دستی-برای-لینوکس-فدوراrhel-فایل-rpm)
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
- ابزار `rsync` (معمولا به صورت پیش‌فرض در macOS موجود است)
- ابزار `pkgbuild` (نصب با ابزارهای خط فرمان Xcode)

#### لینوکس (دبیان/اوبونتو)
- ابزار `fpm` برای ساخت پکیج
- روبی و ابزارهای توسعه

#### لینوکس (فدورا/RHEL)
- ابزار `fpm` برای ساخت پکیج
- روبی و ابزارهای توسعه
- پکیج `rpm-build`

## ساخت پکیج با استفاده از اسکریپت‌های خودکار

برای راحت‌تر کردن فرآیند ساخت پکیج، می‌توانید از اسکریپت‌های خودکاری که در پوشه `build-scripts` قرار دارند استفاده کنید.

1.  مطمئن شوید که فایل‌های `build_linux.sh` و `build_macos.sh` را با محتوای ارائه شده قبلی ایجاد کرده‌اید و در پوشه `build-scripts` در ریشه پروژه قرار دارند.
2.  به فایل‌های اسکریپت دسترسی اجرایی بدهید (اگر قبلاً این کار را نکرده‌اید):
    ```bash
    chmod +x build-scripts/build_linux.sh
    chmod +x build-scripts/build_macos.sh
    ```
3.  **برای ساخت پکیج‌های لینوکس (.deb و .rpm)**، اسکریپت لینوکس را از ریشه پروژه اجرا کنید و شماره نسخه را به عنوان ورودی بدهید:
    ```bash
    ./build-scripts/build_linux.sh v0.2.0
    ```
    (به جای `v0.2.0`، شماره نسخه مورد نظر خود را وارد کنید. حرف `v` در ابتدای شماره نسخه اختیاری است.)

4.  **برای ساخت پکیج macOS (.pkg)**، اسکریپت macOS را از ریشه پروژه اجرا کنید و شماره نسخه را به عنوان ورودی بدهید:
    ```bash
    ./build-scripts/build_macos.sh v0.2.0
    ```
    (به جای `v0.2.0`، شماره نسخه مورد نظر خود را وارد کنید. حرف `v` در ابتدای شماره نسخه اختیاری است.)

اسکریپت‌ها به صورت خودکار پیش‌نیازها را بررسی کرده، وابستگی‌های پایتون را نصب می‌کنند، با PyInstaller بیلد گرفته و پکیج نهایی را در ریشه پروژه ایجاد می‌کنند.

## ساخت پکیج به صورت دستی برای macOS (فایل .pkg)

برای ساخت پکیج نصبی macOS به صورت دستی، مراحل زیر را دنبال کنید:

### ۱. ساخت پوشه اجرایی با PyInstaller (حالت Onedir)

در ریشه پروژه، دستورات زیر را اجرا کنید:

```bash
# فعال‌سازی محیط مجازی در صورت استفاده
source venv/bin/activate

# ساخت پوشه اجرایی (این یک پوشه به نام dist/git_cmsg شامل فایل اجرایی و وابستگی‌ها ایجاد می‌کند)
pyinstaller --onedir git_cmsg.py
```

### ۲. ایجاد ساختار پکیج و کپی فایل‌ها

در ریشه پروژه، ساختار پوشه‌های لازم برای بسته‌بندی را ایجاد کرده و فایل‌های تولید شده توسط PyInstaller را کپی کنید:

```bash
# تعریف مسیر پوشه بسته‌بندی
PACKAGING_DIR="packaging"
PAYLOAD_DIR="$PACKAGING_DIR/payload"
SCRIPTS_DIR="$PACKAGING_DIR/scripts"
INSTALL_LIB_DIR="$PAYLOAD_DIR/usr/local/lib/git-cmsg" # مسیر نصب برنامه در سیستم مقصد
INSTALL_BIN_DIR="$PAYLOAD_DIR/usr/local/bin" # مسیر ایجاد symbolic link در سیستم مقصد

# پاکسازی پوشه packaging قبلی (اگر وجود دارد)
rm -rf "$PACKAGING_DIR"

# ایجاد دایرکتوری های لازم در ساختار پکیج
mkdir -p "$INSTALL_LIB_DIR"
mkdir -p "$SCRIPTS_DIR"
mkdir -p "$INSTALL_BIN_DIR"

# کپی کردن کل محتوای پوشه dist/git_cmsg به پوشه مقصد در ساختار پکیج با rsync
# rsync -a بازگشتی کپی می کند و پرمیشن ها را حفظ می کند
rsync -a dist/git_cmsg/ "$INSTALL_LIB_DIR/"
```

### ۳. ایجاد اسکریپت پس از نصب (postinstall)

فایل `packaging/scripts/postinstall` را با محتوای زیر ایجاد کنید. این اسکریپت یک symbolic link در `/usr/local/bin` برای فایل اجرایی اصلی ایجاد می‌کند تا برنامه قابل اجرا از ترمینال باشد.

```bash
#!/bin/sh
# اسکریپت پس از نصب برای Git-CMSG (macOS)

# مسیر نصب برنامه (باید با مسیر کپی فایل‌ها در مرحله ۲ هماهنگ باشد)
INSTALL_DIR="/usr/local/lib/git-cmsg"
# مسیر فایل اجرایی اصلی داخل پوشه نصب
EXECUTABLE="$INSTALL_DIR/git_cmsg"
# مسیر جایی که می خواهیم symbolic link را ایجاد کنیم
LINK_PATH="/usr/local/bin/git-cmsg"

# اطمینان از اجرایی بودن فایل اصلی
chmod +x "$EXECUTABLE"

# ایجاد symbolic link در مسیر bin
# ابتدا لینک قبلی را (اگر وجود دارد) حذف می کنیم
if [ -L "$LINK_PATH" ]; then
  rm "$LINK_PATH"
fi
# سپس لینک جدید را ایجاد می کنیم
ln -s "$EXECUTABLE" "$LINK_PATH"

exit 0
```

به این اسکریپت دسترسی اجرا بدهید:
```bash
chmod +x packaging/scripts/postinstall
```

### ۴. ساخت پکیج با pkgbuild

در ریشه پروژه، دستور `pkgbuild` را برای ساخت فایل نهایی .pkg اجرا کنید:

```bash
# شماره نسخه مورد نظر خود را به جای 0.1.0 قرار دهید
pkgbuild --root "$PAYLOAD_DIR" \
         --scripts "$SCRIPTS_DIR" \
         --identifier com.arashzich.git-cmsg \
         --version 0.1.0 \
         --install-location / \
         git-cmsg-0.1.0.pkg
```

پس از اجرای این دستور، فایل `git-cmsg-0.1.0.pkg` در ریشه پروژه ساخته می‌شود که می‌توانید آن را برای نصب توزیع کنید.

## ساخت پکیج به صورت دستی برای لینوکس دبیان/اوبونتو (فایل .deb)

### ۱. نصب FPM

ابتدا FPM را نصب کنید:

```bash
# در اوبونتو/دبیان
sudo apt-get update
sudo apt-get install ruby ruby-dev build-essential
sudo gem install fpm
```

### ۲. ساخت فایل اجرایی با PyInstaller (حالت Onefile)

در ریشه پروژه، دستورات زیر را اجرا کنید:

```bash
# فعال‌سازی محیط مجازی در صورت استفاده
source venv/bin/activate

# ساخت فایل اجرایی تنها
pyinstaller --onefile git_cmsg.py
```

### ۳. ساخت پکیج .deb با FPM

در ریشه پروژه، دستور `fpm` را برای ساخت فایل .deb اجرا کنید:

```bash
# شماره نسخه مورد نظر خود را به جای 0.1.0 قرار دهید
fpm -s dir -t deb \
    -n git-cmsg \
    -v 0.1.0 \
    --description "ابزار پیام‌های کامیت گیت" \
    --maintainer "arashzich1992@gmail.com" \
    --vendor "ArashZich" \
    --license "GPL-3.0" \
    --depends "python3 (>= 3.6)" \
    --depends "git" \
    dist/git_cmsg=/usr/bin/git-cmsg
```

این دستور یک فایل `git-cmsg_0.1.0_amd64.deb` در ریشه پروژه ایجاد می‌کند که می‌توانید آن را توزیع کنید.

## ساخت پکیج به صورت دستی برای لینوکس فدورا/RHEL (فایل .rpm)

### ۱. نصب FPM و پیش‌نیازهای آن

```bash
# در فدورا
sudo dnf install ruby ruby-devel gcc make rpm-build
sudo gem install fpm
```

### ۲. ساخت فایل اجرایی با PyInstaller (حالت Onefile)

در ریشه پروژه، دستورات زیر را اجرا کنید:

```bash
# فعال‌سازی محیط مجازی در صورت استفاده
source venv/bin/activate

# ساخت فایل اجرایی تنها
pyinstaller --onefile git_cmsg.py
```

### ۳. ساخت پکیج .rpm با FPM

در ریشه پروژه، دستور `fpm` را برای ساخت فایل .rpm اجرا کنید:

```bash
# شماره نسخه مورد نظر خود را به جای 0.1.0 قرار دهید
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

این دستور یک فایل `git-cmsg-0.1.0-1.x86_64.rpm` در ریشه پروژه ایجاد می‌کند که می‌توانید آن را توزیع کنید.

## رفع مشکلات احتمالی

### مشکل: فایل اجرایی در مسیر PATH قرار نمی‌گیرد

اگر بعد از نصب، دستور `git-cmsg` در ترمینال کار نمی‌کند:

1. اطمینان حاصل کنید که فایل اجرایی (یا symbolic link آن در macOS) در مسیر صحیح (`/usr/bin` یا `/usr/local/bin`) نصب شده است.
2. پرمیشن‌های فایل را بررسی کنید و از اجرایی بودن آن مطمئن شوید:
   ```bash
   sudo chmod +x /usr/bin/git-cmsg # یا مسیر نصب واقعی
   ```
3. ترمینال را مجدداً باز کنید یا `source ~/.bashrc` (یا فایل تنظیمات شل خود) را اجرا کنید تا تغییرات اعمال شود.

### مشکل: خطا در ساخت پکیج .rpm

اگر با خطای `Need executable 'rpmbuild' to convert dir to rpm` مواجه شدید، پکیج `rpm-build` را نصب کنید:
```bash
sudo dnf install rpm-build
```

### مشکل: فایل PyInstaller برای macOS universal2 کار نمی‌کند

برای macOS، از ساخت فایل‌های universal2 خودداری کنید و به جای آن، فقط برای معماری فعلی (ARM64 یا Intel) بسازید.

---

برای هر سؤال یا مشکلی در مورد فرآیند ساخت پکیج، به صفحه مشکلات گیت‌هاب پروژه مراجعه کنید یا با آدرس arashzich1992@gmail.com تماس بگیرید.
