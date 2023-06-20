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
import tkinter as tk
import pyvisa as visa
import serial.tools.list_ports

import gui
from gui.parameter import input_dict
import out
from cnc import Point, CNC
from display_resources import display_resources

from . import data_handler
from . import canvas
from .imaging import VNA, Switches
from .input_validate import input_validate

state = 'idle'

tran_range = (Switches.PORT_MIN, Switches.PORT_MAX)
refl_range = (Switches.PORT_MIN, Switches.PORT_MAX)
port_tran = tran_range[0]
port_refl = refl_range[0]

vna, switches = None, None

cnc = CNC()
_button_auto_detect = None

pos_list = [Point(20, 20),
            Point(-20, 20),
            Point(-20, -20),
            Point(20, -20)]
pos_index = 0

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

# TODO object dimensions
# TODO point circle, linear spaced
# TODO pick individual points
# TODO Origin set
"""

Check boxes to select object type - circular, rectangular


Show origin on gui
    Red cross when origin is not set
Show positions on gui

"""


def main() -> None:
    global state

    gui.core.create_gui()

    # Set up input parameters
    input_dict['num_points'] = gui.tab_home.add_parameter_num('Number of points')
    input_dict['ifbw'] = gui.tab_home.add_parameter_num('IF bandwidth (Hz)')
    input_dict['freq_start'] = gui.tab_home.add_parameter_num('Start frequency (Hz)')
    input_dict['freq_stop'] = gui.tab_home.add_parameter_num('Stop frequency (Hz)')
    input_dict['power'] = gui.tab_home.add_parameter_num('Power (dBm)')

    gui.tab_home.checkbox_row_begin()
    input_dict['S11'] = gui.tab_home.add_parameter_checkbox('S11')
    input_dict['S12'] = gui.tab_home.add_parameter_checkbox('S12')
    input_dict['S21'] = gui.tab_home.add_parameter_checkbox('S21')
    input_dict['S22'] = gui.tab_home.add_parameter_checkbox('S22')
    gui.tab_home.checkbox_row_end()

    input_dict['S21'].toggle()

    # Set up hardware gui
    global _button_auto_detect
    input_dict['address_vna'] = gui.tab_hardware.add_hardware('VNA', default_value='GPIB0::16::INSTR')
    input_dict['address_switch'] = gui.tab_hardware.add_hardware('Switches', default_value='GPIB0::15::INSTR')

    input_dict['address_serial'], _button_auto_detect = \
        gui.tab_hardware.add_hardware('CNC', default_value='',
                                      action=True, action_name='Auto-detect')

    _button_auto_detect['state'] = tk.ACTIVE
    _button_auto_detect.configure(command=on_button_auto_detect)

    # Define button functionality
    gui.tab_hardware.on_connect(on_button_connect)
    gui.tab_hardware.on_display_resources(display_resources)
    gui.bottom_bar.on_button_run(on_button_run)
    gui.bottom_bar.on_button_stop(abort_scan)

    """     
        Main application loop   
    """
    while not gui.core.app_terminated:
        global port_tran, port_refl

        gui.core.update()

        gui.tab_home.draw_canvas(canvas.update)

        # _debug_play_graphics()

        if state == 'idle':
            gui.parameter.update()
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

            # Write to output files
            for s_parameter in vna.sp_to_measure:
                data_close = False
                if port_tran == tran_range[1] and port_refl == refl_range[1] - 1:
                    data_close = True

                out.out_file_data_write(s_parameter, port_tran, port_refl,
                                        vna_output[s_parameter][0],
                                        vna_output[s_parameter][1], data_close)

            scan_finished = update_ports()
            update_progress_bar()

        if state == 'scan_finished':
            for s_parameter in vna.sp_to_measure:
                out.out_file_complete(s_parameter)

            global pos_index
            pos_index += 1

            if pos_index >= len(pos_list):
                vna.close()
                switches.close()

                cnc.set_position(Point(0, 0))

                gui.bottom_bar.toggle_button_stop()

                state = 'idle'
            else:
                # Set up new output folder
                out.mkdir_new_pos()
                for s_parameter in vna.sp_to_measure:
                    meta_dict = data_handler.format_meta_data(vna, s_parameter,
                                                              pos_list[pos_index].x, pos_list[pos_index].y)
                    out.out_file_init(s_parameter, meta_dict, vna.freq_list)

                cnc.set_position(pos_list[pos_index])

                port_tran = tran_range[0]
                port_refl = refl_range[0]

                state = 'scan'

            gui.bottom_bar.progress_bar_set(0)


