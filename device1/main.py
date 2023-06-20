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
import tkinter as tk

import pyvisa as visa

import gui
from gui.parameter import input_dict
import out
from display_resources import display_resources
from .data_handler import format_meta_data
from .gui import calibration
from .imaging import VNA
from .input_validate import input_validate

VISA_ADDRESS_VNA = 'TCPIP0::Localhost::hislip0::INSTR'

state = 'idle'

vna = VNA(None)
_button_calib = None


def main() -> None:
    global state

    gui.bottom_bar.enable_button_stop = False
    gui.core.create_gui()

    # Set up input parameters
    input_dict['num_points'] = gui.tab_home.add_parameter_num('Number of points')
    input_dict['ifbw'] = gui.tab_home.add_parameter_num('IF bandwidth (Hz)')
    input_dict['freq_start'] = gui.tab_home.add_parameter_num('Start frequency (Hz)')
    input_dict['freq_stop'] = gui.tab_home.add_parameter_num('Stop frequency (Hz)')

    # Define button functionality
    gui.bottom_bar.on_button_run(on_button_run)
    gui.tab_hardware.on_connect(scan_for_hardware)
    gui.tab_hardware.on_display_resources(display_resources)

    # Set up hardware gui
    global _button_calib
    input_dict['address_vna'], _button_calib = \
        gui.tab_hardware.add_hardware('VNA', default_value=VISA_ADDRESS_VNA,
                                      action=True, action_name='Calibrate')

    # Set up calibration selection
    _button_calib.configure(command=calibration.create_popup)
    _button_calib['state'] = tk.DISABLED
    calibration.on_apply_calib = on_apply_calib

    while not gui.core.app_terminated:
        gui.core.update()

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
            out.create_meta_file(format_meta_data(vna, input_dict['description'].value))
            vna.save_snp(out.output['full_path'])
            gui.bottom_bar.message_display('Scan saved.', 'green')
            state = 'idle'


def on_button_run() -> None:
    """Begins a scan.
    Checks that hardware is connected and ready,
    that all user input is valid. Assuming no errors,
    state is changed to 'scan'."""

    if vna.resource is None:
        gui.bottom_bar.message_display('Hardware setup failed.', 'red')
        return

    vna.set_parameter_ranges()

    valid = input_validate(vna)
    if not valid:
        return

    gui.bottom_bar.message_clear()

    """Initialize vna parameters"""
    vna.data_point_count = int(input_dict['num_points'].value)
    vna.if_bandwidth = input_dict['ifbw'].value
    vna.freq_start = input_dict['freq_start'].value
    vna.freq_stop = input_dict['freq_stop'].value

    vna.initialize()

    out.init_root(input_dict['output_dir'].value, input_dict['output_name'].value)

    global state
    state = 'scan'


def scan_for_hardware() -> None:
    """Opens the vna resource and checks there is a valid
    connection with it."""
    visa_resource_manager = visa.ResourceManager()
    r_list = visa_resource_manager.list_resources()
    global vna
    visa_vna = None

    if input_dict['address_vna'].value in r_list:
        visa_vna = visa_resource_manager.open_resource(input_dict['address_vna'].value)

        _button_calib['state'] = tk.ACTIVE
        gui.tab_hardware.set_indicator(0, 'Resource found.', 'blue')
    else:
        _button_calib['state'] = tk.DISABLED
        gui.tab_hardware.set_indicator(0, 'Resource not found.', 'red')
    vna = VNA(visa_vna)

    if vna.resource is not None:
        vna.set_calibration_list()  # Get calibrations from VNA
        calibration.cal_list = vna.calibration_list  # Set them in the GUI


def on_apply_calib() -> None:
    """Stores the selected calibration and calibrates the VNA"""
    vna.calibration = calibration.get_selected()
    # Done on thread to prevent gui from freezing
    t = threading.Thread(target=vna.calibrate)
    t.start()

    gui.tab_hardware.set_indicator(0, 'Calibrating...', 'blue')
    gui.core.update_during_thread_wait(t)
    gui.tab_hardware.set_indicator(0, 'Calibrated.', 'green')
