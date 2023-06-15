"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Part of the gui.
Handles initial window to select which device to control.

Author: Noah Stieler, 2023
"""

import tkinter as tk
import tkinter.ttk as ttk
import types

_ASPECT_RATIO = 4 / 3
_HEIGHT = 450
_WIDTH = int(_ASPECT_RATIO * _HEIGHT)

app_terminated = False
_root = None
_frame_base = None


def create_gui() -> None:
    _create_window()

    global _frame_base
    _frame_base = tk.Frame(_root)
    _frame_base.pack(expand=True, fill=tk.BOTH, padx=15, pady=15)

    label = tk.Label(_frame_base, text='Please select a device: ',
                     background=_frame_base['background'],
                     font=('Arial', 12))
    label.pack(anchor='w')


def add_device(func_on_press: types.FunctionType,
               display_name: str = 'Device') -> None:
    def transition() -> None:
        _on_closing()
        func_on_press()

    button = ttk.Button(_frame_base, text=display_name, command=transition)
    button.pack(pady=8, fill=tk.X)


def update() -> None:
    _root.update_idletasks()
    _root.update()


def _create_window() -> None:
    """Creates main application window."""
    global _root

    _root = tk.Tk()
    _root.minsize(_WIDTH, _HEIGHT)
    _root.resizable(False, False)
    _root.title('Algae')
    _root.geometry(f'{_WIDTH}x{_HEIGHT}+50+50')
    _root.protocol('WM_DELETE_WINDOW', _on_closing)

    icon = tk.PhotoImage(file='./res/icon_titlebar.png')
    _root.iconphoto(True, icon)


def _on_closing() -> None:
    _root.destroy()
    global app_terminated
    app_terminated = True
