"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Re-formats data so that it is ready fir JSON conversion.

Author: Noah Stieler, 2023
"""

from datetime import date, datetime

from .imaging import VNA
from gui.parameter import input_dict


def format_meta_data(vna: VNA, description: str, posx=0, posy=0) -> dict:
    """Returns the correctly structured dictionary that can later
    be incorporated into JSON format"""
    out_dict = {
        'freq_start': input_dict['freq_start'].value,
        'freq_stop': input_dict['freq_stop'].value,
        'if_bandwidth': input_dict['ifbw'].value,
        'num_points': input_dict['num_points'].value,
        'posx': posx,
        'posy': posy,
        'vna_name': vna.name,
        'vna_calibration': vna.calibration,
        'date': str(date.today()),
        'time': (datetime.now()).strftime('%H:%M:%S'),
        'description': description
    }
    return out_dict
