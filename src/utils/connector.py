"""A connection helper through serial module to any and all connected CNC machines."""
# imports - connector.py, by Mc_Snurtle
import time
from typing import Any, Union

import serial
from serial.tools import list_ports

# ========== Variables ==========
command_interval: int = 1  # in seconds
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

    def connect(self):
        self.connector = serial.Serial(self.serial_port, self.baud_rate, timeout=timeout)
        time.sleep(2)   # wait for connection to establish / wait for GRBL nonsense
        self.connector.flushInput()
        self.handshake()
        print(f"[CNC] Conection established with {self.serial_port}")

    def handshake(self):
        self.send_gcode("$$")

    def send_gcode(self, command: str, verbose: bool = True) -> Any:
        """Streams G-code to connected machine over the serial port. Returns the machine's response.
        WARNING: This function is blocking, and may take time to receive a response from the machine.

        Params:
            :param command: (str), the G-code command to send.
            :param verbose: (bool), whether to print the CNC's response.
        Returns:
            :returns: (Any), the response given from the machine after `command` was run."""

        self.connector.write((command.strip() + "\r\n").encode("utf-8"))

        time.sleep(command_interval)

        response: Any = self.connector.readline().decode("utf-8").strip()  # This requires the connected machine to terminate ALL responses with an EOL!

        if verbose: print(f"[CNC] {response}")
        return response

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
