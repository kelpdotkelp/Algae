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

# TODO crash when collecting incident and then running again
# TODO check box for incident field scan

import tkinter as tk
import serial.tools.list_ports

import gui
from gui.parameter import input_dict
from gui.button import button_dict
import out
from cnc import *
from display_resources import display_resources

from . import data_handler
from . import canvas
from .imaging import *
from .input_validate import input_validate

WORKING_AREA_RADIUS = 120
WORKING_AREA_PADDING = 20

state = 'idle'

tran_range = (Switches.PORT_MIN, Switches.PORT_MAX)
refl_range = (Switches.PORT_MIN, Switches.PORT_MAX)
port_tran = tran_range[0]
port_refl = refl_range[0]

vna, switches, cnc = None, None, None


def main() -> None:
    global port_tran, port_refl
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

        update_target_dim()

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

            if scan_finished:
                state = scan_finished

        if state == 'scan_finished':
            for s_parameter in vna.sp_to_measure:
                out.out_file_complete(s_parameter)

            if cnc.pos_index + 1 >= len(cnc.pos_list):
                try:
                    cnc.set_position(cnc.pos, Point(0, 0))
                    canvas.set_target_pos(cnc.pos.x, cnc.pos.y)
                except CNCException as e:
                    e.display()
                    abort_scan()
                    return

                button_dict['stop'].toggle_state()

                state = 'idle'
            else:
                # Go to next position
                try:
                    cnc.next_position()
                    canvas.set_target_pos(cnc.pos.x, cnc.pos.y)
                except CNCException as e:
                    e.display()
                    abort_scan()
                    return

                # Set up new output folder
                out.mkdir_new_pos()
                for s_parameter in vna.sp_to_measure:
                    meta_dict = data_handler.format_meta_data(vna, s_parameter,
                                                              cnc.pos.x, cnc.pos.y)
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

    """Check that hardware is connected and ready."""
    if vna is None or switches is None or cnc is None:
        gui.bottom_bar.message_display('Hardware setup failed.', 'red')
        return

    valid = input_validate(vna, cnc)
    if not valid:
        return

    gui.bottom_bar.message_clear()

    """Initialize hardware"""
    vna.initialize()
    cnc.initialize()

    try:
        cnc.next_position()
        canvas.set_target_pos(cnc.pos.x, cnc.pos.y)
    except CNCException as e:
        e.display()
        return

    """Initialize output file structure"""
    out.init_root(input_dict['output_dir'].value, input_dict['output_name'].value)
    out.mkdir_new_pos(first_position=True)

    for s_parameter in vna.sp_to_measure:
        meta_dict = data_handler.format_meta_data(vna, s_parameter,
                                                  cnc.pos.x, cnc.pos.y)
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
    global vna, switches, cnc
    valid = [False, False, False]

    vna = create_vna(input_dict['address_vna'].value)
    if vna is not None:
        valid[0] = True

    switches = create_switches(input_dict['address_switch'].value)
    if switches is not None:
        valid[1] = True

    cnc = create_cnc(input_dict['address_serial'].value)
    if cnc is not None:
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
    if len(cnc.pos_list) == 0:
        return

    try:
        gui.bottom_bar.progress_bar_set(cnc.pos_index / len(cnc.pos_list))
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
        cnc.set_origin()
    except CNCException as e:
        e.display()
        return
    canvas.set_state_origin(False)
    gui.tab_hardware.set_indicator_origin()


def _debug_play_graphics() -> None:
    import time
    update_ports()
    update_progress_bar()
    time.sleep(0.25)
