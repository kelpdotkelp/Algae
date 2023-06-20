"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Part of the gui.
Sets up and handles the hardware tab.

Author: Noah Stieler, 2023
"""

import tkinter as tk
import tkinter.ttk as ttk
import types

from . import parameter

_frame_hardware_box = None
_status_indicators = []
_button_hw_scan, _button_c_connect = None, None
_button_set_origin = None
_hardware_count = 0


def add_hardware(display_name: str, default_value: str = '',
                 action: bool = False, action_name: str = '') -> tuple:
    global _hardware_count
    padding_x = 7
    padding_y = 10

    _frame_hardware_box.rowconfigure(index=_hardware_count, weight=1)

    label = tk.Label(_frame_hardware_box, text=display_name)
    label.grid(row=_hardware_count, column=0, padx=padding_x, pady=padding_y, sticky='w')

    label = tk.Label(_frame_hardware_box, text='\tAddress: ')
    label.grid(row=_hardware_count, column=1, padx=padding_x, pady=padding_y, sticky='w')

    text = tk.StringVar()
    text.set(default_value)
    entry = tk.Entry(_frame_hardware_box, textvariable=text, width=40, justify=tk.RIGHT)
    entry.grid(row=_hardware_count, column=2, padx=padding_x, pady=padding_y)

    button = None
    if action:
        button = ttk.Button(_frame_hardware_box, text=action_name)
        button.grid(row=_hardware_count, column=3, padx=padding_x, pady=padding_y)
        button['state'] = tk.DISABLED

    _status_indicators.append(tk.Label(_frame_hardware_box, text=''))
    _status_indicators[_hardware_count].grid(row=_hardware_count, column=4, padx=padding_x, pady=padding_y)

    _hardware_count += 1

    input_item = parameter.InputItemString(entry, display_name)
    if button is None:
        return input_item
    else:
        return input_item, button


def create(frame_content_base: tk.Frame) -> tk.Frame:
    pady_head = 15
    pady = 10

    frame_page_base = tk.Frame(frame_content_base)
    frame_page_base.rowconfigure(index=0, weight=1)
    frame_page_base.columnconfigure(index=0, weight=1)

    # Holds all widgets
    frame_hardware = tk.Frame(frame_page_base)
    frame_hardware.grid(padx=50, pady=25, row=0, column=0, sticky='new')

    label_hardware = tk.Label(frame_hardware, text='Hardware Setup',
                              background=frame_hardware['background'],
                              font=('Arial', 12))
    label_hardware.pack(pady=(pady_head, pady), anchor='w')

    global _frame_hardware_box
    _frame_hardware_box = tk.Frame(frame_hardware, width=400, height=300,
                                   borderwidth=3, relief=tk.SUNKEN)
    _frame_hardware_box.pack(anchor='w')

    frame_buttons = tk.Frame(frame_hardware)
    frame_buttons.rowconfigure(index=0, weight=1)
    frame_buttons.columnconfigure(index=1, weight=1)
    frame_buttons.pack(pady=pady, anchor='w')

    global _button_hw_scan, _button_c_connect
    _button_hw_scan = ttk.Button(frame_buttons, text='Connect')
    _button_c_connect = ttk.Button(frame_buttons, text='Display resources')

    _button_hw_scan.grid(row=0, column=0)
    _button_c_connect.grid(row=0, column=1, padx=15)

    _create_positioning(frame_hardware)

    return frame_page_base


def _create_positioning(frame_hardware: tk.Frame) -> None:
    global _button_set_origin
    pady_head = 15
    pady = 10
    padx = 7

    label_hardware = tk.Label(frame_hardware, text='Positioning',
                              background=frame_hardware['background'],
                              font=('Arial', 12))
    label_hardware.pack(pady=(pady_head, pady), anchor='w')

    frame_pos_box = tk.Frame(frame_hardware, width=400, height=300,
                             borderwidth=3, relief=tk.SUNKEN)
    frame_pos_box.columnconfigure(index=0, weight=1)
    frame_pos_box.rowconfigure(index=0, weight=1)
    frame_pos_box.pack(anchor='w')

    # Set origin
    frame_origin = tk.Frame(frame_pos_box)
    frame_origin.pack(anchor='w', padx=padx, pady=pady)
    label_set_origin = tk.Label(frame_origin, text='Origin set.',
                                background=frame_pos_box['background'])
    _button_set_origin = ttk.Button(frame_origin, text='Set origin')
    _button_set_origin.grid(row=0, column=0)
    label_set_origin.grid(row=0, column=1)

    # Select target type
    frame_type = tk.Frame(frame_pos_box)
    frame_type.pack(anchor='w', padx=padx, pady=pady)
    frame_type.rowconfigure(index=0, weight=1)

    label_target_type = tk.Label(frame_type, text='Target type:\t', justify=tk.LEFT)
    label_target_type.grid(row=0, column=0)


def on_connect(function: types.FunctionType) -> None:
    _button_hw_scan.configure(command=function)


def on_display_resources(function: types.FunctionType) -> None:
    _button_c_connect.configure(command=function)


def set_indicator(index: int, message: str, color: str) -> None:
    _status_indicators[index].configure(text=message, foreground=color)
