"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

baud rate should be 115200 as required by grbl.
distances are always in millimetres.

Author: Noah Stieler, 2023
"""

# TODO command status displayed on gui.

import serial
import time
from math import sqrt

wa_radius_measured = 120
wa_padding = 20
obj_radius = 20

_TIMEOUT = 1

_ser = None
is_origin_set = False

pos_x = 0
pos_y = 0


def connect(port: str, baud_rate: int) -> None:
    global _ser
    _ser = serial.Serial(port, baud_rate, timeout=_TIMEOUT)

    _ser.write('\r\n\r\n'.encode('utf-8'))
    time.sleep(2)
    _ser.flushInput()


def set_origin() -> None:
    """Sets the origin to be in centre of chamber."""
    _send_command('G90')  # Absolute positioning
    _send_command('G92 X0 Y0')  # Set origin point
    global is_origin_set, pos_x, pos_y
    is_origin_set = True
    pos_x = 0
    pos_y = 0


def set_position(new_x: float, new_y: float) -> bool:
    """Attempts to move to a new position. Returns false
    if position is outside working area."""
    global pos_x, pos_y

    wa_radius = wa_radius_measured - wa_padding - obj_radius
    new_mag = sqrt(pow(new_x, 2) + pow(new_y, 2))

    if new_mag < wa_radius:
        _send_command(f'G0 X{new_x} Y{new_y}')
        pos_x = new_x
        pos_y = new_y
        return True
    else:
        return False


def close() -> None:
    _ser.close()


def _send_command(cmd: str) -> None:
    _ser.write((cmd + '\n').encode('utf-8'))
    out = _ser.readlines()

    for item in out:
        item.decode()
    print(out)
