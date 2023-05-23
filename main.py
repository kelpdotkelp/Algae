import pyvisa

import gui
import pyvisa as visa
from hardware_imaging import VNA, Switches

PATH_VISA_LIBRARY = r'C:\Windows\system32\visa64.dll'

vna, switches = None, None
_e_vna, _e_switches = None, None


# TODO display should be turned back on after scan
# I think VNA software crashes if you shut down while display is off.

def main():
    gui.core.create_gui()

    e_num_points = gui.tab_home.add_parameter('Number of points')
    e_if_bandwidth = gui.tab_home.add_parameter('IF bandwidth (Hz)')
    e_start_freq = gui.tab_home.add_parameter('Start frequency (Hz)')
    e_stop_freq = gui.tab_home.add_parameter('Stop frequency (Hz)')
    e_power = gui.tab_home.add_parameter('Power (dBm)')

    global _e_vna, _e_switches
    _e_vna = gui.tab_hardware.add_hardware('VNA', default_value='GPIB0::16::INSTR')
    _e_switches = gui.tab_hardware.add_hardware('Switches', default_value='GPIB0::15::INSTR')
    gui.tab_hardware.on_hardware_scan(scan_for_hardware)
    gui.tab_hardware.on_check_connection(check_connections)

    while not gui.core.app_terminated:
        gui.core.update()


def scan_for_hardware():
    visa_resource_manager = visa.ResourceManager(PATH_VISA_LIBRARY)
    r_list = visa_resource_manager.list_resources()
    visa_vna, visa_switches = None, None

    if _e_vna.get() in r_list:
        visa_vna = visa_resource_manager.open_resource(_e_vna.get())
        global vna
        vna = VNA(visa_vna)
        gui.tab_hardware.set_indicator(0, 'Resource found.', 'green')
    else:
        gui.tab_hardware.set_indicator(0, 'Resource not found.', 'red')

    if _e_switches.get() in r_list:
        visa_switches = visa_resource_manager.open_resource(_e_switches.get())
        global switches
        switches = Switches(visa_switches)
        gui.tab_hardware.set_indicator(1, 'Resource found.', 'green')
    else:
        gui.tab_hardware.set_indicator(1, 'Resource not found.', 'red')


def check_connections():
    visa_resource_manager = pyvisa.ResourceManager()
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


if __name__ == '__main__':
    main()
