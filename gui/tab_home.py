import tkinter as tk

canvas = None
canvas_size = 0

_frame_parameter_box = None
_parameter_count = 0


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


def add_parameter(display_name):
    global _parameter_count
    padding_x = 15
    padding_y = 10

    _frame_parameter_box.rowconfigure(index=_parameter_count, weight=1)

    new_frame = tk.Frame(_frame_parameter_box)
    new_frame.grid(row=_parameter_count, column=0, pady=padding_y, sticky='nsew')

    tk.Label(new_frame, text=display_name).pack(padx=padding_x, side=tk.LEFT)
    entry = tk.Entry(new_frame)
    entry.pack(padx=padding_x, side=tk.RIGHT)

    _parameter_count += 1

    return entry


def create(frame_content_base):
    frame_page_base = tk.Frame(frame_content_base)

    frame_parameter = tk.Frame(frame_page_base)
    frame_display = tk.Frame(frame_page_base)

    frame_page_base.rowconfigure(index=0, weight=1)
    frame_page_base.columnconfigure(index=0, weight=3)
    frame_page_base.columnconfigure(index=1, weight=4)
    frame_parameter.grid(row=0, column=0, sticky='nsew')
    frame_display.grid(row=0, column=1, sticky='nsew')

    """PARAMETERS"""
    frame_parameter.pack_propagate(False)

    label_parameter = tk.Label(frame_parameter, text='Parameters',
                               background=frame_parameter['background'],
                               font=('Arial', 12))
    label_parameter.pack(padx=50, pady=(60, 10), anchor='w')

    global _frame_parameter_box
    _frame_parameter_box = tk.Frame(frame_parameter, width=400, height=300,
                                    borderwidth=3, relief=tk.SUNKEN)
    _frame_parameter_box.grid_propagate(True)
    _frame_parameter_box.columnconfigure(index=0, weight=1)
    _frame_parameter_box.pack(padx=50, anchor='w')

    """CANVAS"""
    frame_display.pack_propagate(False)
    frame_display.bind('<Configure>', _canvas_resize)

    global canvas
    canvas = tk.Canvas(frame_display, background='white', highlightthickness=0,
                       borderwidth=3, relief=tk.SUNKEN)
    canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    return frame_page_base
