"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Part of the gui.
Sets up and handles the bottom task bar.

Author: Noah Stieler, 2023
"""
from gui.button import *

enable_button_stop = True

progress_bar = None
_label_message = None


def create(frame_base: tk.Frame) -> None:
    frame_base.rowconfigure(index=0, weight=1)
    frame_base.columnconfigure(index=0, weight=1)
    frame_base.columnconfigure(index=1, weight=0)

    frame_left = tk.Frame(frame_base)
    frame_right = tk.Frame(frame_base)

    frame_left.grid(row=0, column=0, sticky='nsew')
    frame_right.grid(row=0, column=1, sticky='nsew')

    global progress_bar, _label_message
    progress_bar = ttk.Progressbar(frame_left, orient=tk.HORIZONTAL,
                                   length=256, mode='determinate')
    _label_message = tk.Label(frame_left, text='')

    progress_bar.pack(padx=25, side=tk.LEFT)
    _label_message.pack(side=tk.LEFT)

    frame_right.rowconfigure(index=0, weight=1)

    button_run = ttk.Button(frame_right, text='Run')
    button_stop = ttk.Button(frame_right, text='Stop', state=tk.DISABLED)
    button_run.grid(row=0, column=0, padx=15)
    if enable_button_stop:
        button_stop.grid(row=0, column=1, padx=15)

    button_dict['run'] = ButtonItem(button_run)
    button_dict['stop'] = ButtonItem(button_stop)


def message_display(message: str, color: str) -> None:
    _label_message.config(text=message, foreground=color)


def message_clear() -> None:
    _label_message.config(text='')


def progress_bar_set(value) -> None:
    """value ranges from 0 to 1"""
    progress_bar['value'] = 100 * value
