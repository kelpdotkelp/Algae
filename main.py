"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

device0 is the 2D cross-section scanner
device1 is the electromagnet scanner

Author: Noah Stieler, 2023
"""

import gui
import device0
import device1

# TODO Remove PATH_VISA_LIBRARY

def main():
    gui.device_select.create_gui()

    gui.device_select.add_device(device0.main, '2D Cross-section (E3-522)')
    gui.device_select.add_device(device1.main, 'Electromagnet (E3-518)')

    while not gui.device_select.app_terminated:
        gui.device_select.update()


if __name__ == '__main__':
    main()
