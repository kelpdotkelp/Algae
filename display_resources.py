"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Creates a popup window that lists all connected
VISA and USB resources.

Author: Noah Stieler, 2023
"""

import pyvisa as visa
import serial.tools.list_ports

import gui


def display_resources() -> None:
    """Lists available resources and creates a popup to display them."""
    visa_resource_manager = visa.ResourceManager()
    r_list = visa_resource_manager.list_resources()
    r_display = 'VISA:\n'
    for address in r_list:

        try:
            resource = visa_resource_manager.open_resource(address)
            if hasattr(resource, 'query'):
                r_display = r_display + address + '\n\t' + resource.query('*IDN?') + '\n'
            else:
                r_display = r_display + address + '\n\t' + r'N\A' + '\n'
        except visa.errors.VisaIOError:
            r_display = r_display + address + '\n\t' + r'N\A' + '\n'
    if len(r_list) == 0:
        r_display = r_display + '\tNo resources found.\n'

    r_display = r_display + 'Serial:\n'
    port_list = serial.tools.list_ports.comports()

    for port in port_list:
        r_display = r_display + port.name + '\n\t' + port.description + '\n'

    if len(port_list) == 0:
        r_display = r_display + '\tNo resources found.\n'

    gui.core.create_popup(r_display, 'Resource Finder')
