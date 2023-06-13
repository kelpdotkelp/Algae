"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Parses the data received from the VNA and re-formats it
formats so that it can be used to generate
valid JSON.

Author: Noah Stieler, 2023
"""

from datetime import date, datetime


def format_data_one_sweep(str_points, freq_list):
    """Returns a list that contains lists of the real and imaginary
    components at each frequency."""
    float_points = str_points.split(',')

    for i in range(len(float_points)):
        float_points[i] = float(float_points[i])

    # Check to ensure no data is missing from vna
    if len(float_points) != 2 * len(freq_list):
        raise MissingDataException(len(float_points), 2 * len(freq_list))

    measurement_set = [[], []]

    for i in range(len(freq_list)):
        # measurement_set.append([freq_list[i], float_points[2 * i], float_points[1 + 2 * i]])
        measurement_set[0].append(float_points[2 * i])  # Real
        measurement_set[1].append(float_points[1 + 2 * i])  # Imaginary

    return measurement_set


def format_meta_data(vna, s_parameter, description, posx=0, posy=0):
    """Returns the correctly structured dictionary that can later
    be incorporated into JSON format"""
    out_dict = {
        's_parameter': s_parameter,
        'freq_start': vna.freq_start,
        'freq_stop': vna.freq_stop,
        'if_bandwidth': vna.if_bandwidth,
        'num_points': vna.data_point_count,
        'power': vna.power,
        'posx': posx,
        'posy': posy,
        'vna_name': vna.name,
        'date': str(date.today()),
        'time': (datetime.now()).strftime('%H:%M:%S'),
        'description': description
    }
    return out_dict


class MissingDataException(Exception):
    """Raised when the parsed vna data does not match two floats per frequency"""

    def __init__(self, actual_num_count, expected_num_count):
        self.actual_num_count = actual_num_count
        self.expected_num_count = expected_num_count

    def get_message(self):
        msg = f'MissingDataException:\n\texpected {self.expected_num_count} floating point numbers' \
              f'\n\treceived from vna {self.actual_num_count} floating point numbers'
        return msg
