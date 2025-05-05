# git_cmsg.py

#!/usr/bin/env python3

import sys
# Import necessary modules and functions
# get_current_branch_name is called inside ui.py, so it's not needed directly here
from git_utils import check_git_installed, is_in_git_repository, get_staged_files, perform_commit # Import perform_commit from git_utils
from messages import get_localized_message, MESSAGES
# Import all UI prompt functions, including confirm_commit
from ui import get_commit_type, get_commit_subject, get_commit_scope, get_commit_body, get_commit_issues, confirm_commit

# Import prompt-toolkit specific things needed in main (for language selection)
from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator, ValidationError

# --- Language Validator ---
class LanguageValidator(Validator):
    def validate(self, document):
        text = document.text.strip().lower()
        if text in ['en', 'fa']:
            return # Valid input
        else:
            # Raise validation error with localized message combining both languages
            raise ValidationError(
                message=get_localized_message('invalid_lang', 'en') + " " + get_localized_message('invalid_lang', 'fa'),
                cursor_position=len(document.text)) # Keep cursor at the end

# --- Import message_formatter module ---
import message_formatter


def main():
    """Main function to run the git-cmsg application."""

    # --- Step 1 & 2: Initial Checks (Git installed, In a repo) ---
    if not check_git_installed():
        # Use localized message for critical early error (fallback to en if messages not loaded yet, but should be fine)
        print(get_localized_message("git_not_installed", 'en'), file=sys.stderr)
        sys.exit(1)

    if not is_in_git_repository():
         # Error message and exit are handled inside git_utils based on git's output.
         # git_utils prints a generic git error or the 'Not a git repository' message from messages.
         sys.exit(1) # Exit the whole program if not in a repo


    print("Git is installed and you are in a Git repository.")


    # --- Step 4: Language Selection (Using prompt_toolkit) ---
    chosen_lang = 'en' # Default language before selection
    while True:
        try:
            # Use prompt() from prompt_toolkit for consistent input handling
            lang_input = prompt(
                f"{MESSAGES['en']['select_lang']}/{MESSAGES['fa']['select_lang']}",
                validator=LanguageValidator() # Use validator for en/fa input
            ).strip().lower()

            if lang_input in ['en', 'fa']:
                 chosen_lang = lang_input # Set the chosen language
                 break # Exit the loop
            # else: Validator handles invalid input message and prompt asks again
        except EOFError: # User pressed Ctrl+D during prompt
             print("\nCommit process aborted by user.", file=sys.stderr)
             sys.exit(1)
        except Exception as e: # Catch any other unexpected errors during language selection
             print(f"An error occurred during language selection: {e}", file=sys.stderr)
             sys.exit(1)


    print(get_localized_message("proceeding", chosen_lang, lang=chosen_lang))


    # --- Step 3: Get staged files and display them (Start of the prompt flow - Step 0) ---
    # get_staged_files handles the "No changes staged" message and exit if no files are staged.
    staged_files = get_staged_files()

    # If we reached here, git is installed, we are in a repo, and staged_files is not empty.

    # --- Display staged files using the chosen language header ---
    # This display logic could be moved to ui.py later for better separation
    print(f"\n{get_localized_message('staged_files_header', chosen_lang)}")
    for f in staged_files:
        print(f"- {f}")
    print("-" * 30) # Separator


    # --- Step 5: Start interactive prompts - Collect all commit message data ---
    # Get Commit Type
    commit_type = get_commit_type(chosen_lang)

    # Get Commit Subject
    commit_subject = get_commit_subject(chosen_lang, commit_type)

    # Get Commit Scope (Optional, suggestions from staged files)
    commit_scope = get_commit_scope(chosen_lang, commit_type, commit_subject, staged_files)

    # Get Commit Body (Optional, multi-line)
    commit_body = get_commit_body(chosen_lang, commit_type, commit_subject, commit_scope)

    # Get Commit Issues (Optional, suggestions from branch name)
    commit_issues = get_commit_issues(chosen_lang, commit_type, commit_subject, commit_scope, commit_body)


    # --- Step 6: Format the collected data into the final commit message string ---
    # Create a dictionary with the collected data
    commit_data = {
        'type': commit_type,
        'subject': commit_subject,
        'scope': commit_scope,
        'body': commit_body,
        'issues': commit_issues # Assuming issues is entered in a format suitable for the footer
    }

    # Call the message_formatter function to get the final string
    # Pass staged_files and chosen_lang to the formatter
    final_commit_message = message_formatter.format_message(commit_data, staged_files, chosen_lang)


    # --- Step 7: Display the formatted message preview and ask for final confirmation (using ui.py) ---
    # Call function from ui.py to handle preview and confirmation
    # This function returns the final message (potentially edited) or None if aborted
    confirmed_message = confirm_commit(final_commit_message, chosen_lang)

    # Check user's confirmation choice
    if confirmed_message is None:
        # If confirm_commit returned None, the user aborted or editing failed/was cancelled
        # confirm_commit already printed an aborted message
        sys.exit(1) # Exit with an error status

    # --- Step 8: Execute the git commit command with the final message (using git_utils.py) ---
    # Call function from git_utils.py to perform the actual commit
    # This function handles success/failure messages and exits
    if perform_commit(confirmed_message):
        # perform_commit already printed git's output
        # Optionally print a final success message if perform_commit doesn't exit
        print(get_localized_message("commit_executed", chosen_lang), file=sys.stderr) # Print success message
        sys.exit(0) # Exit successfully
    else:
        # perform_commit printed the error message
        sys.exit(1) # Exit with an error status


    # This line should technically not be reached if the process completes successfully or with error
    # print("An unexpected state was reached.", file=sys.stderr)
    # sys.exit(1)


if __name__ == "__main__":
    main()