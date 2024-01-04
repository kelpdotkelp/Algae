"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Sets up GUI positioning frame.

Author: Noah Stieler, 2023
"""
from tkinter import filedialog

from gui import style
from gui.widgets import *
from gui.parameter import *
from gui.button import *
import gui.tab_hardware


def custom_position_box(_frame_pos_box: tk.Frame):
    """SET ORIGIN"""
    frame_origin = tk.Frame(_frame_pos_box)
    frame_origin.pack(anchor='w', padx=style.padx_content, pady=style.pady_content)

    gui.tab_hardware._label_set_origin = tk.Label(frame_origin, text='',
                                 background=_frame_pos_box['background'])
    gui.tab_hardware._label_set_origin.grid(row=0, column=1, padx=20)

    button_so = ttk.Button(frame_origin, text='Set origin')
    button_so.grid(row=0, column=0)
    button_dict['set_origin'] = ButtonItem(button_so)

    """WORKING AREA"""
    insert_sub_header(_frame_pos_box, 'Working area')
    widgets = insert_labeled_entry(_frame_pos_box, ('Radius (mm)', 'Height (mm)', 'Padding (mm)'))
    input_dict['wa_radius'] = InputItemNumber(widgets['entry'][0], 'Radius (mm)', 0)
    input_dict['wa_height'] = InputItemNumber(widgets['entry'][1], 'Height (mm)', 0)
    input_dict['wa_pad'] = InputItemNumber(widgets['entry'][2], 'Padding (mm)', 0)

    """TARGET"""
    insert_sub_header(_frame_pos_box, 'Target')
    widgets = insert_labeled_entry(_frame_pos_box, ('Radius (mm)',))
    input_dict['target_radius'] = InputItemNumber(widgets['entry'][0], 'Radius (mm)', 0)

    """POSITION"""
    insert_sub_header(_frame_pos_box, 'Position type')
    widgets = insert_file_dialog(_frame_pos_box, 'Position list')
    button_dict['fd_pos_list'] = ButtonItem(widgets['button'])
    button_dict['fd_pos_list'].command(_open_file_dialog_pos_list)
    input_dict['pos_list_path'] = InputItemString(widgets['entry'], 'Position list', '')


def _open_file_dialog_pos_list() -> None:
    pos_list_dir = filedialog.askopenfilename()
    input_dict['pos_list_path'].set(pos_list_dir)
