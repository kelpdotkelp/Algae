"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

baud rate should be 115200 as required by grbl.
distances are always in millimetres.

Author: Noah Stieler, 2023
"""

import serial
import time
from dataclasses import dataclass
from math import sqrt, pow

import gui.tab_hardware
from gui.parameter import input_dict


@dataclass
class Point:
    x: float
    y: float

    @property
    def mag(self):
        return sqrt(pow(self.x, 2) + pow(self.y, 2))

    def dist(self, other) -> float:
        return sqrt(pow(self.x - other.x, 2) + pow(self.y - other.y, 2))


target_radius = 20


class CNC:
    FEED_RATE = 400  # mm/min

    def __init__(self):
        self.ser = None
        self.origin = False
        self.pos_list = []
        self.pos_index = 0

    @property
    def pos(self) -> Point:
        if self.pos_index < 0:
            return Point(0, 0)
        else:
            return self.pos_list[self.pos_index]

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
        try:
            self._send_command('G90')  # Absolute positioning
            self._send_command('G92 X0 Y0')  # Set origin point
            self._send_command('G21')  # All units in mm
        except CNCException:
            raise
        self.origin = True

    def set_position(self, pos_cur: Point, pos_new: Point) -> None:
        """Attempts to move to a new position."""
        wa_radius = input_dict['wa_radius'].value - input_dict['wa_pad'].value - target_radius

        if pos_new.mag < wa_radius:
            try:
                self._send_command(f'G1 F{CNC.FEED_RATE} X{pos_new.x} Y{pos_new.y}')
            except CNCException:
                raise
            dist = Point(pos_new.x - pos_cur.x, pos_new.y - pos_cur.y).mag
            time.sleep(dist / (CNC.FEED_RATE / 60))
        else:
            raise CNCException(1)

    def next_position(self) -> None:
        if len(self.pos_list) == 0:
            return

        try:
            if self.pos_index == -1:
                pos_cur = Point(0, 0)
            else:
                pos_cur = self.pos_list[self.pos_index - 1]
            self.pos_index += 1
            self.set_position(pos_cur, self.pos_list[self.pos_index])
        except CNCException:
            raise

    def init_pos_index(self) -> None:
        self.pos_index = -1

    def _send_command(self, cmd: str) -> None:
        self.ser.write((cmd + '\n').encode('utf-8'))
        out = self.ser.readlines()

        for i in range(len(out)):
            out[i].decode()
            out[i] = out[i][:-2]

            if out[i] != b'ok':
                raise CNCException(0, cmd)


class CNCException(Exception):
    def __init__(self, code: int, cmd: str = ''):
        self.code = code
        self.cmd = cmd

    def display(self):
        if self.code == 0:
            gui.bottom_bar.message_display('GCODE error with command: ' + self.cmd, 'red')
        if self.code == 1:
            gui.bottom_bar.message_display('Error: Target tried moving outside of safe area.', 'red')


def update_target_dim():
    global target_radius
    if gui.tab_hardware.target_selected == 'circular':
        if 0 < input_dict['target_radius'].value <= float('inf'):
            target_radius = input_dict['target_radius'].value
        else:
            target_radius = 0
