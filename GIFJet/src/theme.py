import os
import sys

def resourcePath(relativePath):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        basePath = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        basePath = os.path.abspath(".")

    return os.path.join(basePath, relativePath)

def loadStyleWithAccent(accentColor):
    path = resourcePath("src/style.qss")  # path to style.qss within the src folder
    with open(path, "r") as file:
        baseStyle = file.read()
    return baseStyle.replace("$ACCENT", accentColor)