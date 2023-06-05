"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

device_0 is the 2D cross-section scanner
device_1 is the electromagnet scanner

Author: Noah Stieler, 2023
"""

import gui
from device_0.main import main as main_device_0


def main():
    gui.device_select.create_gui()

    gui.device_select.add_device(main_device_0, 'E3-522')

    while not gui.device_select.app_terminated:
        gui.device_select.update()


if __name__ == '__main__':
    main()
