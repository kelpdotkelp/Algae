"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Part of the gui.
Sets up and handles the home tab.
Canvas is handled externally to enable graphics for multiple
experiments.

Only parameters ex. numeric, checkbox can be configured externally.
Output path and description fields experiment independent and so are
defined by default.

Author: Noah Stieler, 2023
"""

import tkinter as tk
import types
from tkinter import filedialog
import tkinter.ttk as ttk

from . import parameter

canvas = None
canvas_size = 0

_frame_parameter_box = None
_parameter_row_count = 0

_button_file = None

# Used when setting up a row of checkboxes
_column_count = 0
_new_frame = None


def add_parameter_num(display_name: str) -> parameter.InputItemNumber:
    global _parameter_row_count
    padding_x = 15
    padding_y = 10

    _frame_parameter_box.rowconfigure(index=_parameter_row_count, weight=1)

    new_frame = tk.Frame(_frame_parameter_box)
    new_frame.grid(row=_parameter_row_count, column=0, pady=padding_y, sticky='nsew')

    tk.Label(new_frame, text=display_name).pack(padx=padding_x, side=tk.LEFT)
    entry = tk.Entry(new_frame, justify=tk.RIGHT)
    entry.pack(padx=padding_x, side=tk.RIGHT)

    _parameter_row_count += 1

    return parameter.InputItemNumber(entry, display_name, 0)


def checkbox_row_begin():
    global _column_count, _new_frame
    _column_count = 0

    _frame_parameter_box.rowconfigure(index=_parameter_row_count, weight=1)

    _new_frame = tk.Frame(_frame_parameter_box)
    _new_frame.grid(row=_parameter_row_count, column=0, sticky='nsew')
    _new_frame.rowconfigure(index=0, weight=1)


def add_parameter_checkbox(display_name: str) -> parameter.InputItemBoolean:
    global _column_count
    frame_sub = tk.Frame(_new_frame)
    frame_sub.grid(row=0, column=_column_count)
    _new_frame.columnconfigure(index=_column_count, weight=1)

    tk.Label(frame_sub, text=display_name, justify=tk.LEFT).grid(row=0, column=0)
    checkbox = ttk.Checkbutton(frame_sub)
    checkbox.state(['!alternate'])
    checkbox.grid(row=0, column=1)

    _column_count += 1

    return parameter.InputItemBoolean(checkbox, display_name, 0)


def checkbox_row_end():
    global _parameter_row_count
    _parameter_row_count += 1


def create(frame_content_base: tk.Frame) -> tk.Frame:
    # Set up input and display frames
    frame_page_base = tk.Frame(frame_content_base)

    frame_input = tk.Frame(frame_page_base)
    frame_display = tk.Frame(frame_page_base)

    frame_page_base.rowconfigure(index=0, weight=1)
    frame_page_base.columnconfigure(index=0, weight=3)
    frame_page_base.columnconfigure(index=1, weight=4)
    frame_input.grid(row=0, column=0, sticky='nsew')
    frame_display.grid(row=0, column=1, sticky='nsew')

    # Add to frame_input
    frame_input.pack_propagate(False)

    #       Create widgets
    label_parameter = tk.Label(frame_input, text='Parameters',
                               background=frame_input['background'],
                               font=('Arial', 12))
    global _frame_parameter_box
    _frame_parameter_box = tk.Frame(frame_input, width=400, height=300,
                                    borderwidth=3, relief=tk.SUNKEN)
    label_output = tk.Label(frame_input, text='Output',
                            background=frame_input['background'],
                            font=('Arial', 12))
    frame_output_box = tk.Frame(frame_input, width=_frame_parameter_box['width'] - 30, height=85,
                                borderwidth=3, relief=tk.SUNKEN)

    #       Add to frame
    label_parameter.pack(padx=50, pady=(60, 10), anchor='w')
    _frame_parameter_box.pack(padx=50, anchor='w', fill=tk.X)
    label_output.pack(padx=50, pady=(25, 10), anchor='w')
    frame_output_box.pack(padx=50, anchor='w', fill=tk.X)

    """PARAMETERS"""
    _frame_parameter_box.grid_propagate(True)
    _frame_parameter_box.columnconfigure(index=0, weight=1)

    """OUTPUT"""
    frame_output_box.grid_propagate(True)
    frame_output_box.rowconfigure(index=1, weight=1)
    frame_output_box.columnconfigure(index=0, weight=1)

    # Output directory path
    display_name = 'Output directory path'
    label_odp = tk.Label(frame_output_box, text=display_name)
    label_odp.grid(row=0, column=0, padx=15, pady=5, sticky='w')

    frame_path = tk.Frame(frame_output_box)
    frame_path.grid_propagate(True)
    frame_path.grid(row=1, column=0, padx=15, pady=5, sticky='ew')
    frame_path.columnconfigure(index=0, weight=1)
    frame_path.rowconfigure(index=0, weight=1)

    entry_file_path = tk.Entry(frame_path)
    entry_file_path.grid(row=0, column=0, sticky='ew')
    parameter.input_dict['output_dir'] = \
        parameter.InputItemString(entry_file_path, display_name)

    global _button_file
    _button_file = ttk.Button(frame_path, text='. . .', width=5)
    _button_file.configure(command=_on_file_press)
    _button_file.grid(row=0, column=1)

    # Name
    display_name = 'Name'
    label_name = tk.Label(frame_output_box, text=display_name)
    label_name.grid(row=2, column=0, padx=15, pady=5, sticky='w')

    entry_name = tk.Entry(frame_output_box)
    entry_name.grid(row=3, column=0, padx=15, pady=5, sticky='ew')
    parameter.input_dict['output_name'] = \
        parameter.InputItemString(entry_name, display_name)

    # Description
    display_name = 'Description'
    label_desc = tk.Label(frame_output_box, text=display_name)
    label_desc.grid(row=4, column=0, padx=15, pady=5, sticky='w')

    entry_desc = tk.Entry(frame_output_box)
    entry_desc.grid(row=5, column=0, padx=15, pady=5, sticky='ew')
    parameter.input_dict['description'] = \
        parameter.InputItemString(entry_name, display_name)

    """CANVAS"""
    frame_display.pack_propagate(False)
    frame_display.bind('<Configure>', _canvas_resize)

    global canvas
    canvas = tk.Canvas(frame_display, background='white', highlightthickness=0,
                       borderwidth=3, relief=tk.SUNKEN)
    canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    return frame_page_base


def draw_canvas(draw_func: types.FunctionType) -> None:
    """Wrapper function for drawing to the canvas.
    Performs all the needed checks before drawing so draw_func
    only needs to code to render images."""

    # Crashes if updating canvas when not rendering it
    # ex. being on a different tab
    try:
        if canvas is not None and \
                canvas_size != 0 and \
                canvas.winfo_viewable():
            draw_func()
    except tk.TclError:  # Thrown when closing window
        pass


def _on_file_press() -> None:
    output_dir = filedialog.askdirectory()
    parameter.input_dict['output_dir'].set(output_dir)


def _canvas_resize(event) -> None:
    """Keeps the canvas square regardless of container dimensions."""
    pad = 50

    if canvas is None:
        return

    new_size = min(event.width, event.height)
    canvas.config(width=new_size - 2 * pad,
                  height=new_size - 2 * pad)
    global canvas_size
    canvas_size = new_size - 2 * pad
