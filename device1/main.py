"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Manages VNA state and VNA communication.

Hardware:
    Keysight M9019A PXIe Chassis Gen3
    Keysight M9037A PXIe High-Performance Embedded Controller
    Keysight M9802A PXI Vector Network Analyzer, 6 Port (x4)

Author: Noah Stieler, 2023
"""
import threading
import tkinter
import tkinter as tk

import pyvisa as visa

import gui
import out
from display_resources import visa_display_resources
from .gui import calibration
from .imaging import VNA
from .input_validate import input_validate

VISA_ADDRESS_VNA = 'TCPIP0::Localhost::hislip0::INSTR'

state = 'idle'

vna = VNA(None)
_entry_vna, _button_calib = None, None

"""
Each key is an input parameter and the value is a list.
0 = the widget
1 = parameter value
2 = parameter display name
"""
input_param = {}


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

    # Define button functionality
    gui.bottom_bar.on_button_run(on_button_run)
    gui.tab_hardware.on_hardware_scan(scan_for_hardware)
    gui.tab_hardware.on_check_connection(visa_display_resources)

    # Set up hardware gui
    global _entry_vna, _button_calib
    _entry_vna, _button_calib = gui.tab_hardware.add_hardware('VNA', default_value=VISA_ADDRESS_VNA,
                                                              action=True, action_name='Calibrate')
    _button_calib.configure(command=calibration.create_popup)
    _button_calib['state'] = tk.DISABLED

    calibration.on_apply_calib = on_apply_calib

    while not gui.core.app_terminated:
        gui.core.update()
        get_gui_parameters()

        if state == 'idle':
            pass
        if state == 'scan':
            t = threading.Thread(target=vna.fire)
            t.start()

            gui.bottom_bar.message_display('Scanning...', 'blue')

            gui.core.update_during_thread_wait(t)

            gui.bottom_bar.message_display('Scan complete.', 'blue')
            state = 'scan_finished'

        if state == 'scan_finished':
            vna.save_snp(out.output['full_path'])
            gui.bottom_bar.message_display('Scan saved.', 'green')
            state = 'idle'


def on_button_run():
    """Begins a scan.
    Checks that hardware is connected and ready,
    that all user input is valid. Assuming no errors,
    state is changed to 'scan'."""

    if vna.resource is None:
        gui.bottom_bar.message_display('Hardware setup failed.', 'red')
        return

    vna.set_parameter_ranges()

    valid = input_validate(vna, input_param)
    if not valid:
        return

    gui.bottom_bar.message_clear()

    """Initialize vna parameters"""
    vna.data_point_count = int(input_param['num_points'][1])
    vna.if_bandwidth = input_param['ifbw'][1]
    vna.freq_start = input_param['freq_start'][1]
    vna.freq_stop = input_param['freq_stop'][1]

    vna.initialize()

    out.init_root(gui.tab_home.get_output_dir(), gui.tab_home.get_name())

    global state
    state = 'scan'


def scan_for_hardware():
    """Opens the vna resource and checks there is a valid
    connection with it."""
    visa_resource_manager = visa.ResourceManager()
    r_list = visa_resource_manager.list_resources()
    global vna
    visa_vna = None

    if _entry_vna.get() in r_list:
        visa_vna = visa_resource_manager.open_resource(_entry_vna.get())

        _button_calib['state'] = tk.ACTIVE
        gui.tab_hardware.set_indicator(0, 'Resource found.', 'blue')
    else:
        _button_calib['state'] = tk.DISABLED
        gui.tab_hardware.set_indicator(0, 'Resource not found.', 'red')
    vna = VNA(visa_vna)

    if vna.resource is not None:
        vna.set_calibration_list()  # Get calibrations from VNA
        calibration.cal_list = vna.calibration_list  # Set them in the GUI


def on_apply_calib():
    """Stores the selected calibration and calibrates the VNA"""
    vna.calibration = calibration.get_selected()
    # Done on thread to prevent gui from freezing
    t = threading.Thread(target=vna.calibrate)
    t.start()

    gui.tab_hardware.set_indicator(0, 'Calibrating...', 'blue')
    gui.core.update_during_thread_wait(t)
    gui.tab_hardware.set_indicator(0, 'Calibrated.', 'green')


def get_gui_parameters():
    """Gets data from the tkinter widgets and updates all
    the parameters. For numeric entries, if the input is invalid
    the parameter is set to inf. This will correctly throw an
    error when checking parameters."""
    try:
        for key in input_param:
            input_param[key][1] = input_param[key][0].get()
            try:
                input_param[key][1] = float(input_param[key][1])
            except ValueError:
                input_param[key][1] = float('inf')
    except tkinter.TclError:
        pass


# Old test code, kept for command reference
"""def main():
    rm = visa.ResourceManager()
    address = rm.list_resources()[5]

    print(address)

    resource = rm.open_resource(address)
    resource.timeout = 60 * 1000 # Time in milliseconds

    print(resource.query('*IDN?'))

    resource.write('SYSTEM:PRESET')

    calibration = resource.query('CSET:CATALOG?')
    calibration = calibration.replace('\"', '')
    calibration = calibration.replace('\n', '')
    calibration = calibration.split(',')
    print(f'calibration = {calibration}')

    resource.write('SENSE1:CORRECTION:CSET:ACTIVATE \''+calibration[3]+'\', 1')
    resource.query('*OPC?')
    print('Calibrated.')
    

    resource.write('TRIGGER:SEQUENCE:SOURCE MANUAL')
    resource.write('SENSE1:SWEEP:MODE HOLD')
    resource.query('*OPC?')
    print('Trigger configured.')

    # resource.write('CALCULATE1:PARAMETER:DEFINE:EXTENDED \'parameter_S22_22\', \'S22_22\'')

    # resource.write('DISPLAY:WINDOW1:TRACE1:DELETE')
    # resource.query('*OPC?')
    # resource.write('DISPLAY:WINDOW1:TRACE1:FEED \'parameter_S22_22\'')

    resource.write('SENSE1:SWEEP:POINTS 2101')
    resource.write('SENSE1:CORRECTION:CACHE:MODE 1')
    resource.query('*OPC?')

    resource.write('INITIATE1:IMMEDIATE')
    resource.query('*OPC?')
    print('Scan complete.')

    ports = ''
    for i in range(1, 25):
        if not i == 24:
            ports = ports + str(i) + ','
        else:
            ports = ports + str(i)

    dest = 'C:\\Users\\STIELERN\\Desktop\\out_FAST.s24p'
    start = time.time()
    resource.write(f'CALCULATE1:MEASURE1:DATA:SNP:PORTS:SAVE \'{ports}\', \'{dest}\', fast')
    resource.query('*OPC?')
    print(f'dt (fast) = {time.time()-start}')

    # Slow way to save data
    # start = time.time()
    # resource.write('MMEMORY:STORE \'C:\\Users\\STIELERN\\Desktop\\out_SLOW.s24p\'')
    # resource.query('*OPC?')
    # print(f'dt (slow) = {time.time()-start}')

    resource.close()"""
