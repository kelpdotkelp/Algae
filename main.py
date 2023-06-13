"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

device0 is the 2-port VNA and 24 port switch
device1 is the 24-port VNA

Author: Noah Stieler, 2023
"""

import gui
import device0
import device1


def main():
    gui.device_select.create_gui()

    gui.device_select.add_device(device0.main, '2-Port VNA and 24-Port Switch (E3-522)')
    gui.device_select.add_device(device1.main, '24-Port VNA (E3-518)')

    while not gui.device_select.app_terminated:
        gui.device_select.update()


if __name__ == '__main__':
    main()