def update_ports() -> bool:
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


def on_button_run() -> None:
    """Begins a scan.
    Checks that hardware is connected and ready,
    that all user input is valid, and sets up output directory and files.
    Assuming no user errors, state is changed to 'scan'."""

    """Check that hardware is connected and ready."""
    if vna is None or switches is None or cnc.ser is None:
        gui.bottom_bar.message_display('Hardware setup failed.', 'red')
        return

    valid = input_validate(vna)
    if not valid:
        return

    gui.bottom_bar.message_clear()

    vna.initialize()

    """Initialize CNC"""
    global pos_index
    pos_index = 0

    """TEMP"""
    cnc.set_origin()
    cnc.set_position(pos_list[pos_index])

    """Initialize output file structure"""
    out.init_root(input_dict['output_dir'].value, input_dict['output_name'].value)
    out.mkdir_new_pos()

    for s_parameter in vna.sp_to_measure:
        meta_dict = data_handler.format_meta_data(vna, s_parameter,
                                                  pos_list[pos_index].x, pos_list[pos_index].y)
        out.out_file_init(s_parameter, meta_dict, vna.freq_list)

    """Initialize switches"""
    global port_tran, port_refl
    port_tran = tran_range[0]
    port_refl = refl_range[0]
    switches.initialize()

    gui.bottom_bar.toggle_button_stop()

    global state
    state = 'scan'


def abort_scan() -> None:
    for s_parameter in vna.sp_to_measure:
        out.out_file_complete(s_parameter)

    gui.bottom_bar.progress_bar_set(0)
    gui.bottom_bar.toggle_button_stop()

    canvas.port_reset()

    global state
    state = 'idle'


def on_button_connect() -> None:
    """Opens the vna and switches resources and checks there is a valid
    connection with them."""
    visa_resource_manager = visa.ResourceManager()
    r_list = visa_resource_manager.list_resources()
    global vna, switches

    if input_dict['address_vna'].value in r_list:
        visa_vna = visa_resource_manager.open_resource(input_dict['address_vna'].value)
        vna = VNA(visa_vna)
        gui.tab_hardware.set_indicator(0, 'Connected.', 'green')
    else:
        vna = None
        gui.tab_hardware.set_indicator(0, 'Resource not found.', 'red')

    if input_dict['address_switch'].value in r_list:
        visa_switches = visa_resource_manager.open_resource(input_dict['address_switch'].value)
        switches = Switches(visa_switches)
        gui.tab_hardware.set_indicator(1, 'Connected.', 'green')
    else:
        switches = None
        gui.tab_hardware.set_indicator(1, 'Resource not found.', 'red')

    global cnc
    cnc = CNC()
    success = cnc.connect(input_dict['address_serial'].value)
    if success:
        gui.tab_hardware.set_indicator(2, 'Connected.', 'green')
    else:
        gui.tab_hardware.set_indicator(2, 'Resource not found.', 'red')


def update_progress_bar() -> None:
    try:
        pair_count = tran_range[1] * (refl_range[1] - 1)
        gui.bottom_bar.progress_bar_set((port_tran * 24 - 1 + port_refl) / pair_count)
    except tk.TclError:
        pass


def on_button_auto_detect() -> None:
    port_list = serial.tools.list_ports.comports()

    if len(port_list) == 0:
        return

    elif len(port_list) == 1:
        input_dict['address_serial'].set(port_list[0].name)


def _debug_play_graphics() -> None:
    import time
    update_ports()
    update_progress_bar()
    time.sleep(0.25)
