"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Handles pygrbl configuration and error handling.

Author: Noah Stieler, 2023
"""
import pygrbl
import gui.bottom_bar


def pygrbl_exception(e: pygrbl.PyGRBLException) -> None:
    """Handles exceptions thrown by pygrbl"""
    if type(e) is pygrbl.CommandException:
        gui.bottom_bar.message_display('GCODE error with command: ' + e.cmd, 'red')
    if type(e) is pygrbl.PointOutOfBoundsException:
        gui.bottom_bar.message_display('pygrbl attempted to move outside of bounds.', 'red')
    if type(e) is pygrbl.PyGRBLException:
        gui.bottom_bar.message_display('pygrbl raised an exception.', 'red')
