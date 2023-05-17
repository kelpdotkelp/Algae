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

OUTPUT_FILE_PATH = 'output_test_may17.json'
OUTPUT_JSON_INDENT = '\t'


# TODO Might be useful for debugging: Decorator for timing vna operations
# TODO user input field for meta data to describe what the target is
# TODO ability to measure and output all S-parameters
# TODO user defined trans/refl ranges


def main():
    """Initialize VISA resources"""
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

    """Add meta data and list of frequencies to JSON file"""
    with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as file:
        file.write('{\n') # Required for JSON formatting
        json_out = json.dumps(data_handler.format_meta_data(vna), indent=OUTPUT_JSON_INDENT)
        file.write('\"meta\": ' + json_out + ',\n')
        json_out = json.dumps(vna.freq_list)
        file.write('\"freq\": ' + json_out + ',\n')

    # Multiple scans and position changes will go in here
    start_time = time.time()
    execute_scan(vna, switches)
    end_time = time.time()

    with open(OUTPUT_FILE_PATH, 'a', encoding='utf-8') as file:
        file.write('\n}') # Required for JSON formatting

    print(f'\ntime elapsed= {end_time - start_time} seconds')


def execute_scan(vna, switches):
    """Performs a full scan of the target at the given positions.
    Cycles through all antenna transmission/reflection pairs and appends
    the data to the JSON output.
    Not using json module to format because this formatting style is not provided."""
    tran_range = (Switches.PORT_MIN, Switches.PORT_MAX)
    refl_range = (Switches.PORT_MIN, Switches.PORT_MAX)

    with open(OUTPUT_FILE_PATH, 'a', encoding='utf-8') as file:
        file.write('"data": {\n')

    for port_tran in range(tran_range[0], tran_range[1]+1):
        switches.set_tran(port_tran)

        for port_refl in range(refl_range[0], refl_range[1]+1):
            if port_refl == port_tran:
                continue

            switches.set_refl(port_refl)
            vna_output = vna.fire()

            try:
                # Convert output from string to a list of floats
                vna_output = data_handler.format_data_one_sweep(vna_output, vna.freq_list)
            except data_handler.MissingDataException as error:
                error.display_message()
                quit()

            with open(OUTPUT_FILE_PATH, 'a', encoding='utf-8') as file:
                file.write(OUTPUT_JSON_INDENT + f'"t{port_tran}r{port_refl}"' + ': {\n')
                file.write(2*OUTPUT_JSON_INDENT + '"real": ' + str(vna_output[0]) + ',\n')
                file.write(2*OUTPUT_JSON_INDENT + '"imag": ' + str(vna_output[1]))

                if port_tran == tran_range[1] and port_refl == refl_range[1]-1:
                    file.write('\n' + 2*OUTPUT_JSON_INDENT + '}\n}')  # Close data section
                else:
                    file.write('\n' + 2*OUTPUT_JSON_INDENT + '},\n')

            print(f't{port_tran}r{port_refl}', end='')


if __name__ == '__main__':
    main()
