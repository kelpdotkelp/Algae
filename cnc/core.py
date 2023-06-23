"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

baud rate should be 115200 as required by grbl.
distances are always in millimetres.

Author: Noah Stieler, 2023
"""

# TODO command status displayed on gui.
# TODO command error handling

import serial
import time
from dataclasses import dataclass
from math import sqrt

import gui.tab_hardware
from gui.parameter import input_dict


@dataclass
class Point:
    x: float
    y: float

    @property
    def mag(self):
        return sqrt(pow(self.x, 2) + pow(self.y, 2))


target_radius = 20
target_pos = Point(0, 0)


class CNC:

    def __init__(self):
        self.ser = None
        self.origin = False

    def __del__(self):
        if self.ser is not None:
            self.ser.close()

    def connect(self, port: str, baud_rate: int = 115200, timeout: float = 1) -> bool:
        if self.ser is not None:
            self.ser.close()

        try:
            # timeout is in seconds
            self.ser = serial.Serial(port, baudrate=baud_rate, timeout=timeout)

            self.ser.write('\r\n\r\n'.encode('utf-8'))
            time.sleep(2)
            self.ser.flushInput()

            return True
        except serial.serialutil.SerialException as e:
            self.ser = None

            return False

    def set_origin(self) -> None:
        """Sets the origin at the targets current position."""
        self._send_command('G90')  # Absolute positioning
        self._send_command('G92 X0 Y0')  # Set origin point
        self.origin = True

    def set_position(self, new_pos: Point) -> bool:
        """Attempts to move to a new position. Returns false
        if position is outside working area."""
        wa_radius = input_dict['wa_radius'] - input_dict['wa_pad'] - target_radius

        if new_pos.mag < wa_radius:
            self._send_command(f'G0 X{new_pos.x} Y{new_pos.y}')
            time.sleep(2)  # TODO change me!
            return True
        else:
            return False

    def _send_command(self, cmd: str) -> None:
        self.ser.write((cmd + '\n').encode('utf-8'))
        out = self.ser.readlines()

        for item in out:
            item.decode()
        print(out)


def update_target_dim():
    global target_radius
    if gui.tab_hardware.target_selected == 'circular':
        if 0 < input_dict['target_radius'].value <= float('inf'):
            target_radius = input_dict['target_radius'].value
        else:
            target_radius = 0
