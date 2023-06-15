"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Creates a popup window that lists all connected
VISA resources.

Author: Noah Stieler, 2023
"""

import pyvisa as visa

import gui


def visa_display_resources() -> None:
    """Lists available resources and creates a popup to display them."""
    visa_resource_manager = visa.ResourceManager()
    r_list = visa_resource_manager.list_resources()
    r_display = ''
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
        r_display = 'No resources found.'

    gui.core.create_popup(r_display, 'Resource Finder')
