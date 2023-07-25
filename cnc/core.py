"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

baud rate should be 115200 as required by grbl.
distances are always in millimetres.

Author: Noah Stieler, 2023
"""

import serial
import time
from math import sqrt, pow

import gui.tab_hardware
from gui.parameter import input_dict
from .pos_gen import get_pos_from_file, rand_uniform
from .point import Point

target_radius = 20


class CNC:
    FEED_RATE = 400  # mm/min

    def __init__(self, address):
        self.ser = None
        self.origin = False
        self.pos_list = []
        self.pos_index = 0

        self._connect(address)

    @property
    def pos(self) -> Point:
        if self.pos_index < 0:
            return Point(0, 0)
        else:
            return self.pos_list[self.pos_index]

    def __del__(self):
        if self.ser is not None:
            self.ser.close()

    def _connect(self, port: str, baud_rate: int = 115200, timeout: float = 1) -> None:
        if self.ser is not None:
            self.ser.close()

        try:
            # timeout is in seconds
            self.ser = serial.Serial(port, baudrate=baud_rate, timeout=timeout)

            self.ser.write('\r\n\r\n'.encode('utf-8'))
            time.sleep(2)
            self.ser.flushInput()
        except serial.serialutil.SerialException as e:
            self.ser = None

    def set_origin(self) -> None:
        """Sets the origin at the targets current position."""
        try:
            self._send_command('G90')  # Absolute positioning
            self._send_command('G92 X0 Y0 Z0')  # Set origin point
            self._send_command('G21')  # All units in mm
        except CNCException:
            raise
        self.origin = True

    def set_position(self, pos_cur: Point, pos_new: Point) -> None:
        """Attempts to move to a new position. Delays are put in place to ensure
        VNA does not fire while there is still movement."""
        wa_radius = input_dict['wa_radius'].value - input_dict['wa_pad'].value - target_radius

        if pos_new.mag < wa_radius:
            try:
                time.sleep(0.5)
                self._send_command(f'G1 F{CNC.FEED_RATE} X{pos_new.x} Y{pos_new.y}')

                # Wait until movement has been completed.
                idle_state = False
                while not idle_state:
                    out = self._send_command('?')  # Query status
                    for string in out:
                        if string[0] == '<':
                            end = string.find('|')

                            # Check while moving the CNC that it is in bounds
                            if string[1:end] == 'Run':
                                query_x = string[string.find(':') + 1: string.find(',')]
                                query_y = string[string.find(',') + 1: string.find(',', string.find(',') + 1)]
                                moving_pos = Point(float(query_x), float(query_y))
                                if moving_pos.mag > wa_radius:
                                    self._send_command('!')  # Feed stop
                                    raise CNCException(1)

                            if string[1:end] == 'Idle':
                                idle_state = True

                time.sleep(1)
            except CNCException:
                raise
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

    def initialize(self) -> None:
        self.pos_index = -1

        if input_dict['cnc_enable']:
            radius = input_dict['wa_radius'].value - input_dict['wa_pad'].value - target_radius
            if input_dict['pos_gen_type'].value == 'random uniform':
                self.pos_list = rand_uniform(input_dict['num_pos'].value, radius, order='nearest_neighbour')
            elif input_dict['pos_gen_type'].value == 'list':
                self.pos_list = get_pos_from_file()
        else:
            self.pos_list = []

    def _send_command(self, cmd: str) -> list:
        self.ser.write((cmd + '\n').encode('utf-8'))
        out = self.ser.readlines()

        for i in range(len(out)):
            out[i] = out[i].decode('utf-8')
            out[i] = out[i][:-2]  # Remove \r\n

            # Status command begins with a '<'
            if not (out[i] == 'ok' or out[i][0] == '<'):
                raise CNCException(0, cmd)

        return out


def create_cnc(address: str) -> CNC:
    new_cnc = CNC(address)
    if new_cnc.ser is not None:
        return new_cnc
    else:
        return None


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
    """This is used to calculate the radius of the target. If the
    target_type is rectangular, then the minimum bounding disk is calculated for it."""
    global target_radius
    if input_dict['target_type'].value == 'circular':
        if 0 < input_dict['target_radius'].value < float('inf'):
            target_radius = input_dict['target_radius'].value
        else:
            target_radius = 0
    if input_dict['target_type'].value == 'rectangular':
        if 0 < input_dict['target_length'].value < float('inf') \
                and 0 < input_dict['target_width'].value < float('inf'):
            target_radius = 0.5 * sqrt(
                pow(input_dict['target_length'].value, 2) + pow(input_dict['target_width'].value, 2))
        else:
            target_radius = 0
