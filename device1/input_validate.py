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

    if not (vna.data_point_count_range[0] <= input_dict['num_points'].value <= vna.data_point_count_range[1]):
        gui.bottom_bar.message_display('\"' + input_dict['num_points'].name + f'\" must be in range: ' +
                                       str(vna.data_point_count_range), 'red')
        valid = False
    elif not (vna.if_bandwidth_range[0] <= input_dict['ifbw'].value <= vna.if_bandwidth_range[1]):
        gui.bottom_bar.message_display('\"' + input_dict['ifbw'].name + f'\" must be in range: ' +
                                       str(vna.if_bandwidth_range), 'red')
        valid = False
    elif not (vna.freq_start_range[0] <= input_dict['freq_start'].value <= vna.freq_start_range[1]):
        gui.bottom_bar.message_display('\"' + input_dict['freq_start'].name + f'\" must be in range: ' +
                                       str(vna.freq_start_range), 'red')
        valid = False
    elif not (vna.freq_stop_range[0] <= input_dict['freq_stop'].value <= vna.freq_stop_range[1]):
        gui.bottom_bar.message_display('\"' + input_dict['freq_stop'].name + f'\" must be in range: ' +
                                       str(vna.freq_stop_range), 'red')
        valid = False
    elif not (input_dict['freq_stop'].value > input_dict['freq_start'].value):
        gui.bottom_bar.message_display('Start frequency must be less than stop frequency.', 'red')
        valid = False
    elif not os.path.isdir(input_dict['output_dir'].value):
        gui.bottom_bar.message_display('Invalid output directory.', 'red')
        valid = False

    return valid
