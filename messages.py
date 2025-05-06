# messages.py

import sys

# Dictionary containing all user-facing messages in different languages
# Add new keys and translations here as the project grows
MESSAGES = {
    "en": {
        # --- Initial Messages and Checks ---
        "select_lang": "Choose language (en/fa): ",
        "invalid_lang": "Invalid language choice. Please enter 'en' or 'fa'.",
        "proceeding": "Proceeding with commit message in {lang}.", # {lang} will be replaced by chosen language name (e.g., "en" or "fa")
        "git_not_installed": "Error: Git is not installed or not in the system's PATH.",
        "not_git_repository": "Error: Not a git repository.", # Used by git_utils
        "unexpected_git_error": "An unexpected error occurred while running Git command: {error}", # Used by git_utils
        "parsing_warning": "Warning: Could not parse line format: {line}", # Used by git_utils
        "no_staged_files": "No changes are staged. Please stage changes (`git add .`) before committing.", # Used by git_utils

        # --- Display Staged Files ---
        "staged_files_header": "Changes to be committed:",

        # --- Interactive Prompts (Used by ui.py) ---
        "prompt_type": "What is the type of change? (Type)",
        "prompt_scope": "What is the scope of this change? (Scope - Optional)",
        "prompt_subject": "Commit summary? (Subject)",
        "prompt_body": "Full description? (Body - Optional)",
        "prompt_issues": "Related Issues? (Optional)",

        # --- Type Suggestions (Descriptions used in ui.py) ---
        "type_feat": "feat (New feature)",
        "type_fix": "fix (Bug fix)",
        "type_docs": "docs (Documentation)",
        "type_style": "style (Code style)",
        "type_refactor": "refactor (Code refactor)",
        "type_test": "test (Tests)",
        "type_chore": "chore (General/Maintenance)",
        # Add other conventional types if needed

        # --- Suggestions Header ---
        "suggestions_header": "Suggestions", # Used by ui.py (e.g., for scope, issues)
        # --- New message for suggestion based on analysis ---
        "suggestion": "Suggestion",

        # --- Guideline Hints (Used by ui.py) ---
        "hint_subject": "Guideline: Start with imperative verb, max 50-72 chars.",
        # UPDATED HINT for multi-line Body finalization
        "hint_body": "Guideline: Explain *why* the change, important technical details, contrast with previous behavior.\n(Press Alt+Enter or Esc then Enter to finish)",
        "hint_issues": "Guideline: Example: Closes #123, Fixes #456",
        "hint_skip": "(Leave empty and press Enter to skip)", # Used for optional fields

        # --- Validator Messages (Used by ui.py validators) ---
        "invalid_type_choice": "Invalid choice. Please enter a number between {valid_range}.", # {valid_range} will be replaced by actual range
        "invalid_type_choice_number": "Invalid input. Please enter a number.",
        # "invalid_lang" is also used by the LanguageValidator in git_cmsg.py

        # --- Helper Text (Could be used by ui.py for '?' shortcut if re-added) ---
        "helper_text": "Helper:\n  Press Enter to skip optional fields.\n  Language is chosen at the start.\n  (Press Enter to resume)", # Basic helper info

        # --- Confirmation (Used by ui.py confirm_commit) ---
        "preview_header": "Commit message preview:",
        "confirm_prompt": "Confirm? (y/n/e - edit): ", # y=yes, n=no, e=edit
        "commit_aborted": "Commit aborted.",
        "commit_executed": "Commit successful!", # This might be printed by main or ui after git_utils confirms success

        # --- General Error Messages (Could be used by ui.py or main, some used by git_utils) ---
        "git_command_error": "Error running Git command: {error}", # Generic git command error
        "unexpected_error": "An unexpected error occurred: {error}", # Catch-all for unhandled exceptions

        # --- Messages for Commit Formatting (Used by message_formatter.py) ---
        "file_list_header": "Files changed", # Header for the list of files in the body


        # --- ADDED Explanation Messages ---
        "explanation_header_en": "Explanation (English):",
        "explanation_header_fa": "توضیح (فارسی):",
        
        # --- Full explanation messages (original) ---
        "scope_explanation_en": """Scope defines the PART of the codebase affected by this change.
It adds context to the commit message header.
Examples: 'auth', 'UI', 'api', 'components/button', 'docs'""",
        "scope_explanation_fa": """محدوده، بخشِ کد شما را مشخص می‌کند که این تغییر روی آن تاثیر گذاشته است.
این بخش به خوانایی سربرگ پیام کامیت کمک می‌کند.
مثال‌ها: 'ورود', 'رابط کاربری', 'API', 'کامپوننت‌ها/دکمه', 'مستندات'""",
        "issues_explanation_en": """Use this section to link to issue tracker entries or add other footer information.
Common formats: 'Closes #123', 'Fixes #456', 'Ref #789'.
You can also add lines like 'Co-authored-by: Name <email>' here.""",
        "issues_explanation_fa": """از این بخش برای لینک دادن به تیکت‌ها یا مسائل مرتبط در Issue Tracker یا اضافه کردن اطلاعات دیگر به پاورقی پیام استفاده کنید.
فرمت‌های رایج: 'Closes #123', 'Fixes #456', 'Ref #789'.
همچنین می‌توانید خطوطی مانند 'Co-authored-by: Name <email>' در اینجا اضافه کنید.""",
        
        # --- Short explanation messages (new) ---
        "scope_explanation_short_en": "Scope: Part of codebase affected (e.g., 'auth', 'ui')",
        "issues_explanation_short_en": "Link issues with formats like 'Closes #123' or 'Fixes #456'",
    },
    "fa": {
        # --- Initial Messages and Checks ---
        "select_lang": "زبان مورد نظر را انتخاب کنید (fa/en): ",
        "invalid_lang": "انتخاب زبان نامعتبر است. لطفا 'fa' یا 'en' را وارد کنید.",
        "proceeding": "ادامه فرایند کامیت با زبان {lang}.", # {lang} با نام زبان جایگزین می‌شود
        "git_not_installed": "خطا: گیت نصب نیست یا در PATH سیستم پیدا نشد.",
        "not_git_repository": "خطا: در یک مخزن گیت قرار ندارید.",
        "unexpected_git_error": "خطای غیرمنتظره هنگام اجرای دستور گیت: {error}",
        "parsing_warning": "هشدار: خط مورد نظر قابل پردازش نبود: {line}",
        "no_staged_files": "هیچ تغییری برای کامیت آماده نیست. لطفا با (`git add .`) تغییرات را آماده کنید.",

        # --- Display Staged Files ---
        "staged_files_header": "تغییرات آماده کامیت:",

        # --- Interactive Prompts (Used by ui.py) ---
        "prompt_type": "نوع تغییر چیست؟ (Type)",
        "prompt_scope": "محدوده تغییر چیست؟ (Scope - اختیاری)",
        "prompt_subject": "خلاصه کامیت؟ (Subject)",
        "prompt_body": "توضیحات کامل؟ (Body - اختیاری)",
        "prompt_issues": "Issues مرتبط؟ (اختیاری)",

        # --- Type Suggestions (Descriptions used in ui.py) ---
        "type_feat": "feat (قابلیت جدید)",
        "type_fix": "fix (رفع اشکال)",
        "type_docs": "docs (مستندات)",
        "type_style": "style (استایل کد)",
        "type_refactor": "refactor (بازآرایی کد)",
        "type_test": "test (تست ها)",
        "type_chore": "chore (عمومی/نگهداری)",
        # Add other conventional types if needed

         # --- Suggestions Header ---
        "suggestions_header": "پیشنهادات", # Used by ui.py (e.g., for scope, issues)
        # --- New message for suggestion based on analysis ---
        "suggestion": "پیشنهاد",

        # --- Guideline Hints (Used by ui.py) ---
        "hint_subject": "راهنما: با فعل امری شروع شود، حداکثر ۵۰-۷۲ حرف.",
        # پیام راهنمای به روز شده
        "hint_body": "راهنما: چرایی تغییر، جزئیات مهم فنی، تفاوت با رفتار قبلی.\n(برای پایان، Alt+Enter یا Esc سپس Enter بزنید)",
        "hint_issues": "راهنما: مثال: Closes #123, Fixes #456",
        "hint_skip": "(برای رد شدن، خالی بگذارید و Enter بزنید)",

        # --- Validator Messages (Used by ui.py validators) ---
        "invalid_type_choice": "انتخاب نامعتبر. لطفا عددی بین {valid_range} وارد کنید.",
        "invalid_type_choice_number": "ورودی نامعتبر. لطفا یک عدد وارد کنید.",
        # "invalid_lang" is also used by the LanguageValidator in git_cmsg.py

        # --- Helper Text (Could be used by ui.py for '?' shortcut if re-added) ---
        "helper_text": "راهنما:\n  برای رد شدن از فیلدهای اختیاری Enter بزنید.\n  زبان در ابتدای برنامه انتخاب می‌شود.\n  (برای ادامه Enter بزنید)", # راهنمای پایه

        # --- Confirmation (Used by ui.py confirm_commit) ---
        "preview_header": "پیش‌نمایش کامیت مسیج:",
        "confirm_prompt": "تایید می‌کنید؟ (y=بله, n=خیر, e=ویرایش دستی): ",
        "commit_aborted": "عملیات کامیت لغو شد.",
        "commit_executed": "کامیت با موفقیت انجام شد!", # این پیام می‌تواند توسط main یا ui بعد از موفقیت git_utils نمایش داده شود

        # --- General Error Messages (Could be used by ui.py or main, some used by git_utils) ---
        "git_command_error": "خطا در اجرای دستور گیت: {error}",
        "unexpected_error": "خطای غیرمنتظره رخ داد: {error}",

         # --- Messages for Commit Formatting (Used by message_formatter.py) ---
        "file_list_header": "فایل‌های تغییر یافته", # Header for the list of files in the body


        # --- ADDED Explanation Messages ---
        "explanation_header_en": "Explanation (English):",
        "explanation_header_fa": "توضیح (فارسی):",
        
        # --- Full explanation messages (original) ---
        "scope_explanation_en": """Scope defines the PART of the codebase affected by this change.
It adds context to the commit message header.
Examples: 'auth', 'UI', 'api', 'components/button', 'docs'""",
        "scope_explanation_fa": """محدوده، بخشِ کد شما را مشخص می‌کند که این تغییر روی آن تاثیر گذاشته است.
این بخش به خوانایی سربرگ پیام کامیت کمک می‌کند.
مثال‌ها: 'ورود', 'رابط کاربری', 'API', 'کامپوننت‌ها/دکمه', 'مستندات'""",
        "issues_explanation_en": """Use this section to link to issue tracker entries or add other footer information.
Common formats: 'Closes #123', 'Fixes #456', 'Ref #789'.
You can also add lines like 'Co-authored-by: Name <email>' here.""",
        "issues_explanation_fa": """از این بخش برای لینک دادن به تیکت‌ها یا مسائل مرتبط در Issue Tracker یا اضافه کردن اطلاعات دیگر به پاورقی پیام استفاده کنید.
فرمت‌های رایج: 'Closes #123', 'Fixes #456', 'Ref #789'.
همچنین می‌توانید خطوطی مانند 'Co-authored-by: Name <email>' در اینجا اضافه کنید.""",
        
        # --- Short explanation messages (new) ---
        "scope_explanation_short_fa": "محدوده: بخشی از کد که تغییر کرده (مثال: 'ورود'، 'رابط کاربری')",
        "issues_explanation_short_fa": "برای لینک به تیکت‌ها از فرمت‌هایی مانند 'Closes #123' استفاده کنید",
    }
}


# --- Function to get localized message ---
def get_localized_message(key, language_code, **kwargs):
    """Gets a message string based on key and language code.
       kwargs are used for formatting the message string itself (e.g., {lang}).
       Falls back to English if the language_code or key is not found.
    """
    # Fallback logic: Try specified language, then English, then show untranslated key warning
    lang_messages = MESSAGES.get(language_code)
    if lang_messages is None:
        # If language code is invalid or not found, use English
        lang_messages = MESSAGES['en']

    message = lang_messages.get(key)
    if message is None:
        # If key is not found in the chosen language, try English
        message = MESSAGES['en'].get(key)
        if message is None:
            # If key not found even in English, show a warning and use a placeholder
            print(f"Warning: Message key '{key}' not found in any language.", file=sys.stderr)
            return f"Missing key: {key}" # Return a placeholder string

    try:
        # Format the message with provided keyword arguments
        # Note: The keyword argument passed (e.g., lang='en') matches placeholders like {lang} in the message string
        return message.format(**kwargs)
    except KeyError as e:
        # Warning if formatting expected a key that wasn't provided in kwargs
        print(f"Warning: Missing format key {e} in message '{message}' for language '{language_code}'.", file=sys.stderr)
        return message # Return message without formatting if keys are missing