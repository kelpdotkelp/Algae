"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Provides error checking on user input.

Author: Noah Stieler, 2023
"""

import os.path

import gui
from gui.parameter import input_dict
from .imaging import VNA
from pygrbl import PyGRBLMachine


def input_validate(vna: VNA, grbl_machine: PyGRBLMachine) -> bool:
    """Checks all user input for errors/invalid entries"""
    check_list = ['num_points', 'ifbw', 'freq_start', 'freq_stop']

    for item in check_list:
        if not (vna.p_ranges[item][0] <= input_dict[item].value <= vna.p_ranges[item][1]):
            gui.bottom_bar.message_display('\"' + input_dict[item].name + f'\" must be in range: ' +
                                           str(vna.p_ranges[item]), 'red')
            return False
    if not (input_dict['freq_stop'].value > input_dict['freq_start'].value):
        gui.bottom_bar.message_display('Start frequency must be less than stop frequency.', 'red')
        return False
    elif not os.path.isdir(input_dict['output_dir'].value):
        gui.bottom_bar.message_display('Invalid output directory.', 'red')
        return False

    """     IF POSITIONING IS ENABLED
    """
    if input_dict['cnc_enable'].value:
        if not grbl_machine.origin_set:
            gui.bottom_bar.message_display('CNC origin has not been set.', 'red')
            return False
        elif not (1 <= input_dict['wa_radius'].value < float('inf')):
            gui.bottom_bar.message_display('Invalid working area radius.', 'red')
            return False
        elif not (1 <= input_dict['wa_height'].value < float('inf')):
            gui.bottom_bar.message_display('Invalid working area height.', 'red')
            return False
        elif not (1 <= input_dict['wa_pad'].value < float('inf')):
            gui.bottom_bar.message_display('Invalid padding.', 'red')
            return False

        if not 0 < input_dict['target_radius'].value < float('inf'):
            gui.bottom_bar.message_display('Invalid target dimensions.', 'red')
            return False

        path = input_dict['pos_list_path'].value
        if not os.path.isfile(path):
            gui.bottom_bar.message_display('Position list file was not found.', 'red')
            return False
        ex_start = path.rfind('.')
        if not path[ex_start:len(path)] == '.csv':
            gui.bottom_bar.message_display('Position list file only supports .csv', 'red')
            return False
    return True
