"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Provides error checking on user input.

Author: Noah Stieler, 2023
"""

import os.path

import gui
from .imaging import VNA


def input_validate(vna: VNA, input_param: dict) -> bool:
    """Checks all user input for errors/invalid entries"""
    valid = True

    if not (vna.data_point_count_range[0] <= input_param['num_points'][1] <= vna.data_point_count_range[1]):
        gui.bottom_bar.message_display('\"' + input_param['num_points'][2] + f'\" must be in range: ' +
                                       str(vna.data_point_count_range), 'red')
        valid = False
    elif not (vna.if_bandwidth_range[0] <= input_param['ifbw'][1] <= vna.if_bandwidth_range[1]):
        gui.bottom_bar.message_display('\"' + input_param['ifbw'][2] + f'\" must be in range: ' +
                                       str(vna.if_bandwidth_range), 'red')
        valid = False
    elif not (vna.freq_start_range[0] <= input_param['freq_start'][1] <= vna.freq_start_range[1]):
        gui.bottom_bar.message_display('\"' + input_param['freq_start'][2] + f'\" must be in range: ' +
                                       str(vna.freq_start_range), 'red')
        valid = False
    elif not (vna.freq_stop_range[0] <= input_param['freq_stop'][1] <= vna.freq_stop_range[1]):
        gui.bottom_bar.message_display('\"' + input_param['freq_stop'][2] + f'\" must be in range: ' +
                                       str(vna.freq_stop_range), 'red')
        valid = False
    elif not (input_param['freq_stop'][1] > input_param['freq_start'][1]):
        gui.bottom_bar.message_display('Start frequency must be less than stop frequency.', 'red')
        valid = False
    elif not os.path.isdir(gui.tab_home.get_output_dir()):
        gui.bottom_bar.message_display('Invalid output directory.', 'red')
        valid = False

    return valid
