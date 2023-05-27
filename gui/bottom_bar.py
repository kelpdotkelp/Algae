"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Part of the gui.
Sets up and handles the bottom task bar.

Author: Noah Stieler, 2023
"""

import tkinter as tk
import tkinter.ttk as ttk

_progress_bar = None
_label_message = None
_button_run, _button_stop = None, None


def create(frame_base):
    frame_base.rowconfigure(index=0, weight=1)
    frame_base.columnconfigure(index=0, weight=1)
    frame_base.columnconfigure(index=1, weight=0)

    frame_left = tk.Frame(frame_base)
    frame_right = tk.Frame(frame_base)

    frame_left.grid(row=0, column=0, sticky='nsew')
    frame_right.grid(row=0, column=1, sticky='nsew')

    global _progress_bar, _label_message
    _progress_bar = ttk.Progressbar(frame_left, orient=tk.HORIZONTAL,
                                    length=256, mode='determinate')
    _label_message = tk.Label(frame_left, text='')

    _progress_bar.pack(padx=25, side=tk.LEFT)
    _label_message.pack(side=tk.LEFT)

    frame_right.rowconfigure(index=0, weight=1)

    global _button_run, _button_stop
    _button_run = ttk.Button(frame_right, text='Run')
    _button_stop = ttk.Button(frame_right, text='Stop', state=tk.DISABLED)

    _button_run.grid(row=0, column=0, padx=15)
    _button_stop.grid(row=0, column=1, padx=15)


def message_display(message, color):
    _label_message.config(text=message, foreground=color)


def message_clear():
    _label_message.config(text='')


def on_button_run(function):
    _button_run.configure(command=function)


def on_button_stop(function):
    _button_stop.configure(command=function)


def toggle_button_stop():
    if _button_stop['state'] == tk.DISABLED:
        _button_stop['state'] = tk.ACTIVE
    else:
        _button_stop['state'] = tk.DISABLED


def progress_bar_set(value):
    """value ranges from 0 to 1"""
    _progress_bar['value'] = 100 * value
