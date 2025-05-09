# help_handler.py

import sys
import argparse

# Import necessary components from other modules
from messages import get_localized_message, MESSAGES

# بررسی نسخه پایتون برای مدیریت سازنده ArgumentParser
python_version = sys.version_info
is_python_3_8_or_later = python_version >= (3, 8)


def display_help(language_code):
    """پیام راهنمای محلی‌سازی شده را نمایش می‌دهد."""
    help_message = get_localized_message("help_message", language_code)
    print(help_message)


def handle_arguments(messages, app_version):
    """
    آرگومان های خط فرمان (--help, --version) را تحلیل می‌کند.
    مدیریت نمایش راهنما یا نسخه و خروج از برنامه را انجام می‌دهد.
    سازگار با نسخه های مختلف پایتون.

    Args:
        messages (dict): دیکشنری حاوی تمام پیام های محلی شده برنامه (MESSAGES).
        app_version (str): رشته حاوی شماره نسخه برنامه (مثال: "0.2.0").
    """
    # دریافت رشته قالب‌بندی شده نسخه (با استفاده از زبان انگلیسی برای parser)
    # از پیام محلی شده با placeholder کلیدواژه‌ای استفاده می‌کنیم و شماره نسخه را پاس می‌دهیم.
    version_string_for_parser = get_localized_message(
        "version_format", "en", version_num=app_version)

    # ایجاد parser بدون استفاده از پارامتر 'version' که در نسخه‌های جدید پایتون پشتیبانی نمی‌شود
    parser = argparse.ArgumentParser(
        description=get_localized_message("app_description", "en"),
        add_help=False  # مدیریت دستی نمایش راهنما
    )

    # اضافه کردن آرگومان -v یا --version با action='version'
    parser.add_argument(
        '-v', '--version',
        action='version',  # استفاده از action='version' برای مدیریت خودکار چاپ نسخه و خروج
        # ارائه رشته نسخه (قالب‌بندی شده) به action='version'
        version=version_string_for_parser,
        # اضافه کردن توضیحات راهنما برای این پرچم
        help=get_localized_message("help_argument_description", "en")
    )

    # اضافه کردن آرگومان -h یا --help (این بخش همیشه یکسان است چون نمایش راهنمای آن را خودمان مدیریت می کنیم)
    parser.add_argument(
        '-h', '--help',
        action='store_true',  # فقط True را ذخیره کن اگر پرچم وجود داشت
        # توضیحات راهنما برای این پرچم
        help=get_localized_message("help_argument_description", "en")
    )

    # تحلیل آرگومان ها
    # parse_args() پرچم نسخه را مدیریت کرده و اگر وجود داشته باشد، نسخه را چاپ و خارج می شود.
    # اگر پرچم راهنما (-h یا --help) وجود داشته باشد، parse_args برمی‌گردد و args.help برابر True خواهد بود.
    # اگر هیچ آرگومان شناخته شده‌ای نباشد، parse_args برمی‌گردد و args.help برابر False خواهد بود.
    args = parser.parse_args()

    # اگر پرچم راهنما درخواست شده باشد (و پرچم نسخه باعث خروج نشده باشد)
    if args.help:
        # ابتدا زبان نمایش راهنما را از کاربر بپرس (با ورودی استاندارد)
        chosen_lang = 'en'  # زبان پیش‌فرض
        print(
            f"{messages['en']['select_lang']}/{messages['fa']['select_lang']}", file=sys.stderr)
        while True:
            try:
                lang_input = input().strip().lower()
                if lang_input in ['en', 'fa']:
                    chosen_lang = lang_input
                    break
                else:
                    print(
                        f"{messages['en']['invalid_lang']} / {messages['fa']['invalid_lang']}", file=sys.stderr)
                    print(
                        f"{messages['en']['select_lang']}/{messages['fa']['select_lang']}", file=sys.stderr)
            except EOFError:
                print("\nعملیات توسط کاربر لغو شد.", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"خطایی هنگام انتخاب زبان رخ داد: {e}", file=sys.stderr)
                sys.exit(1)

        # نمایش پیام راهنما به زبان انتخاب شده
        display_help(chosen_lang)
        sys.exit(0)  # خروج موفق

    # اگر نه راهنما و نه نسخه درخواست شده باشد، تابع برمی‌گردد و اجرای عادی ادامه پیدا می کند.
    return

# توجه: بلوک if __name__ == "__main__": در این فایل وجود ندارد.
