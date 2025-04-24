import sys
import os

def resourcePath(relativePath):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # If running from PyInstaller bundle
        basePath = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        # If running from the source code
        basePath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # Adjust to point to the root of the project

    return os.path.join(basePath, relativePath)