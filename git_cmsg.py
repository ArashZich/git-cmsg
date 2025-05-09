# git_cmsg.py

#!/usr/bin/env python3

import sys

# Define the application version
# شماره نسخه برنامه را در اینجا تعریف می کنیم
__version__ = "0.2.1"

# Import necessary modules and functions
from git_utils import check_git_installed, is_in_git_repository, get_staged_files, perform_commit
# MESSAGES برای انتخاب زبان اولیه و پاس دادن به help_handler نیاز است
from messages import get_localized_message, MESSAGES
# Import the new general argument handler function
# ایمپورت کردن تابع جدید handle_arguments از فایل help_handler.py
from help_handler import handle_arguments
from ui import get_commit_type, get_commit_subject, get_commit_scope, get_commit_body, get_commit_issues, confirm_commit

# Import prompt-toolkit specific things needed in main (for language selection)
from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator, ValidationError

# اضافه کردن import جدید برای تحلیلگر تغییرات
from change_analyzer import analyze_staged_changes

# --- Import message_formatter module ---
import message_formatter


# --- Language Validator ---
class LanguageValidator(Validator):
    def validate(self, document):
        text = document.text.strip().lower()
        if text in ['en', 'fa']:
            return  # Valid input
        else:
            raise ValidationError(
                message=get_localized_message(
                    'invalid_lang', 'en') + " / " + get_localized_message('invalid_lang', 'fa'),
                cursor_position=len(document.text))

# تابع display_help حذف شده و به help_handler.py منتقل شده است


def main():
    """تابع اصلی برای اجرای برنامه git-cmsg."""

    # --- مرحله 0: تحلیل آرگومان های خط فرمان و مدیریت راهنما و نسخه ---
    # فراخوانی تابع handle_arguments از help_handler.py
    # این تابع آرگومان های خط فرمان را بررسی می‌کند (--help, --version).
    # اگر --version یا -v داده شده باشد، نسخه را چاپ کرده و برنامه خارج می‌شود.
    # اگر --help یا -h داده شده باشد، راهنما را نمایش داده و برنامه خارج می‌شود.
    # در غیر این صورت، اجرای برنامه در اینجا ادامه پیدا می‌کند.
    # دیکشنری پیام ها (MESSAGES) و شماره نسخه (از متغیر __version__) را به تابع می فرستیم.
    handle_arguments(MESSAGES, __version__)

    # --- ادامه اجرای عادی برنامه اگر پرچم خاصی وجود نداشت ---

    # --- مرحله 1 و 2: بررسی های اولیه (گیت نصب است، در مخزن گیت هستیم) ---
    # این بخش‌ها بدون تغییر باقی می‌مانند و فقط در صورتی اجرا می‌شوند که handle_arguments برنامه را خارج نکرده باشد.
    if not check_git_installed():
        print(get_localized_message("git_not_installed", 'en'), file=sys.stderr)
        sys.exit(1)

    if not is_in_git_repository():
        sys.exit(1)

    print("گیت نصب است و شما در یک مخزن گیت قرار دارید.")

    # --- مرحله 4: انتخاب زبان (با استفاده از prompt_toolkit) ---
    # این بخش همچنان پس از بررسی پرچم راهنما و نسخه در handle_arguments اجرا می‌شود
    # و از prompt_toolkit برای ورودی تعاملی استفاده می‌کند.
    chosen_lang = 'en'  # زبان پیش‌فرض قبل از انتخاب
    while True:
        try:
            lang_input = prompt(
                f"{MESSAGES['en']['select_lang']}/{MESSAGES['fa']['select_lang']}",
                validator=LanguageValidator()
            ).strip().lower()

            if lang_input in ['en', 'fa']:
                chosen_lang = lang_input  # تنظیم زبان انتخاب شده
                break  # خروج از حلقه
        except EOFError:  # کاربر Ctrl+D را حین prompt زد
            print("\nعملیات کامیت توسط کاربر لغو شد.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:  # گرفتن خطاهای غیرمنتظره دیگر حین انتخاب زبان
            print(f"خطایی هنگام انتخاب زبان رخ داد: {e}", file=sys.stderr)
            sys.exit(1)

    print(get_localized_message("proceeding", chosen_lang, lang=chosen_lang))

    # --- مرحله 3: دریافت فایل های stage شده و نمایش آنها ---
    staged_files = get_staged_files()

    print(f"\n{get_localized_message('staged_files_header', chosen_lang)}")
    for f in staged_files:
        print(f"- {f}")
    print("-" * 30)

    # --- اضافه کردن تحلیل تغییرات و ایجاد پیشنهادات ---
    suggestions = analyze_staged_changes(staged_files)

    # --- مرحله 5: شروع prompt های تعاملی - جمع آوری تمام داده های پیام کامیت ---
    commit_type = get_commit_type(chosen_lang, suggestions.get('type', ''))
    commit_subject = get_commit_subject(
        chosen_lang, commit_type, suggestions.get('subject', ''))
    commit_scope = get_commit_scope(
        chosen_lang, commit_type, commit_subject, staged_files, suggestions.get('scope', ''))
    commit_body = get_commit_body(
        chosen_lang, commit_type, commit_subject, commit_scope)
    commit_issues = get_commit_issues(
        chosen_lang, commit_type, commit_subject, commit_scope, commit_body)

    # --- مرحله 6: فرمت کردن داده های جمع آوری شده به رشته نهایی پیام کامیت ---
    commit_data = {
        'type': commit_type,
        'subject': commit_subject,
        'scope': commit_scope,
        'body': commit_body,
        'issues': commit_issues
    }
    final_commit_message = message_formatter.format_message(
        commit_data, staged_files, chosen_lang)

    # --- مرحله 7: نمایش پیش نمایش پیام فرمت شده و درخواست تایید نهایی ---
    confirmed_message = confirm_commit(final_commit_message, chosen_lang)

    if confirmed_message is None:
        sys.exit(1)

    # --- مرحله 8: اجرای دستور git commit با پیام نهایی ---
    if perform_commit(confirmed_message):
        sys.exit(0)  # خروج موفقیت آمیز
    else:
        sys.exit(1)  # خروج با وضعیت خطا


if __name__ == "__main__":
    main()
