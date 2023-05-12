"""
Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Please install:
NI-VISA     ->     https://www.ni.com/en-ca/support/downloads/drivers/download.ni-visa.html#480875
NI-488.2    ->     https://www.ni.com/en-ca/support/downloads/drivers/download.ni-488-2.html#467646

NI GPIB setup guide:
https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000x2YDCAY&l=en-CA

Author: Noah Stieler, 2023
"""

import time
import json
import pyvisa as visa
from hardware_imaging import Switches, VNA
import data_handler


GPIB_ADDRESS_VNA = 'GPIB0::16::INSTR'
GPIB_ADDRESS_SWITCHES = 'GPIB::15::INSTR'

OUTPUT_FILE_PATH = 'output_calibration.json'
OUTPUT_JSON_INDENT = '\t'


# TODO Might be useful for debugging: Decorator for timing vna operations
# TODO user input field for meta data to describe what the target is


def main():
    """Initialize VISA resources"""
    # TODO put this in separate function to eliminate visa_ vars from scope
    visa_resource_manager = visa.ResourceManager(r'C:\Windows\system32\visa64.dll')
    visa_vna, visa_switches = None, None

    try:
        visa_vna = visa_resource_manager.open_resource(GPIB_ADDRESS_VNA)
    except visa.errors.VisaIOError:
        print(f'Resource not found: {GPIB_ADDRESS_VNA}')

    try:
        visa_switches = visa_resource_manager.open_resource(GPIB_ADDRESS_SWITCHES)
    except visa.errors.VisaIOError:
        print(f'Resource not found: {GPIB_ADDRESS_SWITCHES}')
        exit()

    vna = VNA(visa_vna)
    vna.initialize()
    vna.display_on(False)

    switches = Switches(visa_switches)
    switches.initialize()

    # TODO turn the meta data / JSON into a decorator/wrapper function?
    """Add meta data to JSON file"""
    with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as file:
        file.write('{\n') # Required for JSON formatting
        json_out = json.dumps(data_handler.format_meta_data(vna), indent=OUTPUT_JSON_INDENT)
        file.write('\"meta\": ' + json_out + ',\n')

    # Multiple scans and position changes will go in here
    start_time = time.time()
    execute_scan(vna, switches)
    end_time = time.time()

    with open(OUTPUT_FILE_PATH, 'a', encoding='utf-8') as file:
        file.write('\n}') # Required for JSON formatting

    print(f'\ntime elapsed= {end_time - start_time} seconds')


def execute_scan(vna, switches, pos_x=0, pos_y=0, scan_index=1):
    """Performs a full scan of the target at the given positions.
    Cycles through all antenna transmission/reflection pairs and appends
    the data to the JSON output"""
    sweeps = {'pos': [pos_x, pos_y]}

    for port_tran in range(Switches.PORT_MIN, Switches.PORT_MAX + 1):
        switches.set_tran(port_tran)

        for port_refl in range(Switches.PORT_MIN, Switches.PORT_MAX + 1):
            if port_refl == port_tran:
                continue

            switches.set_refl(port_refl)

            vna_output = vna.fire()
            # Convert output from string to a list of floats
            vna_output = data_handler.format_data_one_sweep(vna_output, vna.freq_list)

            # Add sweep to dictionary in preparation for JSON output
            try:
                sweeps[f't{port_tran}r{port_refl}'] = (vna_output)
            except data_handler.MissingDataException as error:
                error.display_message()
                quit()

            print(f't{port_tran}r{port_refl}', end='')
            print(sweeps[f't{port_tran}r{port_refl}'])

    # We now have a full scan stored in sweeps
    output_json = json.dumps(sweeps, indent=OUTPUT_JSON_INDENT)

    with open(OUTPUT_FILE_PATH, 'a', encoding='utf-8') as file:
        file.write(f'\"scan{scan_index}\": ')
        file.write(output_json)


if __name__ == '__main__':
    main()
