"""A connection helper through serial module to any and all connected CNC machines."""
# imports - connector.py, by Mc_Snurtle
import time
from typing import Any, Union

import serial
from serial.tools import list_ports

# ========== Variables ==========
command_interval: Union[int, float] = 0.05  # in seconds
timeout: int = 1    # also in seconds
# feed rates
rapid_rate: int = 100
jog_rate: int = 25
move_rate: int = 25


# ========== Classes ==========
class CNC:
    def __init__(self, serial_port: str, baud_rate: int):
        self.serial_port: str = serial_port
        self.baud_rate: int = baud_rate
        self.connector = None

    def connect(self) -> bool:
        """Performs the initial connection to the CNC over serial, returning its success.

        Returns:
            :returns: (bool), whether a connection was successfully established with the CNC.
        Raises:
            :raises serial.SerialException: if there was a Permission Error whilst connecting to the CNC."""
        try:
            self.connector = serial.Serial(self.serial_port, self.baud_rate, timeout=timeout)
            time.sleep(2)   # wait for connection to establish / wait for GRBL nonsense

            startup_data = ""
            
            # Read all available lines sent by device on connect
            while True:
                if self.connector.in_waiting:
                    line = self.connector.readline().decode("utf-8", errors="replace").strip()
                    if line:
                        print(f"[CNC] Startup message line: '{line}'")
                        startup_data += line + "\n"
                    else:
                        # Empty line, just continue reading
                        continue
                else:
                    # No more data waiting to read, break loop
                    break
            
            print(f"[CNC] Full startup message from device:\n{startup_data.strip()}")


            self.connector.flush()  # wait for all communications to finish
            self.handshake()
            self.connector.flush()  # wait for all communications to finish
            print(f"[CNC] Connection established with {self.serial_port}")
        except serial.SerialException as e:
            print(f"[CNC] There was an error whilst attempting first-time connection to the CNC '{self.serial_port}'. ({e})")
            raise serial.SerialException(e)
            return False
        return True

    def handshake(self):
        self.send_gcode("M105")

    def send_gcode(self, command: str, verbose: bool = True, run_anyway: bool = False) -> Any:
        """Streams G-code to connected machine over the serial port. Returns the machine's response.
        WARNING: This function is blocking, and may take time to receive a response from the machine.

        Params:
            :param command: the G-code command to send.
            :type command: str
            :param verbose: (bool), whether to print the CNC's response.
            :type verbose: bool
            :param run_anyway: whether to ignore parsing & sanitization and run as raw G-code, otherwise, comments and blank lines are removed.
            :type run_anyway: bool
        Returns:
            :returns: the response given from the machine after `command` was run. String if command was sent, and Nonetype if the command was invalid (is comment, etc).
            :rtype: Union[str, None]"""

        if not run_anyway: command = self._parse_command(command)

        try:
            if (command is not None and command != "") or run_anyway:
                if verbose: print(f"[CNC] Sending G-code: `{command}`.")
                self.connector.write((command.strip() + "\r\n").encode("utf-8"))

                time.sleep(command_interval)

                response: Any = self.connector.readline().decode("utf-8").strip()  # This requires the connected machine to terminate ALL responses with an EOL!

                if verbose: print(f"[CNC] Got response: `{response}`")
                return response
            else:
                if verbose: print(f"[CNC] Skipping command '{command}'")
        except serial.SerialException as e:
            print(f"[CNC] An unexpected error occured whilst sending G-code to CNC '{self.serial_port}'. See traceback for more. ({e})")

        return None

    def _parse_command(self, command: str) -> Union[str, None]:
        """Strips the given command of all comments, and returns only the valid G-code (if any).

        Params:
            :param command: the G-code command provided to be parsed.
            :type command: str
        Returns:
            :returns: parsed command, if is entirely comment, returns None.
            :rtype: Union[str, None]"""

        command = command.strip()
        if not (
                command.startswith(":")
                or command.startswith("/")
                or command.startswith("(")
                ) and command != "":    # if not a comment only, and not empty space
            for comment in [":", "/", "("]: # for all possible comments...
                if comment in command:
                    comment = comment.split(comment, 1)[0]  # remove the comment part of the command
            return command

        return None

    def move_to(self, extrude: Union[int, float], feed_rate: Union[int, float], x: Union[int, float] = 0, y: Union[int, float] = 0, z: Union[int, float] = 0) -> Any:
        """Sends the connected CNC machine to move to coordinates relative to it's job's datum.
        Uses the corresponding G-code that normalizes movement vectors to ensure all axes reach the destination at the same time.

        Params:
            :param x: (Union[int, float]), the relative X coordinate to move to. Defaults to 0.
            :param y: (Union[int, float]), the relative Y coordinate to move to. Defaults to 0.
            :param z: (Union[int, float]), the relative Z coordinate to move to. Defaults to 0.
            :param feed_rate: (Union[int, float]), the feed rate in units/minute to move at.
            :param extrude: (Union[int, float]), the amount of unit to extrude into the material.
        Returns:
            :returns: (Any), the machines response from running the movement."""

        return self.send_gcode(f"G0 F{feed_rate} E{extrude} X{x} Y{y} Z{z}")

    def move_to_rapid(self, extrude: Union[int, float], x: Union[int, float] = 0, y: Union[int, float] = 0, z: Union[int, float] = 0) -> Any:
        """Sends the connected CNC machine to move to coordinates relative to it's job's datum as fast as possible.
        Uses the corresponding G-code that sends all axes to the destination as fast as possible regardless of when they'll get there.

        Params:
            :param x: (Union[int, float]), the relative X coordinate to move to. Defaults to 0.
            :param y: (Union[int, float]), the relative Y coordinate to move to. Defaults to 0.
            :param z: (Union[int, float]), the relative Z coordinate to move to. Defaults to 0.
            :param extrude: (Union[int, float]), the amount of unit to extrude into the material.
        Returns:
            :returns: (Any), the machines response from running the rapid movement."""

        return self.send_gcode(f"G1 E{extrude} X{x} Y{y} Z{z}")

    def terminate(self) -> None:
        """Safely terminate connection"""
        if self.connector is not None:
            self.send_gcode("M02")  # send "completely terminate job" command
            self.connector.close()  # don't rely on garbage collection to __del__()


# ========== Functions ==========
def get_machines() -> list[dict[str, str]]:
    """Returns a list of all COM ports through PySerial.

    Returns:
        :returns: (list[dict[str, str]]), for example, the return might look like: `[{"port": "COM1", "desc": "A thingy.", "hwid": "ACPI\\PNP0501\\1"}]`."""
    ports = list_ports.comports()
    results: list[dict[str, str]] = []

    for port, desc, hwid in sorted(ports):
        if desc != "n/a":   # filter to only known ports
            results.append({"port": port, "desc": desc, "hwid": hwid})

    return results
