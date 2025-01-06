import os


def delete_file_if_exists(filename):
    # Check if the file exists
    if os.path.exists(filename):
        os.remove(filename)
        print(f"{filename} has been deleted.")
    else:
        print(f"{filename} does not exist.")


# Function to parse directory and base filename
def create_incremented_filename(file_path):
    """
    If a filename already exists, then create an _1, _2 etc version of the file.

    :param file_path:
    :return:
    """
    # Expand '~' to the full home directory path if needed
    file_path = os.path.expanduser(file_path)

    # Parse the directory and base filename
    directory, base_filename = os.path.split(file_path)

    # If no directory is specified, use the current directory
    if not directory:
        directory = "."

    # Call the recursive function to find the incremented filename
    return recursive_create_incremented_filename(base_filename, directory)


# Recursive function to find the next available file name
def recursive_create_incremented_filename(base_filename, directory, suffix=0):
    # Ensure the directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Construct the full path for the file
    if suffix == 0:
        new_filename = os.path.join(directory, base_filename)
    else:
        # Append suffix to base filename (e.g., 'filename_2')
        base, ext = os.path.splitext(base_filename)
        new_filename = os.path.join(directory, f"{base}_{suffix}{ext}")

    # Check if the file exists in the specified directory
    if os.path.exists(new_filename):
        # If it exists, call the function recursively with an incremented suffix
        return recursive_create_incremented_filename(base_filename, directory, suffix + 1)
    else:
        # If it doesn't exist, return the new filename
        return new_filename
