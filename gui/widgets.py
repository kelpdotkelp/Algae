"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Part of the gui.
Provides functions that insert compound, styled widgets.
Used for items like labeled entry boxes,
sub-headers, sub-headers with option menus. Other parts of the gui still implement
unique functionality.

Author: Noah Stieler, 2023
"""
import tkinter as tk
import tkinter.ttk as ttk
import types

from .style import *


def insert_section(frame_base: tk.Frame, name: str, pack_side: int = tk.TOP) -> None:
    label_hardware = tk.Label(frame_base, text=name,
                              background=frame_base['background'],
                              font=font_h1)
    label_hardware.pack(pady=(pady_section_top, pady_content), anchor='w', side=pack_side)


def insert_sub_header(frame_content: tk.Frame, name: str,
                      om_items: tuple = None, om_changed: types.FunctionType = None) -> None:
    """Inserts a header into a tkinter frame. An optionmenu can be included beside the text."""
    frame_base = tk.Frame(frame_content)
    frame_base.pack(anchor='w', padx=padx_content, pady=0)
    frame_base.rowconfigure(index=0, weight=1)

    label_name = tk.Label(frame_base, text=name, justify=tk.LEFT,
                          font=font_h0)
    label_name.grid(row=0, column=0)

    if om_items is not None and om_changed is not None:
        optionmenu_var = tk.StringVar()
        optionmenu = ttk.OptionMenu(frame_base, optionmenu_var,
                                    om_items[0], *om_items, command=om_changed)
        optionmenu.grid(row=0, column=1)


def insert_labeled_entry(frame_content: tk.Frame, names: tuple) -> dict:
    """Inserts labeled entry boxes in a row. Returns a dict containing
    the new frame and a list of tk.Entry for each name provided."""
    frame_base = tk.Frame(frame_content)
    frame_base.pack(anchor='w', padx=padx_content, pady=pady_content)

    output = {'frame_base': frame_base, 'entry': []}

    for i in range(len(names)):
        label_name = tk.Label(frame_base, text=names[i] + '\t')
        label_name.grid(row=0, column=2 * i, sticky='w')
        entry = tk.Entry(frame_base, justify=tk.RIGHT)
        entry.grid(row=0, column=2 * i + 1, sticky='e', padx=padx_content)
        output['entry'].append(entry)

    return output


def insert_labeled_entry_long(frame_content: tk.Frame, name: str) -> dict:
    """Inserts a label with a larger entry box below it. Returns a dict containing
    the new frame and entry."""
    entry_width = 45

    frame_base = tk.Frame(frame_content)
    frame_base.pack(anchor='w', padx=padx_content, pady=pady_content)

    output = {'frame_base': frame_base, 'entry': []}

    label_name = tk.Label(frame_base, text=name)
    label_name.pack(anchor='w')
    entry = tk.Entry(frame_base, width=entry_width)
    entry.pack(anchor='w', pady=(pady_content, 0), expand=True, fill=tk.X)
    output['entry'] = entry

    return output


def insert_file_dialog(frame_content: tk.Frame, name: str) -> dict:
    """Inserts a label with a larger entry box and side button below it. Returns a dict containing
    the new frame and entry."""
    entry_width = 40

    frame_base = tk.Frame(frame_content)
    frame_base.pack(anchor='w', padx=padx_content, pady=pady_content)

    output = {'frame_base': frame_base, 'entry': [], 'button': []}

    label_name = tk.Label(frame_base, text=name)
    label_name.pack(anchor='w')

    frame_entry = tk.Frame(frame_base)
    frame_entry.pack(anchor='w')
    entry = tk.Entry(frame_entry, width=entry_width)
    entry.pack(anchor='w', pady=(pady_content, 0), side=tk.LEFT)
    output['entry'] = entry

    button = ttk.Button(frame_entry, text='. . .', width=5)
    button.pack(anchor='w', pady=(pady_content, 0), side=tk.LEFT)
    output['button'] = button

    return output
