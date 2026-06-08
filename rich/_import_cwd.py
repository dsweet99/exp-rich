import os

try:
    _IMPORT_CWD = os.path.abspath(os.getcwd())
except FileNotFoundError:
    _IMPORT_CWD = ""
