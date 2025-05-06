# ui.py

# Import necessary libraries
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator, ValidationError
import sys
import os
import re # Import regular expressions for parsing branch name

# Import messages for localization
from messages import get_localized_message, MESSAGES

# Import git utilities to get branch name (used in get_commit_issues)
from git_utils import get_current_branch_name

# Import libraries for editing if confirm_commit allows editing
import tempfile # For creating a temporary file
import subprocess # For opening an external editor

# --- Validator for Commit Type ---
class TypeValidator(Validator):
    def validate(self, document):
        text = document.text
        try:
            type_index = int(text)
            # Ensure this list matches the order and keys in messages.py
            ordered_type_keys = [
                'type_feat', 'type_fix', 'type_chore', 'type_refactor',
                'type_docs', 'type_style', 'type_test'
            ]
            if 1 <= type_index <= len(ordered_type_keys):
                return # Input is a valid number for a type
            else:
                # If number is out of range, raise validation error with message
                raise ValidationError(
                    message=get_localized_message("invalid_type_choice", 'en', # Use a fallback language for validator messages
                                                valid_range=f"1-{len(ordered_type_keys)}"),
                    cursor_position=len(text)) # Keep cursor at the end

        except ValueError:
            # If input is not a number, raise validation error
            raise ValidationError(
                message=get_localized_message("invalid_type_choice_number", 'en'), # Use a fallback language
                cursor_position=len(text))


# --- Function to get Commit Type ---
def get_commit_type(language_code, suggested_type=""):
    """Prompts user for commit type and returns the selected type string."""

    # Ensure this list matches the order and keys in messages.py and TypeValidator
    ordered_type_keys = [
        'type_feat', 'type_fix', 'type_chore', 'type_refactor',
        'type_docs', 'type_style', 'type_test'
    ]
    # Map the message key to the actual conventional commit string
    type_key_to_string = {
        'type_feat': 'feat', 'type_fix': 'fix', 'type_chore': 'chore',
        'type_refactor': 'refactor', 'type_docs': 'docs',
        'type_style': 'style', 'type_test': 'test'
    }
    # معکوس نگاشت بالا برای پیدا کردن کلید از نوع کامیت
    type_string_to_key = {v: k for k, v in type_key_to_string.items()}

    # Build the prompt message with numbered options
    prompt_message = f"{get_localized_message('prompt_type', language_code)}\n"
    
    # اضافه کردن پیشنهاد به پیام، اگر وجود داشته باشد - بدون شماره
    if suggested_type and suggested_type in type_string_to_key:
        suggested_key = type_string_to_key[suggested_type]
        suggested_desc = get_localized_message(suggested_key, language_code)
        
        suggestion_message = get_localized_message('suggestion', language_code)
        prompt_message += f"{suggestion_message}: {suggested_desc}\n"
    
    # ادامه با نمایش گزینه‌ها
    for i, key in enumerate(ordered_type_keys):
        # Get localized description for each type
        localized_type_desc = get_localized_message(key, language_code)
        prompt_message += f"{i + 1}. {localized_type_desc}\n" # Add numbered option

    prompt_message += "> " # Add input indicator

    # Loop until valid input is received
    while True:
        try:
            # Use prompt from prompt_toolkit
            user_input = prompt(
                prompt_message # The question with options
            ).strip()

            # Convert valid input (which passed validation) to the actual type string
            type_index = int(user_input)
            selected_key = ordered_type_keys[type_index - 1] # Get key from 0-based index
            return type_key_to_string[selected_key] # Return the standard type string (e.g., 'feat')

        except (ValueError, IndexError, ValidationError):
             # Validator prints the error message, so just continue the loop if validation failed
             pass


# --- Function to get Commit Subject ---
def get_commit_subject(language_code, commit_type, suggested_subject=""):
    """Prompts user for commit subject."""

    # Build the prompt message
    prompt_message = f"Type: {commit_type}\n"
    prompt_message += f"{get_localized_message('prompt_subject', language_code)}\n"
    
    # اضافه کردن پیشنهاد به پیام، اگر وجود داشته باشد
    if suggested_subject:
        suggestion_message = get_localized_message('suggestion', language_code)
        prompt_message += f"{suggestion_message}: {suggested_subject}\n"
    
    # اضافه کردن راهنمای موضوع
    prompt_message += f"{get_localized_message('hint_subject', language_code)}\n"
    prompt_message += "> " # Input indicator

    # Get user input using prompt_toolkit
    user_input = prompt(prompt_message).strip()

    return user_input


