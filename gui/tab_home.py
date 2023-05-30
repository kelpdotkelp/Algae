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
from tkinter import filedialog
import tkinter.ttk as ttk

canvas = None
canvas_size = 0

_frame_parameter_box = None
_parameter_row_count = 0

_entry_file_path = None
_button_file = None
_text_desc = None


def add_parameter_num(display_name):
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

    return entry


def add_parameter_checkbox(display_name_list):
    global _parameter_row_count

    _frame_parameter_box.rowconfigure(index=_parameter_row_count, weight=1)

    new_frame = tk.Frame(_frame_parameter_box)
    new_frame.grid(row=_parameter_row_count, column=0, sticky='nsew')
    new_frame.rowconfigure(index=0, weight=1)

    checkbox_list = {}
    for i in range(len(display_name_list)):
        frame_sub = tk.Frame(new_frame)
        frame_sub.grid(row=0, column=i)
        new_frame.columnconfigure(index=i, weight=1)

        tk.Label(frame_sub, text=display_name_list[i], justify=tk.LEFT).grid(row=0, column=0)
        checkbox_list[display_name_list[i]] = [ttk.Checkbutton(frame_sub), 0]  # index 1 is checkbutton value
        checkbox_list[display_name_list[i]][0].state(['!alternate'])
        checkbox_list[display_name_list[i]][0].grid(row=0, column=1)

    _parameter_row_count += 1

    return checkbox_list


def create(frame_content_base):
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
    label_odp = tk.Label(frame_output_box, text='Output directory path')
    label_odp.grid(row=0, column=0, padx=15, pady=5, sticky='w')

    frame_path = tk.Frame(frame_output_box)
    frame_path.grid_propagate(True)
    frame_path.grid(row=1, column=0, padx=15, pady=5, sticky='ew')
    frame_path.columnconfigure(index=0, weight=1)
    frame_path.rowconfigure(index=0, weight=1)

    global _entry_file_path, _button_file
    _entry_file_path = tk.Entry(frame_path)
    _entry_file_path.grid(row=0, column=0, sticky='ew')

    _button_file = ttk.Button(frame_path, text='. . .', width=5)
    _button_file.configure(command=_on_file_press)
    _button_file.grid(row=0, column=1)

    # Description
    label_desc = tk.Label(frame_output_box, text='Description')
    label_desc.grid(row=2, column=0, padx=15, pady=5, sticky='w')

    global _text_desc
    _text_desc = tk.Entry(frame_output_box)
    _text_desc.grid(row=3, column=0, padx=15, pady=5, sticky='ew')

    """CANVAS"""
    frame_display.pack_propagate(False)
    frame_display.bind('<Configure>', _canvas_resize)

    global canvas
    canvas = tk.Canvas(frame_display, background='white', highlightthickness=0,
                       borderwidth=3, relief=tk.SUNKEN)
    canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    return frame_page_base


def get_output_dir():
    return _entry_file_path.get()


def get_description():
    return _text_desc.get()


def draw_canvas(draw_func):
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


def _on_file_press():
    output_dir = filedialog.askdirectory()
    text = tk.StringVar()
    text.set(output_dir)
    _entry_file_path.config(textvariable=text)


def _canvas_resize(event):
    """Keeps the canvas square regardless of container dimensions."""
    pad = 50

    if canvas is None:
        return

    new_size = min(event.width, event.height)
    canvas.config(width=new_size - 2 * pad,
                  height=new_size - 2 * pad)
    global canvas_size
    canvas_size = new_size - 2 * pad
