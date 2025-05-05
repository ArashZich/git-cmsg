# ui.py

# Import necessary libraries
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter # Not used yet, but kept for potential future use
from prompt_toolkit.validation import Validator, ValidationError
# KeyBindings import is REMOVED as requested
# from prompt_toolkit.key_bindings import KeyBindings
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

# --- REMOVE KeyBindings instance and handler as requested ---
# kb = KeyBindings()
# @kb.add('?')
# def _(event):
#    # ... (Your helper code here) ...
#    pass


# --- Function to get Commit Type ---
def get_commit_type(language_code):
    """Prompts user for commit type and returns the selected type string."""

    # --- REMOVE setting language_code on the app if KeyBindings is removed ---
    # from prompt_toolkit.application import get_app
    # app = get_app()
    # app.language_code = language_code # This was used for KeyBindings handler


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


    # Build the prompt message with numbered options
    prompt_message = f"{get_localized_message('prompt_type', language_code)}\n" # Main question
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
                prompt_message, # The question with options
                validator=TypeValidator() # Use our custom validator
                # REMOVE key_bindings argument as kb is removed
                # key_bindings=kb
            ).strip()

            # Convert valid input (which passed validation) to the actual type string
            type_index = int(user_input)
            selected_key = ordered_type_keys[type_index - 1] # Get key from 0-based index
            return type_key_to_string[selected_key] # Return the standard type string (e.g., 'feat')

        except (ValueError, IndexError, ValidationError):
             # Validator prints the error message, so just continue the loop if validation failed
             pass


# --- Function to get Commit Subject ---
def get_commit_subject(language_code, commit_type):
    """Prompts user for commit subject."""

    # --- REMOVE setting language_code on the app if KeyBindings is removed ---
    # from prompt_toolkit.application import get_app
    # app = get_app()
    # app.language_code = language_code # This was used for KeyBindings handler


    # Build the prompt message
    prompt_message = (
        f"Type: {commit_type}\n" # Display the selected type for context
        f"Subject: {get_localized_message('prompt_subject', language_code)}\n" # Subject question (localized)
        f"{get_localized_message('hint_subject', language_code)}\n" # Subject guideline hint (localized)
        f"> " # Input indicator
    )

    # Get user input using prompt_toolkit (single line by default)
    # REMOVE key_bindings argument
    user_input = prompt(prompt_message #, key_bindings=kb
                       ).strip()

    return user_input


# --- Function to generate Scope Suggestions ---
def generate_scope_suggestions(staged_files):
    """Generates potential scope suggestions based on staged file paths."""
    suggestions = set() # Use a set to store unique suggestions

    for filepath in staged_files:
        # Split path into components
        # os.path.normpath handles different separators (\ and /)
        # os.path.dirname gets the directory part (e.g., 'src/components')
        # Split the directory path into parts (e.g., ['src', 'components'])
        path_parts = os.path.normpath(os.path.dirname(filepath)).split(os.sep)

        # Add parent directories and cumulative paths as suggestions
        # Iterate through parts to create cumulative scopes (e.g., 'src', 'src/components')
        current_scope_parts = []
        for part in path_parts:
            if part and part != '.': # Ignore empty parts and current directory '.'
                current_scope_parts.append(part)
                # Add the cumulative path as a suggestion (e.g., ['src', 'components'] -> 'src/components')
                suggestions.add('/'.join(current_scope_parts)) # Use '/' as standard scope separator


    # Convert set to sorted list and limit the number of suggestions
    sorted_suggestions = sorted(list(suggestions))
    # Limit to a reasonable number, e.g., first 10 or 15
    return sorted_suggestions[:15]


