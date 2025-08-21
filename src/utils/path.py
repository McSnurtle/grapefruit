# imports - path.py, by Mc_Snurtle
import os
from typing import Iterable


# ========== Variables ==========
gcode_filetypes: Iterable[tuple[str, str]] = (
    ("Text Files", "*.txt"),
    ("Numerical Control Files", "*.nc"),
    ("G-code Files", "*.gc"), 
    ("Tape Files", "*.TAP")
)


# ========== Functions ==========
def get_home() -> str:
    """Returns the absolute path to the current user's home directory (cross-platform). E.g. returns `\"/home/mc-snurtle/\"`"""
    return os.path.abspath(os.path.expanduser("~"))
