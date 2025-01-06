from util.file_utils import create_incremented_filename, delete_file_if_exists

import os
import glob
import shutil
import unittest


# Assuming the create_incremented_filename and recursive_create_incremented_filename functions are defined above

# Helper function to clean up specific files and directories
def cleanup_files_and_directories(test_cases):

    # Iterate through the tests cases to clean up both files and directories
    for file_path in test_cases:
        # Expand the home directory if necessary
        file_path = os.path.expanduser(file_path)

        # Get the directory and filename
        directory, base_filename = os.path.split(file_path)

        # If directory is specified, clean the directory
        if directory and os.path.exists(directory):
            shutil.rmtree(directory)  # Removes directory and all its contents

        # If the file is in the current directory
        if directory == "." or not directory:
            files = glob.glob(base_filename)
            for file in files:
                os.remove(file)
    # delete straggler file
    delete_file_if_exists("filename_1.txt")




# Test class for testing the filename creation function
class TestFilenameIncrement(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("Setup")
        # List of file path tests cases
        cls.test_cases = [
            "filename.txt",  # No directory, current directory
            "linkedIn_App/filename.txt",  # Directory with base filename
            "~/linkedIn_App/user1/filename.txt",  # Home directory with base filename
            "test_dir/file.txt",  # Custom directory
            "subdir/anotherfile.txt"  # Another subdirectory
        ]
        # Clean up any files and directories before tests start
        cleanup_files_and_directories(cls.test_cases)

    def test_create_incremented_filename(self):
        expected_filenames = []

        # Test all cases and confirm filename increment works
        for i, file_path in enumerate(self.test_cases):
            # Create the first file
            filename_1 = create_incremented_filename(file_path)
            expected_filenames.append(filename_1)
            with open(filename_1, 'w') as f:
                f.write(f"Test file {i} - first")

            # Create the second file, which should be incremented
            filename_2 = create_incremented_filename(file_path)
            expected_filenames.append(filename_2)
            with open(filename_2, 'w') as f:
                f.write(f"Test file {i} - second")

            # Check that the filenames are different
            self.assertNotEqual(filename_1, filename_2, f"Failed increment test for {file_path}")

        # Confirm that the files were created and correctly named
        for filename in expected_filenames:
            self.assertTrue(os.path.exists(filename), f"File does not exist: {filename}")

    @classmethod
    def tearDownClass(cls):
        print("Teardown")
        # Clean up any files and directories after the tests or
        # don't use so I can look at the files
        cleanup_files_and_directories(cls.test_cases)


if __name__ == '__main__':
    # Run the tests
    unittest.main()
