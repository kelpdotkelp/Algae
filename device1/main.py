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

import pygrbl

from gui.parameter import input_dict
from gui.button import button_dict
import out
from display_resources import display_resources
from .data_handler import format_meta_data
from .gui import calibration, position
from .imaging import *
from .input_validate import input_validate
from . import pygrbl_handler

"""
    VERY IMPORTANT
    pygrbl default baud rate must be changed to 9600 because device1 uses v0.8
    of GRBL, which requires that baud rate. An incorrect baud rate causes the
    software to get stuck waiting for data from device1.
"""
pygrbl.core.BAUD_RATE = 9600

VISA_ADDRESS_VNA = 'TCPIP0::Localhost::hislip0::INSTR'

# Defaults for this device
WORKING_AREA_RADIUS = 50
WORKING_AREA_HEIGHT = 100
WORKING_AREA_PADDING = 10

pos_list = []
pos_index = 0

state = 'idle'
abort = False

vna = None
grbl_machine = None


def main() -> None:
    global state
    global abort
    global pos_list, pos_index

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
    button_dict['stop'].command(abort_scan)

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

    button_dict['set_origin'].command(on_set_origin)
    button_dict['set_origin'].set_state(0)

    # Set some default GUI values, as these will likely remain constant
    # Units in mm
    input_dict['wa_radius'].set(WORKING_AREA_RADIUS)
    input_dict['wa_height'].set(WORKING_AREA_HEIGHT)
    input_dict['wa_pad'].set(WORKING_AREA_PADDING)

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
            vna.save_snp(out.output['full_path'], pos_index)
            gui.bottom_bar.message_display('Scan saved.', 'green')

            state = 'next_pos'

        if state == 'next_pos':

            # All positions visited
            if pos_index + 1 >= len(pos_list):
                if input_dict['cnc_enable'].value:
                    try:
                        grbl_machine.set_position(pygrbl.Point(0, 0, 0))
                    except pygrbl.PyGRBLException as e:
                        pygrbl_handler.pygrbl_exception(e)
                        abort_scan()
                button_dict['stop'].toggle_state()
                state = 'idle'

            # Go to next position
            else:
                pos_index += 1
                pos = pos_list[pos_index]

                try:
                    grbl_machine.set_position(pos)
                except pygrbl.PyGRBLException as e:
                    pygrbl_handler.pygrbl_exception(e)
                    abort_scan()

                state = 'scan'


def on_button_run() -> None:
    """Begins a scan.
    Checks that hardware is connected and ready,
    that all user input is valid. Assuming no errors,
    state is changed to 'scan'."""
    global abort
    abort = False

    if vna is None:
        gui.bottom_bar.message_display('Hardware setup failed.', 'red')
        return

    valid = input_validate(vna, grbl_machine)
    if not valid:
        return

    gui.bottom_bar.message_clear()

    vna.initialize()

    """Set up positioning"""
    chamber = pygrbl.ChamberCylinder3D(input_dict['wa_radius'].value,
                                       input_dict['wa_height'].value,
                                       input_dict['wa_pad'].value,
                                       input_dict['target_radius'].value,
                                       2*input_dict['target_radius'].value) # Target is assumed spherical
    pygrbl.set_chamber(chamber)

    global pos_list, pos_index
    first_pos = pygrbl.Point(0, 0, 0)
    pos_index = 0
    if input_dict['cnc_enable'].value:
        pos_list = pygrbl.load_csv(input_dict['pos_list_path'].value, 3)
        first_pos = pos_list[0]
        try:
            grbl_machine.set_position(first_pos)
        except pygrbl.PyGRBLException as e:
            pygrbl_handler.pygrbl_exception(e)
            abort_scan()
            return
    else:
        pos_list = []

    out.init_root(input_dict['output_dir'].value, input_dict['output_name'].value)
    out.create_meta_file(format_meta_data(vna, input_dict['description'].value))

    button_dict['stop'].toggle_state()

    global state
    state = 'scan'

def abort_scan() -> None:
    global abort
    abort = True

    button_dict['stop'].toggle_state()

    global state
    state = 'idle'

def on_button_connect() -> None:
    """Opens the vna resource and checks there is a valid
    connection with it."""
    global vna, grbl_machine

    vna = create_vna(input_dict['address_vna'].value)
    if vna is not None:
        button_dict['calibrate'].set_state(1)
        gui.tab_hardware.set_indicator(0, 'Resource found.', 'blue')

        vna.set_calibration_list()  # Get calibrations from VNA
        calibration.cal_list = vna.calibration_list  # Set them in the GUI
    else:
        button_dict['calibrate'].set_state(0)
        gui.tab_hardware.set_indicator(0, 'Resource not found.', 'red')

    grbl_machine = pygrbl.create_pygrbl_machine(input_dict['address_cnc'].value)
    if grbl_machine is not None:
        button_dict['set_origin'].set_state(1)
        gui.tab_hardware.set_indicator(1, 'Connected.', 'green')
    else:
        button_dict['set_origin'].set_state(0)
        gui.tab_hardware.set_indicator(1, 'Resource not found.', 'red')


def on_apply_calib() -> None:
    """Stores the selected calibration and calibrates the VNA"""
    vna.calibration = calibration.get_selected()
    # Done on thread to prevent gui from freezing
    t = threading.Thread(target=vna.calibrate)
    t.start()

    gui.tab_hardware.set_indicator(0, 'Calibrating...', 'blue')
    gui.core.update_during_thread_wait(t)
    gui.tab_hardware.set_indicator(0, 'Calibrated.', 'green')


def on_set_origin() -> None:
    try:
        grbl_machine.set_origin()
    except pygrbl.PyGRBLException as e:
        pygrbl_handler.pygrbl_exception(e)
        return
    gui.tab_hardware.set_indicator_origin()


def on_button_auto_detect() -> None:
    port_list = serial.tools.list_ports.comports()

    if len(port_list) == 0:
        return

    elif len(port_list) == 1:
        input_dict['address_cnc'].set(port_list[0].name)
