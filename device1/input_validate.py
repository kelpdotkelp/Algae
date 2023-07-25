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


def input_validate(vna: VNA) -> bool:
    """Checks all user input for errors/invalid entries"""
    valid = True

    check_list = ['num_points', 'ifbw', 'freq_start', 'freq_stop']

    for item in check_list:
        if not (vna.p_ranges[item][0] <= input_dict[item].value <= vna.p_ranges[item][1]):
            gui.bottom_bar.message_display('\"' + input_dict[item].name + f'\" must be in range: ' +
                                           str(vna.p_ranges[item]), 'red')
            return False
    if not (input_dict['freq_stop'].value > input_dict['freq_start'].value):
        gui.bottom_bar.message_display('Start frequency must be less than stop frequency.', 'red')
        valid = False
    elif not os.path.isdir(input_dict['output_dir'].value):
        gui.bottom_bar.message_display('Invalid output directory.', 'red')
        valid = False

    return valid
