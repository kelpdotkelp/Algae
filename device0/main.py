"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Please install:
NI-VISA     ->     https://www.ni.com/en-ca/support/downloads/drivers/download.ni-visa.html#480875
NI-488.2    ->     https://www.ni.com/en-ca/support/downloads/drivers/download.ni-488-2.html#467646

NI GPIB setup guide:
https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000x2YDCAY&l=en-CA

Author: Noah Stieler, 2023
"""
import os.path
import tkinter
import json
import pyvisa as visa

import gui
from . import data_handler
from . import canvas
from .hardware_imaging import VNA, Switches

state = 'idle'

tran_range = (Switches.PORT_MIN, Switches.PORT_MAX)
refl_range = (Switches.PORT_MIN, Switches.PORT_MAX)
port_tran = tran_range[0]
port_refl = refl_range[0]

PATH_VISA_LIBRARY = r'C:\Windows\system32\visa64.dll'

OUTPUT_JSON_INDENT = '\t'
output_dir = ''
output_dir_name = 'algae_output'
output_full_path = ''  # Concatenation of output dir and parent folder
# Stores currently open files.
# Each key is an s-parameter ['S11', 'S12', 'S21', 'S22']
output_file_dict = {}

vna, switches = VNA(None), Switches(None)
_e_vna, _e_switches = None, None

"""
Each key is an input parameter and the value is a list.
0 = the widget
1 = parameter value
2 = parameter display name
"""
input_param = {}
"""
Each key holds a list:
0 = checkbox widget
1 = current state of the widget (0 or 1)
"""
input_s_param = {}


"""
Bug
VisaIOError: VI_ERROR_INV_OBJECT 
Thrown when:
    1. Valid hardware is set up
    2. USB is disconnected
Thrown by: pyvisa/highlevel.py
-Not sure how to fix something thrown within the package
-Not a fatal error either as everything works if USB is
    connected again 
