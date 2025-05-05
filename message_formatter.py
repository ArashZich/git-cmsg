# message_formatter.py

# Import messages for localization to get the file list header
from messages import get_localized_message

def format_message(commit_data, staged_files, language_code): # Added staged_files and language_code
    """
    Formats the collected commit data into a conventional commit message string,
    including a list of staged files in the body.

    Args:
        commit_data (dict): A dictionary containing commit parts:
            'type' (str): The commit type (required).
            'subject' (str): The commit subject (required).
            'scope' (str): The commit scope (optional, can be empty string).
            'body' (str): The commit body (optional, can be empty string).
            'issues' (str): Related issues/footer info (optional, can be empty string).
        staged_files (list): A list of files that are staged for commit.
        language_code (str): The chosen language code ('en' or 'fa').

    Returns:
        str: The formatted commit message string.
    """
    # Get data from the dictionary, stripping whitespace
    commit_type = commit_data.get('type', '').strip()
    subject = commit_data.get('subject', '').strip()
    scope = commit_data.get('scope', '').strip()
    body = commit_data.get('body', '').strip()
    issues = commit_data.get('issues', '').strip() # This assumes issues are entered in a format suitable for the footer

    # --- Build the Header (Type(Scope): Subject) ---
    header_parts = [commit_type] # Start with the type

    # Add scope if it exists
    if scope:
        header_parts.append(f"({scope})") # Add (scope) right after type

    # Add the required colon and space, then the subject
    header_parts.append(":")
    header = "".join(header_parts) + " " + subject # Combine all parts with the space before subject

    # --- Build the Body section (user provided + automated file list) ---
    # Start with the user-provided body
    full_body_content = body

    # Add the list of staged files automatically to the body
    if staged_files:
        file_list_header = get_localized_message('file_list_header', language_code) # Get localized header
        # Add the header for the file list, separated by a blank line from user body if body exists
        file_list_section = f"\n\n{file_list_header}:\n"
        # Add each file in the list, indented perhaps with '-' or '*'
        for f in staged_files:
            file_list_section += f"- {f}\n" # Example: "- path/to/file.js\n"

        # Append the file list section to the user-provided body
        # Ensure there's a blank line *before* the file list if there was a user body
        if full_body_content:
             full_body_content += "\n" # Add one newline if there's user body, file_list_section adds the second

        full_body_content += file_list_section.strip() # Add the file list content


    # Ensure the final body content is separated by a blank line from the header
    body_section = ""
    if full_body_content.strip(): # Only add body section if there's content (user body or file list)
         body_section = "\n\n" + full_body_content.strip() # Add blank line before body content


    # --- Build the Footer section (if issues or other footers are present) ---
    footer_section = ""
    # For MVP, just add the issues string as a footer if it exists
    if issues:
        # The footer is separated from the body (or header if no body) by *at least* one blank line.
        # Adding "\n\n" ensures a blank line before the footer if it exists.
        footer_section = "\n\n" + issues


    # --- Combine all parts ---
    # Start with the header
    final_message_parts = [header]

    # Add body section if it exists (it includes the leading blank line)
    if body_section:
        final_message_parts.append(body_section)

    # Add footer section if it exists (it includes the leading blank line)
    if footer_section:
        final_message_parts.append(footer_section)

    # Join all parts into the final string
    final_message = "".join(final_message_parts)

    # Remove any trailing whitespace just in case
    return final_message.strip()


# Example usage (for testing this module independently) - This block is commented out but useful for development
# if __name__ == "__main__":
#     print("--- Testing message_formatter.py ---")
#     # Example data mimicking collected input
#     test_data_full = {
#         'type': 'feat',
#         'subject': 'implement user login',
#         'scope': 'auth',
#         'body': 'This commit introduces the user login functionality.\nIt includes form validation and authentication logic.',
#         'issues': 'Closes #123, Fixes #456'
#     }
#     test_files = ['src/auth/login.py', 'src/auth/register.py', 'docs/login.md']
#     test_lang = 'en' # Or 'fa'

#     print("\n--- Full Example with Files ---")
#     print(format_message(test_data_full, test_files, test_lang))
#     print("\n--- Minimal Example with Files ---")
#     test_data_minimal = { 'type': 'chore', 'subject': 'update deps', 'scope': '', 'body': '', 'issues': ''}
#     print(format_message(test_data_minimal, test_files, test_lang))
#     print("\n--- Body Only Example with Files ---")
#     test_data_body_only = { 'type': 'refactor', 'subject': 'simplify data fetching', 'scope': 'api', 'body': 'Rewrites fetching.', 'issues': '' }
#     print(format_message(test_data_body_only, test_files, test_lang))
#     print("\n--- Just Files Example (No body/issues) ---")
#     test_data_just_files = { 'type': 'build', 'subject': 'update build script', 'scope': '', 'body': '', 'issues': '' }
#     print(format_message(test_data_just_files, test_files, test_lang))
#     print("\n------------------------")