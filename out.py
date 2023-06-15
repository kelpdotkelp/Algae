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


def init_root(output_dir: str, root_name: str) -> None:
    """Create root directory for output."""
    output['pos'] = 0
    output['dir_dest'] = output_dir
    output['root_name'] = root_name

    dir_created = False
    index = 0
    while not dir_created:
        try:
            full_path = output['dir_dest'] + '\\' + output['root_name']
            if index != 0:
                full_path = full_path + f'_{index}'

            os.mkdir(full_path)
            output['full_path'] = full_path

            dir_created = True
        except FileExistsError:
            index += 1
        except OSError:  # Invalid directory name
            output['root_name'] = _root_default_name


def create_meta_file(meta: dict) -> None:
    file = open(output['full_path'] + '\\meta.json', 'w', encoding='utf-8')
    json_meta = json.dumps(meta, indent=_OUTPUT_JSON_INDENT)
    file.write('{\n')
    file.write('\"meta\": ' + json_meta + '\n}')
    file.close()


def mkdir_new_pos() -> None:
    """Creates new directory in the root for a position."""
    output['dir_cur'] = output['full_path'] + '\\pos' + str(output['pos_index'])
    os.mkdir(output['dir_cur'])
    output['pos_index'] += 1


def out_file_init(s_parameter: str, meta: dict, freqs: list) -> None:
    """Initializes .json files with header information."""
    f_name = output['dir_cur'] + '\\' + s_parameter + '.json'
    _open_files[s_parameter] = open(f_name, 'w', encoding='utf-8')

    json_meta = json.dumps(meta, indent=_OUTPUT_JSON_INDENT)
    json_freqs = json.dumps(freqs)

    _open_files[s_parameter].write('{\n')  # Required for JSON formatting
    _open_files[s_parameter].write('\"meta\": ' + json_meta + ',\n')
    _open_files[s_parameter].write('\"freq\": ' + json_freqs + ',\n')
    _open_files[s_parameter].write('"data": {\n')


def out_file_data_write(s_parameter: str, tran: int, refl: int,
                        real: list, imag: list, close_data: bool) -> None:
    """Writes a single sweep to .json files."""
    _open_files[s_parameter].write(_OUTPUT_JSON_INDENT + f'"t{tran}r{refl}"' + ': {\n')
    _open_files[s_parameter].write(
        2 * _OUTPUT_JSON_INDENT + '"real": ' + str(real) + ',\n')
    _open_files[s_parameter].write(
        2 * _OUTPUT_JSON_INDENT + '"imag": ' + str(imag))

    if close_data:
        _open_files[s_parameter].write('\n' + 2 * _OUTPUT_JSON_INDENT + '}\n}')
    else:
        _open_files[s_parameter].write('\n' + 2 * _OUTPUT_JSON_INDENT + '},\n')


def out_file_complete(s_parameter: str) -> None:
    _open_files[s_parameter].write('\n}')  # Required for JSON formatting
    _open_files[s_parameter].close()
