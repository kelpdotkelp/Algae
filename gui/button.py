"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Part of the gui.
Maintains an updated dictionary of all buttons.

Author: Noah Stieler, 2023
"""
import tkinter as tk
import tkinter.ttk as ttk
import types
from dataclasses import dataclass

button_dict = {}


@dataclass
class ButtonItem:
    widget: ttk.Button

    def command(self, function: types.FunctionType) -> None:
        self.widget.configure(command=function)

    def toggle_state(self) -> None:
        if str(self.widget['state']) == tk.DISABLED:
            self.widget['state'] = tk.ACTIVE
        else:
            self.widget['state'] = tk.DISABLED

    def set_state(self, state: int) -> None:
        if state == 0:
            self.widget['state'] = tk.DISABLED
        elif state == 1:
            self.widget['state'] = tk.ACTIVE
