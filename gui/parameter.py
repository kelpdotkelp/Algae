"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Part of the gui.
Maintains a dictionaries of all gui input.

Author: Noah Stieler, 2023
"""
import tkinter
from tkinter import Widget
from dataclasses import dataclass

input_dict = {}
checkbox_dict = {}


@dataclass
class InputItem:
    widget: Widget
    name: str


@dataclass
class InputItemNumber(InputItem):
    value: float


@dataclass
class InputItemBoolean(InputItem):
    value: bool


def update():
    """Gets data from the tkinter widgets and
    updates all the parameters. For numeric entries,
    if the input is invalid, the parameter is set to inf.
    This will correctly throw an error when checking parameters."""
    try:
        for key in input_dict:
            input_dict[key].value = input_dict[key].widget.get()

            if type(input_dict[key]) is InputItemNumber:
                try:
                    input_dict[key].value = float(input_dict[key].value)
                except ValueError:
                    input_dict[key].value = float('inf')

        for key in checkbox_dict:
            if 'selected' in checkbox_dict[key].widget.state():
                checkbox_dict[key].value = 1
            else:
                checkbox_dict[key].value = 0
    except tkinter.TclError:
        pass
