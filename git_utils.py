# git_utils.py

import subprocess
import sys
import os
import re
import tempfile # Import tempfile for creating temporary files

# Note: subprocess is already imported by one of the functions.

def check_git_installed():
    """Checks if Git is installed and available in the PATH."""
    try:
        # Try to run a simple git command to check availability
        subprocess.run(['git', '--version'], check=True, capture_output=True)
        # check=True will raise CalledProcessError if git command fails
        # capture_output=True prevents output from showing up directly
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        # FileNotFoundError: git command not found in PATH
        # CalledProcessError: git command failed (e.g., permission issues, though less likely for --version)
        return False
    except Exception as e:
        # Consider using a proper logging mechanism later instead of print
        print(f"An unexpected error occurred while checking Git: {e}", file=sys.stderr)
        return False

def is_in_git_repository():
    """Checks if the current directory is inside a Git repository."""
    try:
        # git rev-parse --is-inside-work-tree returns 0 if inside a repo, 1 otherwise
        result = subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            check=False, # We handle the return code manually (expect 1 if not in repo)
            capture_output=True, # Capture stdout/stderr
            text=True # Decode output as text
        )
        return result.returncode == 0 # Return True if return code is 0 (is in repo)
    except FileNotFoundError:
         # This error should ideally be caught by check_git_installed earlier,
         # but added here as a defensive check.
        print("Error: 'git' command not found while checking repository status.", file=sys.stderr)
        sys.exit(1) # Exit the whole program if git isn't found here either
    except Exception as e:
        print(f"An unexpected error occurred while checking repository status: {e}", file=sys.stderr)
        sys.exit(1) # Exit the whole program on other errors


def get_staged_files():
    """Runs git status --porcelain and returns a list of staged files."""
    staged_files = []
    try:
        # Run git status --porcelain v1 format (simpler to parse for basic info)
        # check=False because we handle the return code manually (e.g., if not in a repo,
        # although that should be caught by is_in_git_repository)
        result = subprocess.run(
            ['git', 'status', '--porcelain', '-z'], # Use -z to handle filenames with spaces better
            check=False,
            capture_output=True,
            text=True, # Get output as text (handles UTF-8 on modern systems)
            cwd=os.getcwd() # Ensure command runs in current directory
        )

        # Handle potential errors from git status
        if result.returncode != 0:
             # This shouldn't happen if is_in_git_repository passed, but as a safeguard
             print(f"Error running 'git status --porcelain':\n{result.stderr}", file=sys.stderr)
             sys.exit(1) # Exit the whole program


        # Parse the --porcelain -z output
        # -z uses a null byte instead of newline as separator
        # Each record is typically: XY file_path\x00
        # R/C records are: RX original_path\x00new_path\x00
        # We split by null byte, the last item is empty after the final null byte
        entries = result.stdout.strip('\x00').split('\x00')

        i = 0
        while i < len(entries):
            entry = entries[i]
            if not entry: # Skip empty entries (e.g., resulting from split)
                i += 1
                continue

            status = entry[:2] # Get the status codes (e.g., "A ", " M", "AM", "R ")
            filepath = entry[3:] # Get the rest of the entry (filename(s))

            # Check if the file is staged (Index status - first char - is not ' ')
            if status[0] != ' ':
                if status[0] in ['R', 'C']:
                    # For R and C, the next entry is the *new* path after the original path in the current entry
                    original_path = filepath # This is the original path part of the R/C entry
                    i += 1 # Move to the next entry which contains the new path
                    if i < len(entries):
                         filepath = entries[i] # The new path for R/C
                    else:
                         print(f"Warning: Unexpected end of porcelain output after R/C entry: {entry}", file=sys.stderr)
                         # Fallback to original path or skip? Let's skip for safety in parsing.
                         i += 1 # Ensure we move past the problematic state
                         continue # Skip this entry

                # At this point, filepath contains the relevant path (new path for R/C, only path for others)
                staged_files.append(filepath)

            i += 1 # Move to the next entry (or the one after the new path for R/C)


        # If no files are staged, inform the user and exit successfully
        if not staged_files:
             # Use sys.stderr for user-facing info that isn't part of standard output
             print("No changes are staged. Please stage changes (`git add .`) before committing.", file=sys.stderr)
             sys.exit(0) # Exit with status 0 (success)

        return staged_files

    except FileNotFoundError:
        # Should have been caught by check_git_installed
        print("Error: 'git' command not found during status check.", file=sys.stderr)
        sys.exit(1) # Exit the whole program
    except Exception as e:
        print(f"An unexpected error occurred while getting git status: {e}", file=sys.stderr)
        sys.exit(1) # Exit the whole program

