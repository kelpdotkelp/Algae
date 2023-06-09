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

import tkinter as tk

import pyvisa as visa

import gui
from display_resources import visa_display_resources
from .gui import calibration
from .imaging import VNA

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
    input_param['power'] = [gui.tab_home.add_parameter_num('Power (dBm)'),
                            0, 'Power (dBm)']

    # Define button functionality
    gui.tab_hardware.on_hardware_scan(scan_for_hardware)
    gui.tab_hardware.on_check_connection(visa_display_resources)

    # Set up hardware gui
    global _entry_vna, _button_calib
    _entry_vna, _button_calib = gui.tab_hardware.add_hardware('VNA', default_value='change me!',
                                                              action=True, action_name='Calibrate')
    _button_calib.configure(command=calibration.create_popup)
    _button_calib['state'] = tk.DISABLED

    calibration.on_apply_calib = on_apply_calib
    calibration.cal_list = ['A', 'B', 'C', 'D']

    while not gui.core.app_terminated:
        gui.core.update()


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


def on_apply_calib():
    """Stores the selected calibration and calibrates the VNA"""
    vna.calibration = calibration.get_selected()
    vna.calibrate()
    gui.tab_hardware.set_indicator(0, 'Calibrated.', 'green')


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
