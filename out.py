"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Handles file structure and JSON output.

Author: Noah Stieler, 2023
"""

import os.path
import json

_OUTPUT_JSON_INDENT = '\t'

# Stores currently open files.
# Each key is an s-parameter ['S11', 'S12', 'S21', 'S22']
_open_files = {}

# Manages where to write data to
_output = {
    'pos_index': 0,
    'root_name': 'algae_output',
    'dir_dest': '',  # Selected by the user
    'full_path': '',  # Full path to root dir
    'dir_cur': ''
}


def init_root(output_dir):
    """Create root directory for output."""
    _output['pos'] = 0
    _output['dir_dest'] = output_dir

    dir_created = False
    index = 0
    while not dir_created:
        full_path = _output['dir_dest'] + '\\' + _output['root_name'] + f'_{index}'
        if os.path.isdir(full_path):
            index += 1
        else:
            _output['full_path'] = full_path
            os.mkdir(_output['full_path'])
            dir_created = True


def mkdir_new_pos():
    _output['dir_cur'] = _output['full_path'] + '\\pos' + str(_output['pos_index'])
    os.mkdir(_output['dir_cur'])
    _output['pos_index'] += 1


def out_file_init(s_parameter, meta, freqs):
    f_name = _output['dir_cur'] + '\\' + s_parameter + '.json'
    _open_files[s_parameter] = open(f_name, 'w', encoding='utf-8')

    json_meta = json.dumps(meta, indent=_OUTPUT_JSON_INDENT)
    json_freqs = json.dumps(freqs)

    _open_files[s_parameter].write('{\n')  # Required for JSON formatting
    _open_files[s_parameter].write('\"meta\": ' + json_meta + ',\n')
    _open_files[s_parameter].write('\"freq\": ' + json_freqs + ',\n')
    _open_files[s_parameter].write('"data": {\n')


def out_file_data_write(s_parameter, tran, refl, list_real, list_imag, close_data):
    _open_files[s_parameter].write(_OUTPUT_JSON_INDENT + f'"t{tran}r{refl}"' + ': {\n')
    _open_files[s_parameter].write(
        2 * _OUTPUT_JSON_INDENT + '"real": ' + str(list_real) + ',\n')
    _open_files[s_parameter].write(
        2 * _OUTPUT_JSON_INDENT + '"imag": ' + str(list_imag))

    if close_data:
        _open_files[s_parameter].write('\n' + 2 * _OUTPUT_JSON_INDENT + '}\n}')
    else:
        _open_files[s_parameter].write('\n' + 2 * _OUTPUT_JSON_INDENT + '},\n')


def out_file_complete(s_parameter):
    _open_files[s_parameter].write('\n}')  # Required for JSON formatting
    _open_files[s_parameter].close()
