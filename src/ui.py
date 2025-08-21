# imports - ui.py, by Mc_Snurtle
import os
import sys
import tkinter as tk
from tkinter import filedialog
from typing import Iterable, Union

from utils.path import get_home, gcode_filetypes

# ========== Constants ==========
WIDTH: int = 800
HEIGHT: int = 600

# ========== Variables ==========
__author__: str = "Mc_Snurtle"
__version__: str = "v0.0.1"  # TO DO: make dynamic


# ========== Classes ==========
class UI(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # window decorations
        self.title(f"Grapefruit - {__version__} - by {__author__}")
        self.minsize(WIDTH, HEIGHT)
        self.geometry(f"{WIDTH}x{HEIGHT}")

        # vars
        self.gcode_path: str = ""
        self.status: str = "Welcome to grapefruit!"

        # layout
        self._construct_menus()

        status_frame: tk.Frame = tk.Frame(self, bg="#000000")
        self.status_bar: tk.Label = tk.Label(status_frame, text=self.status, justify="left", anchor="w")
        self.status_bar.pack(side="left", fill="x", expand=True, padx=1,
                             pady=1)  # couldn't supress PyCharm warnings about Literals
        status_frame.pack(side="bottom", anchor="sw", fill="x")

    def _construct_menus(self):
        """Instantiate the menus"""
        menubar = tk.Menu(self, tearoff=False)

        file_menu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self._get_and_load_gcode)  # could have used a lambda... But didn't!
        file_menu.add_separator()
        file_menu.add_command(label="Exit Program", command=self.terminate)

        self.configure(menu=menubar)

    def _load_gcode(self, path: Union[str, None] = None, verbose: bool = False) -> Iterable[str]:
        """Loads G-code based on the given absolute filepath.

        Params:
            :param path: (Union[str, None]), the absolute path to the G-code file (.txt, .nc, .tap) or None. Defaults to `self.gcode_path`.
            :param verbose: (bool), whether to print the **entire log of the G-code**. WARNING: CAN GET VERY MESSY.
        Returns:
            :returns: (Iterable[str]), the list of lines of commands found within the specified file."""

        gcode_path = path if isinstance(path, str) else self.gcode_path
        with open(gcode_path, "r") as fp:
            commands: Iterable[str] = fp.readlines()

        if verbose: print("".join(commands))    # don't add \n since .readlines() already parses that out from text documents.

        return commands

    def _get_and_load_gcode(self):
        self._load_gcode(self.show_open_file_dialog(), verbose=True)

    def show_status(self, message: str) -> None:
        """Updates the status bar at the bottom of the UI with `message`.

        Params:
            :param message: (str), the message to show

        Returns:
            :returns: None"""

        self.status: str = message
        self.status_bar.configure(text=self.status)
        self.status_bar.update()

    def show_open_file_dialog(self) -> str:
        path: str = os.path.abspath(filedialog.askopenfilename(initialdir=get_home(), filetypes=gcode_filetypes))
        print(f"[Grapefruit] Retrieved path '{path}' from user.")
        self.gcode_path = path
        return path

    def terminate(self, exit_code: int = 0) -> None:
        """Safely closes down the UI.

        Params:
            :param exit_code: (int), the code to exit the program with. Defaults to 0 (lived happily ever after)."""

        self.show_status("Closing...")
        # TO DO: safely disconnect from serial stream and tell machine to stop whatever it's doing. We can't just have the bit spinning forever!
        self.destroy()
        sys.exit(exit_code)


if __name__ == '__main__':
    ui = UI()
    ui.mainloop()