# --- Function to generate Scope Suggestions ---
def generate_scope_suggestions(staged_files):
    """Generates potential scope suggestions based on staged file paths."""
    suggestions = set() # Use a set to store unique suggestions

    for filepath in staged_files:
        # Split path into components
        path_parts = os.path.normpath(os.path.dirname(filepath)).split(os.sep)

        # Add parent directories and cumulative paths as suggestions
        current_scope_parts = []
        for part in path_parts:
            if part and part != '.': # Ignore empty parts and current directory '.'
                current_scope_parts.append(part)
                # Add the cumulative path as a suggestion (e.g., ['src', 'components'] -> 'src/components')
                suggestions.add('/'.join(current_scope_parts)) # Use '/' as standard scope separator

    # Convert set to sorted list and limit the number of suggestions
    sorted_suggestions = sorted(list(suggestions))
    # Limit to a reasonable number, e.g., first 5 (کاهش تعداد پیشنهادها)
    return sorted_suggestions[:5]


# --- Function to get Commit Scope (with more guidance) ---
def get_commit_scope(language_code, commit_type, commit_subject, staged_files, suggested_scope=""):
    """Prompts user for commit scope, providing suggestions based on staged files."""

    # Generate suggestions based on staged files
    suggestions = generate_scope_suggestions(staged_files)

    # --- Build the prompt message with improved structure ---
    prompt_message = f"Type: {commit_type}\n"
    prompt_message += f"Subject: {commit_subject}\n"
    prompt_message += f"{get_localized_message('prompt_scope', language_code)}\n"
    
    # اضافه کردن پیشنهاد به پیام، اگر وجود داشته باشد
    if suggested_scope:
        suggestion_message = get_localized_message('suggestion', language_code)
        prompt_message += f"{suggestion_message}: {suggested_scope}\n"

    # --- توضیحات کوتاه‌تر و مختصرتر (فقط به زبان کاربر) ---
    if language_code == 'fa':
        prompt_message += f"{get_localized_message('scope_explanation_short_fa', language_code)}\n"
    else:
        prompt_message += f"{get_localized_message('scope_explanation_short_en', language_code)}\n"

    # Add suggestions if any
    if suggestions:
        suggestions_header = get_localized_message('suggestions_header', language_code)
        # Format suggestions as a comma-separated list
        prompt_message += f"{suggestions_header}: {', '.join(suggestions)}\n"

    # Add the optional/skip guideline
    prompt_message += f"{get_localized_message('hint_skip', language_code)}\n"
    prompt_message += "> " # Input indicator

    # Get user input using prompt_toolkit
    user_input = prompt(prompt_message).strip()

    return user_input


# --- Function to get Commit Body (Full Description) ---
def get_commit_body(language_code, commit_type, commit_subject, commit_scope):
    """Prompts user for commit body (multi-line input)."""

    # Build the prompt message
    prompt_message = f"Type: {commit_type}\n"
    prompt_message += f"Subject: {commit_subject}\n"
    prompt_message += f"Scope: {commit_scope if commit_scope else '(skipped)'}\n"
    prompt_message += f"{get_localized_message('prompt_body', language_code)}\n"
    prompt_message += f"{get_localized_message('hint_body', language_code)}\n"
    prompt_message += "> " # Input indicator

    # Use prompt_toolkit.prompt with multiline=True for multi-line input
    user_input = prompt(prompt_message, multiline=True).strip()

    return user_input


# --- Function to generate Issue Suggestions from branch name ---
def generate_issue_suggestions_from_branch(branch_name):
    """Generates potential issue number suggestions from a branch name."""
    suggestions = set() # Use a set for unique suggestions

    # Return empty list if no branch name or detached HEAD
    if not branch_name or branch_name == 'HEAD':
        return []

    # Common patterns in branch names for issue numbers
    issue_number_pattern = re.compile(r'[^0-9](\d+)([^0-9]|$)|(^(\d+))')

    # Find all potential issue numbers in the branch name
    found_matches = issue_number_pattern.findall(branch_name)
    numbers = []
    for match in found_matches:
        # In the regex, the number is either in group 1 or group 4
        if match[0] and match[1]: # If first part of regex matched (e.g., non-digit followed by digits)
             numbers.append(match[1]) # The number is in group 1
        elif match[3]: # If second part of regex matched (start of string followed by digits)
             numbers.append(match[3]) # The number is in group 4

    # Format as #issue_number
    for num_str in numbers:
        suggestions.add(f"#{num_str}") # Suggest format like #123

    # Convert set to sorted list
    sorted_suggestions = sorted(list(suggestions))
    # Limit to a reasonable number, e.g., first 3 (کاهش تعداد پیشنهادها)
    return sorted_suggestions[:3]


