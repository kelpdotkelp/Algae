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


@dataclass
class InputItem:
    widget: Widget
    name: str


@dataclass
class InputItemNumber(InputItem):
    value: float

    def update(self) -> None:
        self.value = self.widget.get()
        try:
            self.value = float(self.value)
        except ValueError:
            self.value = float('inf')


@dataclass
class InputItemString(InputItem):
    value: str = ''

    def update(self) -> None:
        self.value = self.widget.get()

    def set(self, text: str) -> None:
        tk_text = tkinter.StringVar()
        tk_text.set(text)
        self.widget.config(text=tk_text)


@dataclass
class InputItemBoolean(InputItem):
    value: bool

    def update(self) -> None:
        if 'selected' in self.widget.state():
            self.value = 1
        else:
            self.value = 0

    def toggle(self) -> None:
        self.widget.invoke()


def update() -> None:
    """Gets data from the tkinter widgets and
    updates all the parameters. For numeric entries,
    if the input is invalid, the parameter is set to inf.
    This will correctly throw an error when checking parameters."""
    try:
        for key in input_dict:
            input_dict[key].update()
    except tkinter.TclError:
        pass
