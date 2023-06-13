"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Re-formats data so that it is ready fir JSON conversion.

Author: Noah Stieler, 2023
"""

from datetime import date, datetime


def format_meta_data(vna, description, posx=0, posy=0):
    """Returns the correctly structured dictionary that can later
    be incorporated into JSON format"""
    out_dict = {
        'freq_start': vna.freq_start,
        'freq_stop': vna.freq_stop,
        'if_bandwidth': vna.if_bandwidth,
        'num_points': vna.data_point_count,
        'posx': posx,
        'posy': posy,
        'vna_name': vna.name,
        'vna_calibration': vna.calibration,
        'date': str(date.today()),
        'time': (datetime.now()).strftime('%H:%M:%S'),
        'description': description
    }
    return out_dict
