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

from tkinter import filedialog

from . import parameter
from .widgets import *
from .button import *

canvas = None
canvas_size = 0

_frame_parameter_box = None
_parameter_row_count = 0

# Used when setting up a row of checkboxes
_column_count = 0
_new_frame = None


def add_parameter_num(display_name: str) -> parameter.InputItemNumber:
    global _parameter_row_count
    _frame_parameter_box.rowconfigure(index=_parameter_row_count, weight=1)

    new_frame = tk.Frame(_frame_parameter_box)
    new_frame.grid(row=_parameter_row_count, column=0, pady=pady_content, sticky='nsew')

    tk.Label(new_frame, text=display_name).pack(padx=padx_content, side=tk.LEFT)
    entry = tk.Entry(new_frame, justify=tk.RIGHT)
    entry.pack(padx=padx_content, side=tk.RIGHT)

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
    frame_input.grid(row=0, column=0, padx=50, pady=(pady_section_top, pady_content), sticky='nsew')
    frame_display.grid(row=0, column=1, sticky='nsew')

    # Add to frame_input
    frame_input.pack_propagate(False)

    insert_section(frame_input, 'Parameters')

    global _frame_parameter_box
    _frame_parameter_box = tk.Frame(frame_input, width=400, height=300,
                                    borderwidth=3, relief=tk.SUNKEN)
    _frame_parameter_box.grid_propagate(True)
    _frame_parameter_box.columnconfigure(index=0, weight=1)
    _frame_parameter_box.pack(anchor='w', fill=tk.X)

    insert_section(frame_input, 'Output')

    frame_output_box = tk.Frame(frame_input, borderwidth=3, relief=tk.SUNKEN)
    frame_output_box.pack(anchor='w')

    # Output directory path
    widgets = insert_file_dialog(frame_output_box, 'Output directory path')
    parameter.input_dict['output_dir'] = \
        parameter.InputItemString(widgets['entry'], 'Output directory path')
    button_dict['file_exp'] = ButtonItem(widgets['button'])
    button_dict['file_exp'].command(_on_file_press)

    # Name
    widgets = insert_labeled_entry_long(frame_output_box, 'Name')
    parameter.input_dict['output_name'] = \
        parameter.InputItemString(widgets['entry'], 'Name')

    # Description
    widgets = insert_labeled_entry_long(frame_output_box, 'Description')
    parameter.input_dict['description'] = \
        parameter.InputItemString(widgets['entry'], 'Description')

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
