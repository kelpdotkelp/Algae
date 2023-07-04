"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Contains the base class for all VISA resources.

Author: Noah Stieler, 2023
"""

import pyvisa as visa


class VisaResource:
    manager: visa.ResourceManager = None

    def __init__(self, address: str):
        if VisaResource.manager is None:
            VisaResource.manager = visa.ResourceManager()

        self.address = address
        self.resource = None

        try:
            self.resource = VisaResource.manager.open_resource(address)
        except visa.VisaIOError:
            pass

    def __del__(self):
        if self.resource is None:
            return

        try:
            self.write('*RST')
            self.resource.close()
        except visa.errors.VisaIOError:
            pass
        except visa.errors.InvalidSession:
            pass

    def write(self, cmd: str) -> None:
        self.resource.write(cmd)

    def query(self, cmd: str) -> str:
        return self.resource.query(cmd)
