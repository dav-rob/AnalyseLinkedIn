import os
from dotenv import load_dotenv

# Flag to track if load_dotenv has been called
_dotenv_loaded = False

def load_env_if_needed():
    """
    Loads a dotenv file and sets a flag to indicate that it has been loaded.
    :return:
    """
    global _dotenv_loaded
    if not _dotenv_loaded:
        load_dotenv()
        load_dotenv("api.env")
        _dotenv_loaded = True

def get_env_key(key):
    """
    Gets a key from .env file.

    :param key: The key to look up in the environment variables.
    :return: The value of the environment variable.
    :raises: ValueError if the key is not found.
    """
    load_env_if_needed()
    api_key = os.getenv(key)
    if api_key is None:
        raise ValueError(f"{key} key not found in environment variables. Please set it in your .env file.")
    return api_key
