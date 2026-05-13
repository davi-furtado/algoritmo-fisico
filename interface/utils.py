from os import path
import sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return path.join(sys._MEIPASS, relative_path)
    base_path = path.dirname(path.abspath(__file__))
    return path.join(base_path, relative_path)