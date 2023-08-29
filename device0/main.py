"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Please install:
NI-VISA     ->     https://www.ni.com/en-ca/support/downloads/drivers/download.ni-visa.html#480875
NI-488.2    ->     https://www.ni.com/en-ca/support/downloads/drivers/download.ni-488-2.html#467646

NI GPIB setup guide:
https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000x2YDCAY&l=en-CA


--- Known bug ---
VisaIOError: VI_ERROR_INV_OBJECT
Thrown when:
    1. Valid hardware is set up
    2. USB is disconnected
Thrown by: pyvisa/highlevel.py
-Not sure how to fix something thrown within the package
-Not a fatal error either as everything works if USB is
    connected again

Author: Noah Stieler, 2023
"""

import tkinter as tk
import serial.tools.list_ports
from datetime import date, datetime

import gui
from gui.button import button_dict
from gui.parameter import input_dict
import out
from display_resources import display_resources
from . import canvas
from .imaging import *
from .input_validate import input_validate
import pygrbl
from . import pygrbl_handler

abort = False

WORKING_AREA_RADIUS = 120  # Default for this device
WORKING_AREA_PADDING = 20  # Default for this device
pos_list = []
pos_index = 0

grbl_machine = None

state = 'idle'

tran_range = (Switches.PORT_MIN, Switches.PORT_MAX)
refl_range = (Switches.PORT_MIN, Switches.PORT_MAX)
port_tran = tran_range[0]
port_refl = refl_range[0]

vna, switches = None, None


def main() -> None:
    global port_tran, port_refl
    global state
    global pos_list, pos_index

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
    input_dict['address_vna'] = gui.tab_hardware.add_hardware('VNA', default_value='GPIB0::16::INSTR')
    input_dict['address_switch'] = gui.tab_hardware.add_hardware('Switches', default_value='GPIB0::15::INSTR')

    input_dict['address_serial'], button_dict['auto_detect'] = \
        gui.tab_hardware.add_hardware('CNC', default_value='',
                                      action=True, action_name='Auto-detect')
    input_dict['wa_radius'].set(WORKING_AREA_RADIUS)
    input_dict['wa_pad'].set(WORKING_AREA_PADDING)

    # Define button functionality
    button_dict['connect'].command(on_button_connect)
    button_dict['disp_res'].command(display_resources)
    button_dict['run'].command(on_button_run)
    button_dict['stop'].command(abort_scan)

    button_dict['set_origin'].command(on_set_origin)
    button_dict['set_origin'].set_state(0)

    button_dict['auto_detect'].command(on_button_auto_detect)
    button_dict['auto_detect'].set_state(1)

    """     
        Main application loop   
    """
    while not gui.core.app_terminated:
        gui.core.update()
        gui.tab_home.draw_canvas(canvas.update)

        pygrbl_handler.update_chamber()

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
                    vna_output[s_parameter] = VNA.format_data_one_sweep(vna_output[s_parameter], vna.freq_list)
                except MissingDataException as error:
                    gui.bottom_bar.message_display(error.get_message(), 'red')
                    abort_scan()

            if not abort:
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

                if scan_finished:
                    state = scan_finished

        if state == 'scan_finished':
            for s_parameter in vna.sp_to_measure:
                out.out_file_complete(s_parameter)

            # All positions visited
            if pos_index + 1 >= len(pos_list):
                if input_dict['cnc_enable'].value:
                    try:
                        grbl_machine.set_position(pygrbl.Point(0, 0))
                        canvas.set_target_pos(0, 0)
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
                    canvas.set_target_pos(pos.x, pos.y)
                except pygrbl.PyGRBLException as e:
                    pygrbl_handler.pygrbl_exception(e)
                    abort_scan()

                if not abort:
                    # Set up new output folder
                    out.mkdir_new_pos()
                    for s_parameter in vna.sp_to_measure:
                        meta_dict = format_meta_data(s_parameter,
                                                                  pos.x, pos.y)
                        out.out_file_init(s_parameter, meta_dict, vna.freq_list)

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

    global abort
    abort = False

    """Check that hardware is connected and ready."""
    if vna is None or switches is None or grbl_machine is None:
        gui.bottom_bar.message_display('Hardware setup failed.', 'red')
        return

    valid = input_validate(vna, grbl_machine)
    if not valid:
        return

    gui.bottom_bar.message_clear()

    """Initialize hardware"""
    vna.initialize()

    """Set up positioning"""
    pygrbl.set_chamber(pygrbl_handler.chamber)

    global pos_list, pos_index
    first_pos = pygrbl.Point(0, 0)
    if input_dict['cnc_enable'].value:
        if input_dict['pos_gen_type'].value == 'random uniform 2d':
            pos_list = pygrbl.ChamberCircle2D.gen_rand_uniform(input_dict['num_pos'].value,
                                                               pygrbl_handler.chamber.true_radius,
                                                               order='nearest_neighbour')
        elif input_dict['pos_gen_type'].value == 'list':
            pos_list = pygrbl.load_csv(input_dict['pos_list_path'].value, 2)

        first_pos = pos_list[0]

        try:
            grbl_machine.set_position(first_pos)
            canvas.set_target_pos(first_pos.x, first_pos.y)
        except pygrbl.PyGRBLException as e:
            pygrbl_handler.pygrbl_exception(e)
            abort_scan()
            return
    else:
        pos_list = []

    """Initialize output file structure"""
    out.init_root(input_dict['output_dir'].value, input_dict['output_name'].value)
    out.mkdir_new_pos(first_position=True)

    for s_parameter in vna.sp_to_measure:
        meta_dict = format_meta_data(s_parameter, first_pos.x, first_pos.y)
        out.out_file_init(s_parameter, meta_dict, vna.freq_list)

    """Initialize switches"""
    global port_tran, port_refl
    port_tran = tran_range[0]
    port_refl = refl_range[0]
    switches.initialize()

    button_dict['stop'].toggle_state()

    global state
    state = 'scan'


def abort_scan() -> None:
    global abort
    abort = True

    for s_parameter in vna.sp_to_measure:
        out.out_file_complete(s_parameter)

    gui.bottom_bar.progress_bar_set(0)
    button_dict['stop'].toggle_state()

    canvas.port_reset()

    global state
    state = 'idle'


def on_button_connect() -> None:
    """Opens the vna and switches resources and checks there is a valid
    connection with them."""
    global vna, switches, grbl_machine
    valid = [False, False, False]

    vna = create_vna(input_dict['address_vna'].value)
    if vna is not None:
        valid[0] = True

    switches = create_switches(input_dict['address_switch'].value)
    if switches is not None:
        valid[1] = True

    grbl_machine = pygrbl.create_pygrbl_machine(input_dict['address_serial'].value)
    if grbl_machine is not None:
        valid[2] = True
        button_dict['set_origin'].set_state(1)
    else:
        button_dict['set_origin'].set_state(0)

    for i in range(len(valid)):
        if valid[i]:
            gui.tab_hardware.set_indicator(i, 'Connected.', 'green')
        else:
            gui.tab_hardware.set_indicator(i, 'Resource not found.', 'red')


def update_progress_bar() -> None:
    if len(pos_list) == 0:
        return

    try:
        gui.bottom_bar.progress_bar_set(pos_index / len(pos_list))
    except tk.TclError:
        pass


def on_button_auto_detect() -> None:
    port_list = serial.tools.list_ports.comports()

    if len(port_list) == 0:
        return

    elif len(port_list) == 1:
        input_dict['address_serial'].set(port_list[0].name)


def on_set_origin() -> None:
    try:
        grbl_machine.set_origin()
    except pygrbl.PyGRBLException as e:
        pygrbl_handler.pygrbl_exception(e)
        abort_scan()
        return
    canvas.set_state_origin(False)
    gui.tab_hardware.set_indicator_origin()


def format_meta_data(s_parameter: str, posx: float = 0, posy: float = 0) -> dict:
    """Returns the correctly structured dictionary that can later
    be incorporated into JSON format"""
    out_dict = {
        's_parameter': s_parameter,
        'freq_start': input_dict['freq_start'].value,
        'freq_stop': input_dict['freq_stop'].value,
        'if_bandwidth': input_dict['ifbw'].value,
        'num_points': input_dict['num_points'].value,
        'power': input_dict['power'].value,
        'posx': posx,
        'posy': posy,
        'vna_name': vna.name,
        'date': str(date.today()),
        'time': (datetime.now()).strftime('%H:%M:%S'),
        'description': input_dict['description'].value,
        'rotation': input_dict['rotation'].value
    }
    return out_dict


def _debug_play_graphics() -> None:
    import time
    update_ports()
    update_progress_bar()
    time.sleep(0.25)
