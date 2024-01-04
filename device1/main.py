"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Manages VNA, and controls cartesian robot.

Hardware:
    Keysight M9019A PXIe Chassis Gen3
    Keysight M9037A PXIe High-Performance Embedded Controller
    Keysight M9802A PXI Vector Network Analyzer, 6 Port (x4)
    Custom GRBL cartesian robot

Author: Noah Stieler, 2023
"""
import serial.tools.list_ports

from gui.parameter import input_dict
from gui.button import button_dict
import out
from display_resources import display_resources
from .data_handler import format_meta_data
from .gui import calibration, position
from .imaging import *
from .input_validate import input_validate

VISA_ADDRESS_VNA = 'TCPIP0::Localhost::hislip0::INSTR'

state = 'idle'

vna = None


def main() -> None:
    global state

    gui.bottom_bar.enable_button_stop = False
    gui.core.create_gui(position.custom_position_box)

    # Set up input parameters
    input_dict['num_points'] = gui.tab_home.add_parameter_num('Number of points')
    input_dict['ifbw'] = gui.tab_home.add_parameter_num('IF bandwidth (Hz)')
    input_dict['freq_start'] = gui.tab_home.add_parameter_num('Start frequency (Hz)')
    input_dict['freq_stop'] = gui.tab_home.add_parameter_num('Stop frequency (Hz)')

    # Define button functionality
    button_dict['connect'].command(on_button_connect)
    button_dict['disp_res'].command(display_resources)
    button_dict['run'].command(on_button_run)

    # Set up hardware gui
    input_dict['address_vna'], button_dict['calibrate'] = \
        gui.tab_hardware.add_hardware('VNA', default_value=VISA_ADDRESS_VNA,
                                      action=True, action_name='Calibrate')
    # Set up calibration selection
    button_dict['calibrate'].command(calibration.create_popup)
    button_dict['calibrate'].set_state(0)
    calibration.on_apply_calib = on_apply_calib

    input_dict['address_cnc'], button_dict['auto_detect'] = \
        gui.tab_hardware.add_hardware('CNC', default_value='',
                                      action=True, action_name='Auto-detect')
    button_dict['auto_detect'].command(on_button_auto_detect)
    button_dict['auto_detect'].set_state(1)

    while not gui.core.app_terminated:
        gui.core.update()

        if state == 'idle':
            gui.parameter.update()
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

    if vna is None:
        gui.bottom_bar.message_display('Hardware setup failed.', 'red')
        return

    valid = input_validate(vna)
    if not valid:
        return

    gui.bottom_bar.message_clear()

    vna.initialize()

    out.init_root(input_dict['output_dir'].value, input_dict['output_name'].value)

    global state
    state = 'scan'


def on_button_connect() -> None:
    """Opens the vna resource and checks there is a valid
    connection with it."""
    global vna

    vna = create_vna(input_dict['address_vna'].value)
    if vna is not None:
        button_dict['calibrate'].set_state(1)
        gui.tab_hardware.set_indicator(0, 'Resource found.', 'blue')

        vna.set_calibration_list()  # Get calibrations from VNA
        calibration.cal_list = vna.calibration_list  # Set them in the GUI
    else:
        button_dict['calibrate'].set_state(0)
        gui.tab_hardware.set_indicator(0, 'Resource not found.', 'red')


def on_apply_calib() -> None:
    """Stores the selected calibration and calibrates the VNA"""
    vna.calibration = calibration.get_selected()
    # Done on thread to prevent gui from freezing
    t = threading.Thread(target=vna.calibrate)
    t.start()

    gui.tab_hardware.set_indicator(0, 'Calibrating...', 'blue')
    gui.core.update_during_thread_wait(t)
    gui.tab_hardware.set_indicator(0, 'Calibrated.', 'green')


def on_button_auto_detect() -> None:
    port_list = serial.tools.list_ports.comports()

    if len(port_list) == 0:
        return

    elif len(port_list) == 1:
        input_dict['address_cnc'].set(port_list[0].name)
