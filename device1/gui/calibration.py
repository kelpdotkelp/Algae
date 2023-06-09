"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Extension of gui to enable selection of a VNA calibration.

Author: Noah Stieler, 2023
"""

import tkinter as tk
import tkinter.ttk as ttk

on_apply_calib = None
cal_list = []

_root = None
_listbox = None


def create_popup():
    """Creates listbox window."""
    global _root, _listbox
    _root = tk.Tk()
    _root.resizable(False, False)
    _root.title('Select Calibration')
    _root.geometry(f'{650}x{200}+50+50')
    _root.protocol('WM_DELETE_WINDOW', _on_closing)

    _root.rowconfigure(index=0, weight=0)
    _root.rowconfigure(index=1, weight=0)
    _root.columnconfigure(index=0, weight=1)

    frame = tk.Frame(_root)

    scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL)

    _listbox = tk.Listbox(frame, height=6, yscrollcommand=scroll.set)
    for i in range(len(cal_list)):
        _listbox.insert(i, cal_list[i])

    scroll.config(command=_listbox.yview)

    _listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    button = ttk.Button(_root, text='Apply')

    if on_apply_calib is not None:
        button.configure(command=_on_closing_button)

    frame.grid(row=0, column=0, padx=20, pady=10, sticky='nsew')
    button.grid(row=1, column=0, padx=20, pady=10, sticky='e')


def get_selected():
    """Returns the selected listbox entry."""
    if _listbox.curselection() is not ():
        return cal_list[_listbox.curselection()[0]]
    else:
        return ''


def _on_closing():
    global _root, _listbox
    _root.destroy()
    _root = None
    _listbox = None


def _on_closing_button():
    on_apply_calib()
    _on_closing()