# --- Function to get Commit Scope (with more guidance) ---
def get_commit_scope(language_code, commit_type, commit_subject, staged_files):
    """Prompts user for commit scope, providing suggestions based on staged files."""

    # Generate suggestions based on staged files
    suggestions = generate_scope_suggestions(staged_files)

    # --- Build the prompt message with improved structure ---
    prompt_message_parts = [
        f"Type: {commit_type}", # Display previous info
        f"Subject: {commit_subject}",
        f"{get_localized_message('prompt_scope', language_code)}\n", # Main question (localized)

        # --- ADDED GUIDANCE FOR SCOPE (using new message keys and separating English/Persian) ---
        f"{get_localized_message('explanation_header_en', language_code)}\n", # Explanation header (English)
        f"{get_localized_message('scope_explanation_en', language_code)}\n", # English explanation (multi-line)
        f"\n", # Blank line separator between English and Persian explanations
        f"{get_localized_message('explanation_header_fa', language_code)}\n", # Explanation header (Persian)
        f"{get_localized_message('scope_explanation_fa', language_code)}\n", # Persian explanation (multi-line)
        # --- END ADDED GUIDANCE ---
    ]

    # Add suggestions if any
    if suggestions:
        suggestions_header = get_localized_message('suggestions_header', language_code)
        # Format suggestions as a comma-separated list
        prompt_message_parts.append(f"\n{suggestions_header}: {', '.join(suggestions)}\n") # Add blank line before suggestions

    # Add the optional/skip guideline
    prompt_message_parts.append(f"\n{get_localized_message('hint_skip', language_code)}\n") # Add blank line before skip hint
    prompt_message_parts.append("> ") # Input indicator

    # Join all parts to create the final prompt string
    prompt_message = "".join(prompt_message_parts)


    # Get user input using prompt_toolkit (single line)
    user_input = prompt(prompt_message).strip()

    return user_input


# --- Function to get Commit Body (Full Description) ---
def get_commit_body(language_code, commit_type, commit_subject, commit_scope):
    """Prompts user for commit body (multi-line input)."""

    # --- REMOVE setting language_code on the app if KeyBindings is removed ---
    # from prompt_toolkit.application import get_app
    # app = get_app()
    # app.language_code = language_code # This was used for KeyBindings handler

    # Build the prompt message
    prompt_message_parts = [
        f"Type: {commit_type}", # Display previous info
        f"Subject: {commit_subject}",
        f"Scope: {commit_scope if commit_scope else '(skipped)'}\n", # Show scope or skipped
        f"{get_localized_message('prompt_body', language_code)}\n", # Body question (localized)
        f"{get_localized_message('hint_body', language_code)}\n", # Body guideline hint (localized)
        f"> ", # Input indicator
    ]
    prompt_message = "".join(prompt_message_parts)

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

    # Common patterns in branch names for issue numbers:
    # feature/#123-description, fix/issue-456, bugfix/789, chore_101_task
    # Regex finds sequences of digits (\d+) that are preceded by a non-digit character or start of string ([^0-9]|^)
    # and potentially followed by a non-digit or end of string ([^0-9]|$)
    # This regex looks for numbers that are likely standalone issue numbers or part of issue references.
    # It captures the digits in groups 1 or 4.
    issue_number_pattern = re.compile(r'[^0-9](\d+)([^0-9]|$)|(^(\d+))')

    # Find all potential issue numbers in the branch name
    # findall returns a list of tuples for groups. We need to flatten it and filter for actual digits.
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

    # You could add logic here to check if these issue numbers exist in an issue tracker API (more complex!)

    # Convert set to sorted list
    sorted_suggestions = sorted(list(suggestions))
    # Limit to a reasonable number, e.g., first 5
    return sorted_suggestions[:5]


