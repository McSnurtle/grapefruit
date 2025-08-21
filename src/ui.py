# imports - ui.py, by Mc_Snurtle
import os
import sys
import time
import tkinter as tk
from tkinter import (ttk, filedialog, messagebox)
from typing import (Iterable, Union)

from utils.path import (get_home, gcode_filetypes)
from utils.connector import (CNC, get_machines)

# ========== Constants ==========
WIDTH: int = 800
HEIGHT: int = 600
command_interval: int = 1  # in seconds # TODO: move this and it's references across all scripts to the new gcode module as mentioned in issue #1

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
        self.serial_port: str = "COM3"  # TODO: make a widget for machine setup accessed through "Machine" menubar cascade.
        self.baud_rate: int = 9600
        self.cnc = None
        self.gcode_path: str = ""
        self.status: str = "Welcome to grapefruit! To connect a machine, select Machine > Connect to <your machine>, and load some some G-code from File > Open!"

        if not len(get_machines()) > 0:
            messagebox.showwarning("No Machines Found!", "No valid CNC machines were found over COM ports. Please ensure it is on and plugged in properly.")

        # layout
        self._construct_menus()

        status_frame: tk.Frame = tk.Frame(self, bg="#000000")
        self.status_bar: tk.Label = tk.Label(status_frame, text=self.status, justify="left", anchor="w")
        self.status_bar.pack(side="left", fill="x", expand=True, padx=1,
                             pady=1)  # couldn't supress PyCharm warnings about Literals
        status_frame.pack(side="bottom", anchor="sw", fill="x")

        # TODO: move the following gcode section to it's own self._construct_gcode() method. It's cluttering up __init__()!

        gcode_tabs = ttk.Notebook(self, width=WIDTH//2, height=HEIGHT//3)

        mdi_frame: tk.Frame = tk.Frame(gcode_tabs)
        gcode_tabs.add(mdi_frame, text="MDI")

        mdi_controls = tk.Frame(mdi_frame)
        run_mdi = tk.Button(mdi_controls, text="Run MDI", bg="#00FF00", command=self._run_mdi)
        run_mdi.pack(side="left", padx=5, pady=5)
        stop_mdi = tk.Button(mdi_controls, text="Stop MDI", bg="#FF0000")
        stop_mdi.pack(side="left", padx=5, pady=5)
        mdi_controls.pack(side="bottom", fill="x", expand=True)
        self.mdi_input = tk.Text(mdi_frame)
        mdi_scrollbar = tk.Scrollbar(mdi_frame, command=self.mdi_input.yview)
        mdi_scrollbar.pack(side="right", fill="y", expand=True)
        self.mdi_input["yscrollcommand"] = mdi_scrollbar.set  # widget.yscrollcommand is a PyRight error apparently
        self.mdi_input.pack(fill="both", expand=True)


        gcode_frame: tk.Frame = tk.Frame(gcode_tabs)
        gcode_tabs.add(gcode_frame, text="G-code")

        gcode_controls = tk.Frame(gcode_frame)
        run_gcode = tk.Button(gcode_controls, text="Run G-code", bg="#00FF00", command=self._run_gcode)
        run_gcode.pack(side="left", padx=5, pady=5)
        gcode_controls.pack(side="bottom", fill="x", expand=True)
        self.gcode_input = tk.Text(gcode_frame, state="disabled")
        gcode_scrollbar = tk.Scrollbar(gcode_frame, command=self.gcode_input.yview)
        gcode_scrollbar.pack(side="right", fill="y", expand=True)
        self.gcode_input["yscrollcommand"] = gcode_scrollbar.set
        self.gcode_input.pack(fill="both", expand=True)

        gcode_tabs.pack(side="left")

    def _construct_menus(self):
        """Instantiate the menus"""
        menubar = tk.Menu(self, tearoff=False)

        file_menu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self._get_and_load_gcode)  # could have used a lambda... But didn't!
        file_menu.add_separator()
        file_menu.add_command(label="Exit Program", command=self.terminate)

        machine_menu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Machine", menu=machine_menu)
        for machine in get_machines():
            machine_menu.add_command(label=f"Connect to {machine["desc"]} ({machine["port"]}", command=lambda: self._connect_to_machine(machine["port"]))

        self.configure(menu=menubar)

    def _connect_to_machine(self, serial_port: str) -> None:
        self.serial_port = serial_port
        self.cnc = CNC(serial_port=self.serial_port, baud_rate=self.baud_rate)
        self.cnc.connect()

    def _run_mdi(self, verbose: bool = True) -> None:
        commands = self.mdi_input.get(1.0, tk.END).split("\n")  # split on newlines

        self._stream_gcode(commands, verbose=verbose)

    def _run_gcode(self, verbose: bool = True) -> None:
        commands = self.gcode_input.get(1.0, tk.END).split("\n")

        self._stream_gcode(commands, verbose=verbose)

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
        self.gcode_input.configure(state="normal")
        [self.gcode_input.insert(float(index+1), command) for index, command in enumerate(commands)]
        self.gcode_input.configure(state="disabled")

        if verbose: print(
            "".join(commands))  # don't add \n since .readlines() already parses that out from text documents.

        return commands

    def _stream_gcode(self, commands: Iterable[str], verbose: bool = True) -> None:
        """Initiates a connection with the CNC's serial port and sends the provided G-code commands in sequence."""

        for command in commands:
            if command:
                # NOT IMPLEMENTED YET
                pass
                # response = self.cnc.send_gcode(command)
                if verbose: print(f"[Grapefruit] Running G-code: `{command}`."); # print(f"[Grapefruit] Got response: `{response}`.")
                time.sleep(command_interval)

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
