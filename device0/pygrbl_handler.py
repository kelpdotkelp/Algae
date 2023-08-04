"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Handles pygrbl configuration and error handling.

Author: Noah Stieler, 2023
"""

from math import sqrt

import pygrbl
from gui.parameter import input_dict
import gui.bottom_bar

target_radius = 20  # Circular cross-section of target
chamber = None


def update_chamber():
    """Calculate the radius of the target and updates the chamber geometry from gui information. If the
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

    global chamber
    if chamber is None:
        chamber = pygrbl.ChamberCircle2D(0, 0, 0)

    chamber.radius = input_dict['wa_radius'].value
    chamber.padding = input_dict['wa_pad'].value
    chamber.target_radius = target_radius


def pygrbl_exception(e: pygrbl.PyGRBLException) -> None:
    """Handles exceptions thrown by pygrbl"""
    if type(e) is pygrbl.CommandException:
        gui.bottom_bar.message_display('GCODE error with command: ' + e.cmd, 'red')
    if type(e) is pygrbl.PointOutOfBoundsException:
        gui.bottom_bar.message_display('pygrbl attempted to move outside of bounds.', 'red')
    if type(e) is pygrbl.PyGRBLException:
        gui.bottom_bar.message_display('pygrbl raised an exception.', 'red')