# --- Function to get Commit Issues (with more guidance) ---
def get_commit_issues(language_code, commit_type, commit_subject, commit_scope, commit_body):
    """Prompts user for related issues, providing suggestions from the branch name."""

    # Get current branch name using the git_utils function
    branch_name = get_current_branch_name()

    # Generate issue suggestions based on branch name
    suggestions = generate_issue_suggestions_from_branch(branch_name)


    # --- Build the prompt message with improved structure ---
    prompt_message_parts = [
        f"Type: {commit_type}", # Display previous info
        f"Subject: {commit_subject}",
        f"Scope: {commit_scope if commit_scope else '(skipped)'}\n", # Show scope or skipped
        f"Body: {'(skipped)' if not commit_body.strip() else '...'}\n", # Show if body was entered or skipped ('...' if not empty)
        f"{get_localized_message('prompt_issues', language_code)}\n", # Issues question (localized)

        # --- ADDED GUIDANCE FOR ISSUES (using new message keys and separating English/Persian) ---
        f"\n{get_localized_message('explanation_header_en', language_code)}\n", # Explanation header (English)
        f"{get_localized_message('issues_explanation_en', language_code)}\n", # English explanation (multi-line)
        f"\n{get_localized_message('explanation_header_fa', language_code)}\n", # Explanation header (Persian)
        f"{get_localized_message('issues_explanation_fa', language_code)}\n", # Persian explanation (multi-line)
        # --- END ADDED GUIDANCE ---
    ]

    # Add suggestions if any
    if suggestions:
        suggestions_header = get_localized_message('suggestions_header', language_code)
        prompt_message_parts.append(f"\n{suggestions_header}: {', '.join(suggestions)}\n") # Add blank line before suggestions

    # Add the optional/skip and example format guidelines
    prompt_message_parts.append(f"\n{get_localized_message('hint_skip', language_code)}\n") # Add blank line before skip hint
    prompt_message_parts.append(f"{get_localized_message('hint_issues', language_code)}\n") # Localized hint for format (e.g., Closes #123)
    prompt_message_parts.append("> ") # Input indicator

    # Join all parts to create the final prompt string
    prompt_message = "".join(prompt_message_parts)


    # --- Get user input using prompt_toolkit ---
    user_input = prompt(prompt_message).strip() # Single line input

    return user_input


# --- Function to display final preview and confirm ---
def confirm_commit(commit_message_string, language_code):
    """
    Displays the final commit message preview and asks for user confirmation.
    Allows editing the message externally.

    Args:
        commit_message_string (str): The formatted commit message string.
        language_code (str): The chosen language code ('en' or 'fa').

    Returns:
        str: The confirmed or edited commit message string, or None if aborted.
             Returns the original string if 'y' is chosen.
             Returns the edited string if 'e' is chosen and editing is successful.
             Returns None if 'n' or Ctrl+D is chosen.
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
            user_choice = prompt(confirm_prompt_text).strip().lower()

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
                     # Indicate returning to preview loop
                     # print(get_localized_message('proceeding', language_code, lang=language_code)) # Maybe redundant here
                     # Loop continues to show the new preview
                else:
                     # If editing failed or was cancelled in editor, prompt again
                     print("Editing cancelled or failed. Please try again or choose y/n.", file=sys.stderr)
                     # Loop continues to ask for confirmation

            else:
                # Invalid input, prompt again
                print("Invalid choice. Please enter 'y', 'n', or 'e'.", file=sys.stderr)
                # Loop continues to ask for confirmation

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
    # suffix=".gitmessage" is a convention, helps some editors with syntax highlighting
    # delete=False means the file is not automatically deleted when closed, we delete it manually in finally
    # encoding='utf-8' ensures proper handling of international characters
    with tempfile.NamedTemporaryFile(mode='w+', suffix=".gitmessage", delete=False, encoding='utf-8') as tmp_file:
        tmp_file_path = tmp_file.name
        tmp_file.write(initial_message)
        tmp_file.flush() # Ensure all data is written to disk before opening editor

    try:
        # Open the editor with the temporary file
        # Use subprocess.run which is generally preferred over subprocess.call or os.system
        # shell=True is often needed for the system to find the editor command correctly,
        # especially if it has spaces or is an alias/function in the shell.
        # check=True will raise CalledProcessError if the editor command fails (e.g., not found, editor exits with error)
        # The user interacts with the editor directly in the terminal, so capture_output=False (default) is fine.
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
         # Editor was run but exited with a non-zero status (e.g., user saved and exited with an error status, though most editors exit 0 on save)
         print("Editor exited with an error. Editing may have failed or was cancelled improperly.", file=sys.stderr)
         return None # Indicate editing failed
    except Exception as e:
        # Catch any other unexpected errors during the process
        print(f"An unexpected error occurred while opening editor: {e}", file=sys.stderr)
        return None # Indicate editing failed

    finally:
        # Ensure the temporary file is deleted regardless of success, failure, or exceptions
        # Use os.unlink for reliability across OSes
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path) # Delete the temporary file


# --- Placeholder functions for next prompts (remain the same) ---
# get_commit_issues is already implemented above.
# def get_commit_issues(language_code, commit_type, commit_subject, commit_scope, commit_body):
#    ...