# --- Function to get Commit Issues (with more guidance) ---
def get_commit_issues(language_code, commit_type, commit_subject, commit_scope, commit_body):
    """Prompts user for related issues, providing suggestions from the branch name."""

    # Get current branch name using the git_utils function
    branch_name = get_current_branch_name()

    # Generate issue suggestions based on branch name
    suggestions = generate_issue_suggestions_from_branch(branch_name)

    # --- Build the prompt message with improved structure ---
    prompt_message = f"Type: {commit_type}\n"
    prompt_message += f"Subject: {commit_subject}\n"
    prompt_message += f"Scope: {commit_scope if commit_scope else '(skipped)'}\n"
    prompt_message += f"Body: {'(skipped)' if not commit_body.strip() else '...'}\n"
    prompt_message += f"{get_localized_message('prompt_issues', language_code)}\n"

    # --- توضیحات کوتاه‌تر و مختصرتر (فقط به زبان کاربر) ---
    if language_code == 'fa':
        prompt_message += f"{get_localized_message('issues_explanation_short_fa', language_code)}\n"
    else:
        prompt_message += f"{get_localized_message('issues_explanation_short_en', language_code)}\n"

    # Add suggestions if any
    if suggestions:
        suggestions_header = get_localized_message('suggestions_header', language_code)
        prompt_message += f"{suggestions_header}: {', '.join(suggestions)}\n"

    # Add the optional/skip guideline and example format
    prompt_message += f"{get_localized_message('hint_skip', language_code)}\n"
    prompt_message += f"{get_localized_message('hint_issues', language_code)}\n"
    prompt_message += "> " # Input indicator

    # Get user input using prompt_toolkit
    user_input = prompt(prompt_message).strip()

    return user_input


# --- Function to display final preview and confirm ---
def confirm_commit(commit_message_string, language_code):
    """
    Displays the final commit message preview and asks for user confirmation.
    Allows editing the message externally.
    """
    while True: # Loop until user confirms, aborts, or edits successfully
        # Display the formatted message preview
        preview_header = get_localized_message('preview_header', language_code)
        confirm_prompt_text = get_localized_message('confirm_prompt', language_code)

        # Use print for the multi-line message preview
        print(f"\n{preview_header}\n{'-' * 30}") # Header and separator
        print(commit_message_string) # The actual message
        print(f"{'-' * 30}\n") # Separator

        # Get user input for confirmation
        try:
            user_choice = prompt(
                f"{confirm_prompt_text} "
            ).strip().lower()

            if user_choice == 'y':
                return commit_message_string # User confirms, return the current message

            elif user_choice == 'n':
                print(get_localized_message('commit_aborted', language_code), file=sys.stderr)
                return None # User aborts

            elif user_choice == 'e':
                # User wants to edit externally
                edited_message = edit_message_externally(commit_message_string)
                if edited_message is not None:
                     # If editing was successful, update the message and loop to show preview again
                     commit_message_string = edited_message
                else:
                     # If editing failed or was cancelled in editor, prompt again
                     print("Editing cancelled or failed. Please try again or choose y/n.", file=sys.stderr)

            else:
                # Invalid input, prompt again
                print("Invalid choice. Please enter 'y', 'n', or 'e'.", file=sys.stderr)

        except EOFError: # User pressed Ctrl+D
            print("\nCommit process aborted by user.", file=sys.stderr)
            return None # User aborts

        except Exception as e: # Catch other unexpected errors during confirmation
            print(f"An error occurred during confirmation: {e}", file=sys.stderr)
            return None # Abort on error

# --- Helper function to open external editor ---
def edit_message_externally(initial_message):
    """
    Opens an external editor for the user to edit the commit message.
    Uses the GIT_EDITOR environment variable or a common default.
    """
    # Get the editor command from environment variables, fallback to common defaults
    editor = os.environ.get('GIT_EDITOR') or \
             os.environ.get('VISUAL') or \
             os.environ.get('EDITOR') or \
             'nano' # Default to nano if no editor is set

    # Create a temporary file to write the message to
    with tempfile.NamedTemporaryFile(mode='w+', suffix=".gitmessage", delete=False, encoding='utf-8') as tmp_file:
        tmp_file_path = tmp_file.name
        tmp_file.write(initial_message)
        tmp_file.flush() # Ensure all data is written to disk before opening editor

    try:
        # Open the editor with the temporary file
        subprocess.run(f'{editor} "{tmp_file_path}"', shell=True, check=True)

        # Read the edited content back from the temporary file
        with open(tmp_file_path, 'r', encoding='utf-8') as tmp_file:
            edited_message = tmp_file.read().strip() # Read all content and remove leading/trailing whitespace

        return edited_message # Return the successfully edited message

    except FileNotFoundError:
         # Editor command itself wasn't found
         print(f"Error: Editor command '{editor}' not found. Please set GIT_EDITOR, VISUAL, or EDITOR environment variable, or install a default editor like nano.", file=sys.stderr)
         return None # Indicate editing failed
    except subprocess.CalledProcessError:
         # Editor was run but exited with a non-zero status
         print("Editor exited with an error. Editing may have failed or was cancelled improperly.", file=sys.stderr)
         return None # Indicate editing failed
    except Exception as e:
        # Catch any other unexpected errors during the process
        print(f"An unexpected error occurred while opening editor: {e}", file=sys.stderr)
        return None # Indicate editing failed

    finally:
        # Ensure the temporary file is deleted regardless of success, failure, or exceptions
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path) # Delete the temporary file