"""


def main():
    global state

    gui.core.create_gui()

    # Set up input parameters
    input_param['num_points'] = [gui.tab_home.add_parameter_num('Number of points'),
                                 0, 'Number of points']
    input_param['ifbw'] = [gui.tab_home.add_parameter_num('IF bandwidth (Hz)'),
                           0, 'IF bandwidth (Hz)']
    input_param['freq_start'] = [gui.tab_home.add_parameter_num('Start frequency (Hz)'),
                                 0, 'Start frequency (Hz)']
    input_param['freq_stop'] = [gui.tab_home.add_parameter_num('Stop frequency (Hz)'),
                                0, 'Stop frequency (Hz)']
    input_param['power'] = [gui.tab_home.add_parameter_num('Power (dBm)'),
                            0, 'Power (dBm)']

    global input_s_param
    input_s_param = gui.tab_home.add_parameter_checkbox(['S11', 'S12', 'S21', 'S22'])
    input_s_param['S21'][0].state(['selected'])

    # Set up hardware gui
    global _e_vna, _e_switches
    _e_vna = gui.tab_hardware.add_hardware('VNA', default_value='GPIB0::16::INSTR')
    _e_switches = gui.tab_hardware.add_hardware('Switches', default_value='GPIB0::15::INSTR')

    # Define button functionality
    gui.tab_hardware.on_hardware_scan(scan_for_hardware)
    gui.tab_hardware.on_check_connection(check_connections)
    gui.bottom_bar.on_button_run(on_button_run)
    gui.bottom_bar.on_button_stop(abort_scan)

    """     
        Main application loop   
    """
    while not gui.core.app_terminated:
        gui.core.update()
        get_gui_parameters()

        gui.tab_home.draw_canvas(canvas.update)

        # debug_play_graphics()

        if state == 'idle':
            pass
        if state == 'scan':
            if port_refl == port_tran:
                scan_finished = update_ports()
                if scan_finished:
                    state = 'scan_finished'
                continue

            switches.set_tran(port_tran)
            switches.set_refl(port_refl)

            vna_output = vna.fire()

            # Convert output from string to a list of floats
            for s_parameter in vna.sp_to_measure:
                try:
                    vna_output[s_parameter] = data_handler.format_data_one_sweep(vna_output[s_parameter], vna.freq_list)
                except data_handler.MissingDataException as error:
                    gui.bottom_bar.message_display(error.get_message(), 'red')
                    abort_scan()

            for s_parameter in vna.sp_to_measure:
                output_file_dict[s_parameter].write(OUTPUT_JSON_INDENT + f'"t{port_tran}r{port_refl}"' + ': {\n')
                output_file_dict[s_parameter].write(
                    2 * OUTPUT_JSON_INDENT + '"real": ' + str(vna_output[s_parameter][0]) + ',\n')
                output_file_dict[s_parameter].write(
                    2 * OUTPUT_JSON_INDENT + '"imag": ' + str(vna_output[s_parameter][1]))

                if port_tran == tran_range[1] and port_refl == refl_range[1] - 1:
                    output_file_dict[s_parameter].write('\n' + 2 * OUTPUT_JSON_INDENT + '}\n}')  # Close data section
                else:
                    output_file_dict[s_parameter].write('\n' + 2 * OUTPUT_JSON_INDENT + '},\n')

            scan_finished = update_ports()
            update_progress_bar()

            if scan_finished:
                state = 'scan_finished'

            # print(f't{port_tran}r{port_refl}')
        if state == 'scan_finished':

            for s_parameter in vna.sp_to_measure:
                output_file_dict[s_parameter].write('\n}')  # Required for JSON formatting
                output_file_dict[s_parameter].close()

            vna.close()
            switches.close()

            gui.bottom_bar.progress_bar_set(0)
            gui.bottom_bar.toggle_button_stop()

            state = 'idle'


def update_ports():
    """Cycles the trans and refl port of the switches.
    Returns a bool to indicate when all trans/refl pairs have
    been cycled through. Also updates canvas info."""
    global port_tran, port_refl
    is_complete = False

    port_refl += 1
    if port_refl > refl_range[1]:
        port_tran += 1
        port_refl = refl_range[0]
    if port_tran > tran_range[1]:
        is_complete = True
        canvas.port_reset()
    else:
        canvas.port_complete(port_tran)

    canvas.port_pair(port_tran, port_refl)

    return is_complete


def on_button_run():
    """Begins a scan.
    Checks that hardware is connected and ready,
    that all user input is valid, and sets up output directory and files.
    Assuming no user errors, state is changed to 'scan'."""

    """Check that hardware is connected and ready."""
    scan_for_hardware()
    if vna.resource is None or switches.resource is None:
        gui.bottom_bar.message_display('Hardware setup failed.', 'red')
        return

    """Check that all parameters are valid."""
    vna.set_parameter_ranges()
    if not (vna.data_point_count_range[0] <= input_param['num_points'][1] <= vna.data_point_count_range[1]):
        gui.bottom_bar.message_display('\"' + input_param['num_points'][2] + f'\" must be in range: ' +
                                       str(vna.data_point_count_range), 'red')
        return
    if not (vna.if_bandwidth_range[0] <= input_param['ifbw'][1] <= vna.if_bandwidth_range[1]):
        gui.bottom_bar.message_display('\"' + input_param['ifbw'][2] + f'\" must be in range: ' +
                                       str(vna.if_bandwidth_range), 'red')
        return
    if not (vna.freq_start_range[0] <= input_param['freq_start'][1] <= vna.freq_start_range[1]):
        gui.bottom_bar.message_display('\"' + input_param['freq_start'][2] + f'\" must be in range: ' +
                                       str(vna.freq_start_range), 'red')
        return
    if not (vna.freq_stop_range[0] <= input_param['freq_stop'][1] <= vna.freq_stop_range[1]):
        gui.bottom_bar.message_display('\"' + input_param['freq_stop'][2] + f'\" must be in range: ' +
                                       str(vna.freq_stop_range), 'red')
        return
    if not (vna.power_range[0] <= input_param['power'][1] <= vna.power_range[1]):
        gui.bottom_bar.message_display('\"' + input_param['power'][2] + f'\" must be in range: ' +
                                       str(vna.power_range), 'red')
        return
    if not (input_param['freq_stop'][1] > input_param['freq_start'][1]):
        gui.bottom_bar.message_display('Start frequency must be less than stop frequency.', 'red')
        return

    if not os.path.isdir(gui.tab_home.get_output_dir()):
        gui.bottom_bar.message_display('Invalid output directory.', 'red')
        return

    gui.bottom_bar.message_clear()

    """Set up output directory"""
    global output_dir, output_full_path
    output_dir = gui.tab_home.get_output_dir()
    dir_created = False

    index = 0
    while not dir_created:
        if os.path.isdir(output_dir + rf'\{output_dir_name}_{index}'):
            index += 1
        else:
            output_full_path = output_dir + rf'\{output_dir_name}_{index}'
            os.mkdir(output_full_path)
            dir_created = True

    """Initialize vna parameters"""
    vna.data_point_count = int(input_param['num_points'][1])
    vna.if_bandwidth = input_param['ifbw'][1]
    vna.freq_start = input_param['freq_start'][1]
    vna.freq_stop = input_param['freq_stop'][1]
    vna.power = input_param['power'][1]

    vna.sp_to_measure = []
    for key in input_s_param:
        if input_s_param[key][1] == 1:
            vna.sp_to_measure.append(key)

    vna.initialize()
    switches.initialize()

    """Add meta data and list of frequencies to JSON file"""
    global output_file_dict

    for s_parameter in vna.sp_to_measure:
        output_file_dict[s_parameter] = open(output_full_path + '\\' + s_parameter + '.json', 'w', encoding='utf-8')

        output_file_dict[s_parameter].write('{\n')  # Required for JSON formatting

        json_out = json.dumps(
            data_handler.format_meta_data(vna, s_parameter, gui.tab_home.get_description())
            , indent=OUTPUT_JSON_INDENT)
        output_file_dict[s_parameter].write('\"meta\": ' + json_out + ',\n')

        json_out = json.dumps(vna.freq_list)
        output_file_dict[s_parameter].write('\"freq\": ' + json_out + ',\n')

        output_file_dict[s_parameter].write('"data": {\n')

    global port_tran, port_refl
    port_tran = tran_range[0]
    port_refl = refl_range[0]

    gui.bottom_bar.toggle_button_stop()

    global state
    state = 'scan'


def abort_scan():
    for s_parameter in vna.sp_to_measure:
        output_file_dict[s_parameter].close()

    gui.bottom_bar.progress_bar_set(0)
    gui.bottom_bar.toggle_button_stop()

    canvas.port_reset()

    global state
    state = 'idle'


def scan_for_hardware():
    """Opens the vna and switches resources and checks there is a valid
    connection with them."""
    visa_resource_manager = visa.ResourceManager(PATH_VISA_LIBRARY)
    r_list = visa_resource_manager.list_resources()
    global vna, switches
    visa_vna, visa_switches = None, None

    if _e_vna.get() in r_list:
        visa_vna = visa_resource_manager.open_resource(_e_vna.get())
        gui.tab_hardware.set_indicator(0, 'Resource found.', 'green')
    else:
        gui.tab_hardware.set_indicator(0, 'Resource not found.', 'red')
    vna = VNA(visa_vna)

    if _e_switches.get() in r_list:
        visa_switches = visa_resource_manager.open_resource(_e_switches.get())
        gui.tab_hardware.set_indicator(1, 'Resource found.', 'green')
    else:
        gui.tab_hardware.set_indicator(1, 'Resource not found.', 'red')
    switches = Switches(visa_switches)


def check_connections():
    """Lists available resources and creates a popup to display them."""
    visa_resource_manager = visa.ResourceManager()
    r_list = visa_resource_manager.list_resources()
    r_display = ''
    for address in r_list:

        try:
            resource = visa_resource_manager.open_resource(address)
            r_display = r_display + address + '\n\t' + resource.query('*IDN?') + '\n'
        except visa.errors.VisaIOError:
            r_display = r_display + address + '\n\t' + r'N\A' + '\n'
    if len(r_list) == 0:
        r_display = 'No resources found.'

    gui.tab_hardware.create_message(r_display)


def get_gui_parameters():
    """Gets data from the tkinter widgets and
    updates all the parameters. For numeric entries,
    if the input is invalid, the parameter is set to inf.
    This will correctly throw an error when checking parameters."""
    try:
        for key in input_param:
            input_param[key][1] = input_param[key][0].get()
            try:
                input_param[key][1] = float(input_param[key][1])
            except ValueError:
                input_param[key][1] = float('inf')

        for key in input_s_param:
            if 'selected' in input_s_param[key][0].state():
                input_s_param[key][1] = 1
            else:
                input_s_param[key][1] = 0
    except tkinter.TclError:
        pass


def update_progress_bar():
    try:
        pair_count = tran_range[1] * (refl_range[1] - 1)
        gui.bottom_bar.progress_bar_set((port_tran * 24 - 1 + port_refl) / pair_count)
    except tkinter.TclError:
        pass


def debug_play_graphics():
    import time
    update_ports()
    time.sleep(0.25)