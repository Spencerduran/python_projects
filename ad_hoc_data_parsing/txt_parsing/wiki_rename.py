import os
import re

"""
VimWiki Filename Standardizer

This script walks through a VimWiki directory and standardizes filenames by:
- Converting all characters to lowercase
- Replacing hyphens with underscores
- Removing special characters (keeping only a-z, 0-9, and underscores)
- Removing duplicate underscores
- Preserving .wiki extensions

The script will:
1. Show all planned filename changes
2. Ask for confirmation before making changes
3. Perform the renaming
4. Print instructions for updating wiki links in affected files

Usage: Set wiki_path variable to your VimWiki directory and run the script
"""


def standardize_filename(filename):
    # Keep the .wiki extension as is
    if not filename.endswith(".wiki"):
        return filename

    # Split name and extension
    name = filename[:-5]  # remove .wiki

    # Convert to lowercase
    name = name.lower()

    # Convert dashes to underscores
    name = name.replace("-", "_")

    # Replace multiple underscores with single underscore
    name = re.sub(r"_+", "_", name)

    # Remove any special characters except underscores
    name = re.sub(r"[^a-z0-9_]", "", name)

    # Add back .wiki extension
    return f"{name}.wiki"


def rename_wiki_files(directory):
    changes = []

    # Walk through all directories
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".wiki"):
                old_path = os.path.join(root, filename)
                new_filename = standardize_filename(filename)
                new_path = os.path.join(root, new_filename)

                if old_path != new_path:
                    changes.append((old_path, new_path))

    # First, print all planned changes
    if changes:
        print("The following files will be renamed:")
        for old, new in changes:
            print(f"{old} -> {new}")

        # Ask for confirmation
        response = input("\nDo you want to proceed with these changes? (yes/no): ")
        if response.lower() == "yes":
            # Perform the renaming
            for old_path, new_path in changes:
                try:
                    os.rename(old_path, new_path)
                    print(f"Renamed: {old_path} -> {new_path}")
                except Exception as e:
                    print(f"Error renaming {old_path}: {e}")
        else:
            print("No changes were made.")
    else:
        print("No files need to be renamed.")

    # Return the changes for reference
    return changes


# Usage example (with a path variable)
wiki_path = "/Users/spencer/repos/VimWiki"  # Replace with your actual path
changes = rename_wiki_files(wiki_path)

# After renaming, print instructions for updating links
if changes:
    print("\nFiles have been renamed. You'll need to update your wiki links.")
    print("Search for these patterns in your wiki files:")
    for old_path, new_path in changes:
        old_name = os.path.basename(old_path)[:-5]  # remove .wiki
        new_name = os.path.basename(new_path)[:-5]  # remove .wiki
        print(f"Find: [[{old_name}]] or [{old_name}]")
        print(f"Replace with: [[{new_name}]] or [{new_name}]")
