"""
Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Provides the class VNA and Switches which provides an
interface for setting up and controlling each device.

Hardware:
    Agilent E8363B PNA Network Analyzer
    Agilent 87050A Option K24 Multiport Test Set

Author: Noah Stieler, 2023
"""

import time

# TODO query the sweep time and set timeout accordingly
class VNA:
    """Commands follow the SCPI specification"""

    def __init__(self, resource):
        self.resource = resource
        self.name = ""

        self.data_point_count = 10
        self.if_bandwidth = 5 * 1000  # Hz
        self.freq_start = 8 * 1000000000  # Hz
        self.freq_stop = 16 * 1000000000  # Hz
        self.power = 0  # dBm

        self.freq_list = self._freq_list_linspace()

    def initialize(self):
        self.resource.read_termination = '\n'
        self.resource.write_termination = '\n'

        self.name = self.resource.query('*IDN?')

        self.write('SYSTEM:FPRESET')

        self.display_on(False)

        self.write('DISPLAY:WINDOW1:STATE ON')
        self.write('CALCULATE1:PARAMETER:DEFINE \'CH1_1_S21\', S21')
        self.write('DISPLAY:WINDOW1:TRACE1:FEED \'CH1_1_S21\'')

        self.write('DISPLAY:WINDOW2:STATE ON')
        self.write('CALCULATE1:PARAMETER:DEFINE \'CH2_1_S11\', S11')
        self.write('DISPLAY:WINDOW2:TRACE1:FEED \'CH2_1_S11\'')

        self.write('INITIATE:CONTINUOUS OFF')
        self.write('TRIGGER:SOURCE MANUAL')
        self.write('SENSE1:SWEEP:MODE HOLD')
        self.write('SENSE1:AVERAGE OFF')

        self.write('SENSE1:SWEEP:TYPE LINEAR')
        self.write(f'SENSE1:SWEEP:POINTS {self.data_point_count}')
        self.write(f'SENSE1:BANDWIDTH {self.if_bandwidth}')
        self.write(f'SENSE1:FREQUENCY:START {self.freq_start}')
        self.write(f'SENSE1:FREQUENCY:STOP {self.freq_stop}')
        # This is from the old software but the manual has a different syntax
        self.write(f'SOURCE1:POWER1 {self.power}DBM')

        self.resource.timeout = 100 * 1000 #time in milliseconds

    def display_on(self, setting):
        """Old software said VNA runs faster with display off,
        as mentioned in programming guide"""
        if setting:
            self.write('DISPLAY:VISIBLE ON')
        else:
            self.write('DISPLAY:VISIBLE OFF')

    def write(self, cmd):
        self.resource.write(cmd)

    def query(self, cmd):
        return self.resource.query(cmd)

    def fire(self):
        """Trigger the VNA and return the data it collected."""
        self.write('INIT:IMM')
        # vna.send_command('*WAI') # *OPC? might be better because it stops the controller from attempting a read
        self.query('*OPC?')  # Controller waits until all commands are completed.

        self.write('CALCULATE1:PARAMETER:SELECT \'CH2_1_S11\'')
        return self.query('CALCULATE:DATA? SDATA')

    def _freq_list_linspace(self):
        """Returns a list of the frequencies the VNA is sampling at."""
        list = []
        inc = (self.freq_stop - self.freq_start) / (self.data_point_count - 1)
        for i in range(self.data_point_count):
            list.append(self.freq_start + i * inc)
        return list


class Switches:
    """Commands must be terminated with a semicolon
    Previous software said that trans must be set before refl but
    both orders worked in my tests"""
    PORT_MIN = 1
    PORT_MAX = 24

    debounce_time = 0.03  # seconds

    def __init__(self, resource):
        self.resource = resource

    def initialize(self):
        self.write('*rst')  # reset

    def set_tran(self, port):
        """Port indices are 1-24 inclusive"""
        self.write(f'tran_{Switches.pad_port_number(port)};')
        time.sleep(Switches.debounce_time)

    def set_refl(self, port):
        """Port indices are 1-24 inclusive"""
        self.write(f'refl_{Switches.pad_port_number(port)}')
        time.sleep(Switches.debounce_time)

    def write(self, cmd):
        self.resource.write(cmd)

    @staticmethod
    def pad_port_number(port):
        """If the port is less than 9, it must be padded with a
        leading 0 in the command"""
        if port <= 9:
            return '0' + str(port)
        else:
            return str(port)
