import os
def get_data_path(filename):
    """
    Get the absolute path to a data file in the 'data' directory.

    Args:
        filename (str): The name of the file to retrieve.

    Returns:
        str: The absolute path to the specified file.
    """
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', filename)