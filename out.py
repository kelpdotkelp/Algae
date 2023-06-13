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

_root_default_name = 'algae_output'

# Manages where to write data to
output = {
    'pos_index': 0,
    'root_name': _root_default_name,
    'dir_dest': '',  # Selected by the user
    'full_path': '',  # Full path to root dir
    'dir_cur': ''
}


def init_root(output_dir):
    """Create root directory for output."""
    output['pos'] = 0
    output['dir_dest'] = output_dir

    dir_created = False
    index = 0
    while not dir_created:
        full_path = output['dir_dest'] + '\\' + output['root_name'] + f'_{index}'
        if os.path.isdir(full_path):
            index += 1
        else:
            output['full_path'] = full_path
            os.mkdir(output['full_path'])
            dir_created = True


def mkdir_new_pos():
    """Creates new directory in the root for a position."""
    output['dir_cur'] = output['full_path'] + '\\pos' + str(output['pos_index'])
    os.mkdir(output['dir_cur'])
    output['pos_index'] += 1


def out_file_init(s_parameter, meta, freqs):
    """Initializes .json files with header information."""
    f_name = output['dir_cur'] + '\\' + s_parameter + '.json'
    _open_files[s_parameter] = open(f_name, 'w', encoding='utf-8')

    json_meta = json.dumps(meta, indent=_OUTPUT_JSON_INDENT)
    json_freqs = json.dumps(freqs)

    _open_files[s_parameter].write('{\n')  # Required for JSON formatting
    _open_files[s_parameter].write('\"meta\": ' + json_meta + ',\n')
    _open_files[s_parameter].write('\"freq\": ' + json_freqs + ',\n')
    _open_files[s_parameter].write('"data": {\n')


def out_file_data_write(s_parameter, tran, refl, list_real, list_imag, close_data):
    """Writes a single sweep to .json files."""
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
