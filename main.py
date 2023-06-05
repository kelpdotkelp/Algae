"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

device0 is the 2D cross-section scanner
device_1 is the electromagnet scanner

Author: Noah Stieler, 2023
"""

import gui
import device0


def main():
    gui.device_select.create_gui()

    gui.device_select.add_device(device0.main, 'E3-522')

    while not gui.device_select.app_terminated:
        gui.device_select.update()


if __name__ == '__main__':
    main()
