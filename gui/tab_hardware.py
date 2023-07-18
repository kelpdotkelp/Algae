"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Part of the gui.
Sets up and handles the hardware tab.

Author: Noah Stieler, 2023
"""
from .parameter import *
from .button import *
from .widgets import *
from . import style

target_selected = 'circular'
target_types = ('Circular', 'Rectangular')

position_gen_selected = 'random uniform'
position_gen_types = ('Random uniform', 'List')

_frame_hardware_box = None
_status_indicators = []
_hardware_count = 0

# Displays origin set status
_label_set_origin = None

# Holds target dimensions
_frame_target_type_base = None
_frame_circ, _frame_rect = None, None

# Holds position type information
_frame_position_gen_base = None
_frame_rand, _frame_list = None, None


def set_indicator(index: int, message: str, color: str) -> None:
    _status_indicators[index].configure(text=message, foreground=color)


def set_indicator_origin() -> None:
    _label_set_origin.configure(text='Origin set.', foreground='green')


def add_hardware(display_name: str, default_value: str = '',
                 action: bool = False, action_name: str = '') -> tuple:
    global _hardware_count
    _frame_hardware_box.rowconfigure(index=_hardware_count, weight=1)

    label = tk.Label(_frame_hardware_box, text=display_name)
    label.grid(row=_hardware_count, column=0, padx=style.padx_content, pady=style.pady_content, sticky='w')

    label = tk.Label(_frame_hardware_box, text='\tAddress: ')
    label.grid(row=_hardware_count, column=1, padx=style.padx_content, pady=style.pady_content, sticky='w')

    text = tk.StringVar()
    text.set(default_value)
    entry = tk.Entry(_frame_hardware_box, textvariable=text, width=40, justify=tk.RIGHT)
    entry.grid(row=_hardware_count, column=2, padx=style.padx_content, pady=style.pady_content)

    button = None
    if action:
        button = ttk.Button(_frame_hardware_box, text=action_name)
        button.grid(row=_hardware_count, column=3, padx=style.padx_content, pady=style.pady_content)
        button['state'] = tk.DISABLED

    _status_indicators.append(tk.Label(_frame_hardware_box, text=''))
    _status_indicators[_hardware_count].grid(row=_hardware_count, column=4,
                                             padx=style.padx_content, pady=style.pady_content)

    _hardware_count += 1

    input_item = InputItemString(entry, display_name)
    button_item = ButtonItem(button)
    if button is None:
        return input_item
    else:
        return input_item, button_item


def create(frame_content_base: tk.Frame) -> tk.Frame:
    frame_page_base = tk.Frame(frame_content_base)
    frame_page_base.rowconfigure(index=0, weight=1)
    frame_page_base.columnconfigure(index=0, weight=1)

    # Holds all widgets
    frame_hardware = tk.Frame(frame_page_base)
    frame_hardware.grid(padx=50, pady=25, row=0, column=0, sticky='new')

    insert_section(frame_hardware, 'Hardware Setup')

    global _frame_hardware_box
    _frame_hardware_box = tk.Frame(frame_hardware, width=400, height=300,
                                   borderwidth=3, relief=tk.SUNKEN)
    _frame_hardware_box.pack(anchor='w')

    frame_buttons = tk.Frame(frame_hardware)
    frame_buttons.rowconfigure(index=0, weight=1)
    frame_buttons.columnconfigure(index=1, weight=1)
    frame_buttons.pack(pady=style.pady_content, anchor='w')

    button_connect = ttk.Button(frame_buttons, text='Connect')
    button_connect.grid(row=0, column=0)
    button_dict['connect'] = ButtonItem(button_connect)

    button_dr = ttk.Button(frame_buttons, text='Display resources')
    button_dr.grid(row=0, column=1, padx=15)
    button_dict['disp_res'] = ButtonItem(button_dr)

    _create_positioning(frame_hardware)

    return frame_page_base


def _create_positioning(frame_hardware: tk.Frame) -> None:
    insert_section(frame_hardware, 'Positioning')

    frame_pos_box = tk.Frame(frame_hardware, width=400, height=300,
                             borderwidth=3, relief=tk.SUNKEN)
    frame_pos_box.columnconfigure(index=0, weight=1)
    frame_pos_box.rowconfigure(index=0, weight=1)
    frame_pos_box.pack(anchor='w')

    """SET ORIGIN"""
    frame_origin = tk.Frame(frame_pos_box)
    frame_origin.pack(anchor='w', padx=style.padx_content, pady=style.pady_content)

    global _label_set_origin
    _label_set_origin = tk.Label(frame_origin, text='',
                                 background=frame_pos_box['background'])
    _label_set_origin.grid(row=0, column=1, padx=20)

    button_so = ttk.Button(frame_origin, text='Set origin')
    button_so.grid(row=0, column=0)
    button_dict['set_origin'] = ButtonItem(button_so)

    """WORKING AREA"""
    insert_sub_header(frame_pos_box, 'Working area')
    widgets = insert_labeled_entry(frame_pos_box, ('Radius (mm)', 'Padding (mm)'))
    input_dict['wa_radius'] = InputItemNumber(widgets['entry'][0], 'Radius (mm)', 0)
    input_dict['wa_pad'] = InputItemNumber(widgets['entry'][1], 'Padding (mm)', 0)

    """TARGET TYPE"""
    insert_sub_header(frame_pos_box, 'Target type', target_types, _optionmenu_target_type)

    global _frame_target_type_base
    _frame_target_type_base = tk.Frame(frame_pos_box)
    _frame_target_type_base.pack(anchor='w')

    global _frame_circ
    widgets = insert_labeled_entry(_frame_target_type_base, ('Radius (mm)',))
    _frame_circ = widgets['frame_base']
    input_dict['target_radius'] = InputItemNumber(widgets['entry'][0], 'Radius (mm)', 0)

    global _frame_rect
    widgets = insert_labeled_entry(_frame_target_type_base, ('Length (mm)', 'Width (mm)'))
    _frame_rect = widgets['frame_base']
    input_dict['target_length'] = InputItemNumber(widgets['entry'][0], 'Length (mm)', 0)
    input_dict['target_width'] = InputItemNumber(widgets['entry'][1], 'Width (mm)', 0)

    _optionmenu_target_type('circular')

    """POSITION GENERATION"""
    insert_sub_header(frame_pos_box, 'Position type', position_gen_types, _optionmenu_position_type)

    global _frame_position_gen_base
    _frame_position_gen_base = tk.Frame(frame_pos_box)
    _frame_position_gen_base.pack(anchor='w')

    global _frame_rand
    widgets = insert_labeled_entry(_frame_position_gen_base, ('Number of positions',))
    _frame_rand = widgets['frame_base']
    input_dict['num_pos'] = InputItemNumber(widgets['entry'][0], 'Number of positions', 0)
    input_dict['num_pos'].set('0')

    global _frame_list
    widgets = insert_file_dialog(_frame_position_gen_base, 'Position list')
    _frame_list = widgets['frame_base']
    # TODO handle entry and button

    _optionmenu_position_type('random uniform')

def _optionmenu_target_type(*args) -> None:
    """Args is a tuple containing the selected option at index 0."""
    global target_selected
    target_selected = args[0].lower()

    if target_selected == 'circular':
        _frame_rect.pack_forget()
        _frame_circ.pack(anchor='w', padx=padx_content, pady=pady_content)
    elif target_selected == 'rectangular':
        _frame_circ.pack_forget()
        _frame_rect.pack(anchor='w', padx=pady_content, pady=pady_content)


def _optionmenu_position_type(*args) -> None:
    """Args is a tuple containing the selected option at index 0."""
    global position_gen_selected
    position_gen_selected = args[0].lower()

    if position_gen_selected == 'random uniform':
        _frame_list.pack_forget()
        _frame_rand.pack(anchor='w', padx=padx_content, pady=pady_content)
    elif position_gen_selected == 'list':
        _frame_rand.pack_forget()
        _frame_list.pack(anchor='w', padx=padx_content, pady=pady_content)
