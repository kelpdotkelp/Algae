"""
Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Parses the data received from the VNA and re-formats it
formats so that it can be used to generate
valid JSON.

Author: Noah Stieler, 2023
"""

from datetime import date, datetime

def _vna_str_to_float(str_points):
    """Converts string list of complex numbers
    to floating point list"""
    num_list = str_points.split(',')

    for i in range(len(num_list)):
        str = num_list[i]
        sign = 1 if str[0] == '+' else -1
        sign_exp = 1 if str[15] == '+' else -1
        num_list[i] = sign * float(str[1:14]) * pow(10, sign_exp * int(str[16:19]))

    return num_list


def format_data_one_sweep(str_points, freq_list):
    """Returns the correctly structured list that can later be
    incorporated into JSON format"""
    float_points = _vna_str_to_float(str_points)

    #Check to ensure no data is missing from vna
    if len(float_points) != 2 * len(freq_list):
        raise MissingDataException(len(float_points), 2 * len(freq_list))

    # Each entry is a list of frequency, real, and imaginary components of measurement
    measurement_set = []

    for i in range(len(freq_list)):
        measurement_set.append([freq_list[i], float_points[2 * i], float_points[1 + 2 * i]])

    return measurement_set


def format_meta_data(vna):
    """Returns the correctly structured dictionary that can later
    be incorporated into JSON format"""
    out_dict = {
        'freq_start': vna.freq_start,
        'freq_stop': vna.freq_stop,
        'if_bandwidth': vna.if_bandwidth,
        'num_points': vna.data_point_count,
        'power': vna.power,
        'vna_name': vna.name,
        'date': str(date.today()),
        'time': (datetime.now()).strftime('%H:%M:%S'),
    }
    return out_dict


class MissingDataException(Exception):
    """Raised when the parsed vna data does not match two floats per frequency"""
    def __init__(self, actual_num_count, expected_num_count):
        self.actual_num_count = actual_num_count
        self.expected_num_count = expected_num_count

    def display_message(self):
        print(f'MissingDataException:'
              f'\n\texpected {self.expected_num_count} floating point numbers'
              f'\n\trecieved from vna {self.actual_num_count} floating point numbers')