# --- Function to get current branch name ---
def get_current_branch_name():
    """Gets the current Git branch name."""
    try:
        # git rev-parse --abbrev-ref HEAD returns the current branch name
        # HEAD is used to refer to the current commit
        # --abbrev-ref gets the branch name instead of the full hash
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            check=True, # Check=True will raise error if not in repo or detached HEAD (though we handle not in repo earlier)
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        branch_name = result.stdout.strip()

        # Handle detached HEAD state (git rev-parse returns HEAD)
        if branch_name == 'HEAD':
             # Return None or a specific string if in detached HEAD state
             return None # Or maybe "(detached HEAD)"


        return branch_name

    except FileNotFoundError:
        # Should have been caught by check_git_installed
        print("Error: 'git' command not found during branch check.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
         # This could happen if not in a git repo (already checked) or other git errors
         # For detached HEAD, rev-parse --abbrev-ref HEAD might return 'HEAD' and exit 0.
         # Other errors (like not a repo) would exit non-zero.
         if not is_in_git_repository(): # Defensive check
              # Error already handled by is_in_git_repository
              sys.exit(1)
         else:
              # Handle other git errors during branch check
              print(f"Error getting branch name: {e.stderr.strip()}", file=sys.stderr)
              return None # Return None on error


    except Exception as e:
        print(f"An unexpected error occurred while getting branch name: {e}", file=sys.stderr)
        return None

# --- Function to perform the Git commit ---
def perform_commit(commit_message_string):
    """
    Executes the git commit command with the given message.
    Uses a temporary file for the message to handle multi-line and special characters.

    Args:
        commit_message_string (str): The formatted commit message string.

    Returns:
        bool: True if the commit was successful, False otherwise.
        Exits the program on failure.
    """
    # Create a temporary file to write the commit message to
    # delete=False means the file is not automatically deleted when closed
    with tempfile.NamedTemporaryFile(mode='w+', suffix=".gitmessage", delete=False, encoding='utf-8') as tmp_file:
        tmp_file_path = tmp_file.name
        tmp_file.write(commit_message_string)
        tmp_file.flush() # Ensure content is written to disk

    try:
        # Execute the git commit command, reading the message from the temporary file
        # -F reads the message from the specified file
        # We don't use shell=True here as it's generally safer with subprocess.run
        # check=True will raise CalledProcessError if the git commit command fails
        result = subprocess.run(
            ['git', 'commit', '-F', tmp_file_path],
            check=True,
            capture_output=True,
            text=True,
            cwd=os.getcwd() # Run command in current directory
        )

        # If check=True, we only reach here on success
        # Print git's output (usually confirmation of commit)
        print(result.stdout, file=sys.stdout) # Print successful commit message
        # print(result.stderr, file=sys.stderr) # Print any stderr output (less common on success)
        return True # Commit successful

    except FileNotFoundError:
        # This should not happen if check_git_installed passed
        print("Error: 'git' command not found during commit execution.", file=sys.stderr)
        return False # Indicate failure
    except subprocess.CalledProcessError as e:
         # This happens if git commit fails (e.g., no changes added, conflicts, hooks failed)
         print(f"Error executing git commit:\n{e.stderr.strip()}", file=sys.stderr)
         # print(f"Git command: {' '.join(e.cmd)}", file=sys.stderr) # Optional: print the command that failed
         # print(f"Return code: {e.returncode}", file=sys.stderr) # Optional: print return code
         return False # Indicate failure
    except Exception as e:
        print(f"An unexpected error occurred during commit execution: {e}", file=sys.stderr)
        return False # Indicate failure

    finally:
        # Ensure the temporary file is deleted regardless of success or failure
        # Use os.unlink for reliability across OSes
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path) # Delete the temporary file


# Note: We don't need the if __name__ == "__main__": block in utility files
# because they are meant to be imported and used by other scripts.