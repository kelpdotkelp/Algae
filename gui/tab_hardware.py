"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Part of the gui.
Sets up and handles the hardware tab.

Author: Noah Stieler, 2023
"""
from .parameter import *
from .button import *

target_selected = 'circular'
target_types = ('Circular', 'Rectangular')

_frame_hardware_box = None
_status_indicators = []
_hardware_count = 0

# Holds target dimensions
_frame_circ, _frame_rect = None, None
_label_set_origin = None


def set_indicator(index: int, message: str, color: str) -> None:
    _status_indicators[index].configure(text=message, foreground=color)


def set_indicator_origin() -> None:
    _label_set_origin.configure(text='Origin set.', foreground='green')


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

    input_item = InputItemString(entry, display_name)
    button_item = ButtonItem(button)
    if button is None:
        return input_item
    else:
        return input_item, button_item


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

    button_connect = ttk.Button(frame_buttons, text='Connect')
    button_connect.grid(row=0, column=0)
    button_dict['connect'] = ButtonItem(button_connect)

    button_dr = ttk.Button(frame_buttons, text='Display resources')
    button_dr.grid(row=0, column=1, padx=15)
    button_dict['disp_res'] = ButtonItem(button_dr)

    _create_positioning(frame_hardware)

    return frame_page_base


def _create_positioning(frame_hardware: tk.Frame) -> None:
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

    global _label_set_origin
    _label_set_origin = tk.Label(frame_origin, text='',
                                 background=frame_pos_box['background'])
    _label_set_origin.grid(row=0, column=1, padx=20)

    button_so = ttk.Button(frame_origin, text='Set origin')
    button_so.grid(row=0, column=0)
    button_dict['set_origin'] = ButtonItem(button_so)

    # Working area
    label_wa = tk.Label(frame_pos_box, text='Working area', justify=tk.LEFT)
    label_wa.pack(anchor='w', padx=padx, pady=pady)

    frame_wa = tk.Frame(frame_pos_box)
    frame_wa.pack(anchor='w', padx=padx, pady=pady)

    label_radius = tk.Label(frame_wa, text='Radius (mm)\t')
    label_radius.grid(row=0, column=0, sticky='w')
    entry_radius = tk.Entry(frame_wa, justify=tk.RIGHT)
    entry_radius.grid(row=0, column=1, sticky='e', padx=7)
    input_dict['wa_radius'] = InputItemNumber(entry_radius, 'Radius (mm)', 0)

    label_pad = tk.Label(frame_wa, text='Padding (mm)\t')
    label_pad.grid(row=0, column=2, sticky='w')
    entry_pad = tk.Entry(frame_wa, justify=tk.RIGHT)
    entry_pad.grid(row=0, column=3, sticky='e', padx=7)
    input_dict['wa_pad'] = InputItemNumber(entry_pad, 'Padding (mm)', 0)

    # Number of positions
    frame_pos = tk.Frame(frame_pos_box)
    frame_pos.pack(anchor='w', padx=padx, pady=pady)

    label_pos = tk.Label(frame_pos, text='Number of positions\t')
    label_pos.grid(row=0, column=0, sticky='w')
    entry_pos = tk.Entry(frame_pos, justify=tk.RIGHT)
    entry_pos.grid(row=0, column=1, sticky='e', padx=7)
    input_dict['num_pos'] = InputItemNumber(entry_pos, 'Number of positions', 0)
    input_dict['num_pos'].set('0')

    # Select target type
    frame_type = tk.Frame(frame_pos_box)
    frame_type.pack(anchor='w', padx=padx, pady=pady)
    frame_type.rowconfigure(index=0, weight=1)

    label_target_type = tk.Label(frame_type, text='Target type ', justify=tk.LEFT)
    label_target_type.grid(row=0, column=0)

    optionmenu_var = tk.StringVar()
    optionmenu = ttk.OptionMenu(frame_type, optionmenu_var,
                                target_types[0], *target_types, command=_optionmenu_changed)
    optionmenu.grid(row=0, column=1)

    # Target specs
    global _frame_circ
    _frame_circ = tk.Frame(frame_pos_box)
    _frame_circ.rowconfigure(index=0, weight=1)

    label_radius = tk.Label(_frame_circ, text='Radius (mm)\t')
    label_radius.grid(row=0, column=0, sticky='w')
    entry_radius = tk.Entry(_frame_circ, justify=tk.RIGHT)
    entry_radius.grid(row=0, column=1, sticky='e', padx=7)
    input_dict['target_radius'] = InputItemNumber(entry_radius, 'Radius (mm)', 0)

    global _frame_rect
    _frame_rect = tk.Frame(frame_pos_box)
    _frame_rect.rowconfigure(index=0, weight=1)

    label_l = tk.Label(_frame_rect, text='Length (mm)\t')
    label_l.grid(row=0, column=0, sticky='w')
    entry_l = tk.Entry(_frame_rect, justify=tk.RIGHT)
    entry_l.grid(row=0, column=1, sticky='e', padx=7)
    input_dict['target_length'] = InputItemNumber(entry_l, 'Length (mm)', 0)

    label_w = tk.Label(_frame_rect, text='Width (mm)\t')
    label_w.grid(row=0, column=2, sticky='w')
    entry_w = tk.Entry(_frame_rect, justify=tk.RIGHT)
    entry_w.grid(row=0, column=3, sticky='e', padx=7)
    input_dict['target_width'] = InputItemNumber(entry_w, 'Width (mm)', 0)

    _optionmenu_changed('circular')


def _optionmenu_changed(*args) -> None:
    """Args is a tuple containing the selected option at index 0."""
    global target_selected
    target_selected = args[0].lower()

    if target_selected == 'circular':
        _frame_rect.pack_forget()
        _frame_circ.pack(anchor='w', padx=7, pady=10)
    elif target_selected == 'rectangular':
        _frame_circ.pack_forget()
        _frame_rect.pack(anchor='w', padx=7, pady=10)
