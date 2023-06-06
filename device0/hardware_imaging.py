"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Provides the class VNA and Switches which provides an
interface for setting up and controlling each device.

VNA commands follow the SCPI specification.

Hardware:
    Agilent E8363B PNA Network Analyzer
    Agilent 87050A Option K24 Multiport Test Set

Author: Noah Stieler, 2023
"""

import time
import pyvisa as visa

from .data_handler import vna_str_to_float


class VNA:

    def __init__(self, resource):
        self.resource = resource
        self.name = ""

        self.sp_to_measure = ['S21']
        self.data_point_count = 5
        self.if_bandwidth = 5 * 1000  # Hz
        self.freq_start = 3 * 1000000000  # Hz
        self.freq_stop = 5 * 1000000000  # Hz
        self.power = 0  # dBm

        self.data_point_count_range = ()
        self.if_bandwidth_range = ()
        self.freq_start_range = ()
        self.freq_stop_range = ()
        self.power_range = ()

        self.freq_list = self._freq_list_linspace()
        self.sweep_time = 0

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

    def close(self):
        # Sending *RST prevents vna software crash
        self.write('*RST')
        self.resource.close()

    def initialize(self):
        self.resource.read_termination = '\n'
        self.resource.write_termination = '\n'

        self.name = self.resource.query('*IDN?')
        self.freq_list = self._freq_list_linspace()

        self.write('SYSTEM:FPRESET')

        self.display_on(False)

        # Using convention that parameter names are prefixed with 'parameter_'
        self.write('CALCULATE1:PARAMETER:DEFINE \'parameter_S11\', S11')
        self.write('CALCULATE1:PARAMETER:DEFINE \'parameter_S12\', S12')
        self.write('CALCULATE1:PARAMETER:DEFINE \'parameter_S21\', S21')
        self.write('CALCULATE1:PARAMETER:DEFINE \'parameter_S22\', S22')

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

        # Kind of arbitrary, chosen like this to ensure plenty of time to complete sweep
        # Extra important if data_point_count is large.
        self.resource.timeout = 100 * 1000  # time in milliseconds

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
        # self.write('*WAI')  # *OPC? might be better because it stops the controller from attempting a read
        self.query('*OPC?')  # Controller waits until all commands are completed.

        # Using convention that parameter names are prefixed with 'parameter_'
        output = {}
        for s_parameter in self.sp_to_measure:
            self.write('CALCULATE1:PARAMETER:SELECT \'' + 'parameter_' + s_parameter + '\'')
            output[s_parameter] = self.query('CALCULATE:DATA? SDATA')

        return output

    def _freq_list_linspace(self):
        """Returns a list of the frequencies the VNA is sampling at."""
        list_out = []
        inc = (self.freq_stop - self.freq_start) / (self.data_point_count - 1)
        for i in range(self.data_point_count):
            list_out.append(self.freq_start + i * inc)
        return list_out

    def set_parameter_ranges(self):
        """Gets all valid parameter ranges from the VNA.
        this is used when the 'run' button is pressed to ensure the
        user submitted valid data."""
        self.resource.read_termination = '\n'
        self.resource.write_termination = '\n'

        # Including these commands first in case
        # this setup changes parameter range.
        self.write('SYSTEM:FPRESET')
        parameter_name = 'parameter_' + self.sp_to_measure[0]
        self.write('CALCULATE1:PARAMETER:DEFINE \'' + parameter_name + '\', ' + self.sp_to_measure[0])
        self.write('INITIATE:CONTINUOUS OFF')
        self.write('TRIGGER:SOURCE MANUAL')
        self.write('SENSE1:SWEEP:MODE HOLD')
        self.write('SENSE1:AVERAGE OFF')
        self.write('SENSE1:SWEEP:TYPE LINEAR')

        self.data_point_count_range = (
            int(self.query('SENSE1:SWEEP:POINTS? MIN')),
            int(self.query('SENSE1:SWEEP:POINTS? MAX'))
        )
        self.if_bandwidth_range = (
            vna_str_to_float(self.query('SENSE1:BANDWIDTH? MIN')),
            vna_str_to_float(self.query('SENSE1:BANDWIDTH? MAX'))
        )
        self.freq_start_range = (
            vna_str_to_float(self.query('SENSE1:FREQUENCY:START? MIN')),
            vna_str_to_float(self.query('SENSE1:FREQUENCY:START? MAX'))
        )
        self.freq_stop_range = (
            vna_str_to_float(self.query('SENSE1:FREQUENCY:STOP? MIN')),
            vna_str_to_float(self.query('SENSE1:FREQUENCY:STOP? MAX'))
        )
        self.power_range = (
            vna_str_to_float(self.query('SOURCE1:POWER1? MIN')),
            vna_str_to_float(self.query('SOURCE1:POWER1? MAX'))
        )


class Switches:
    """Commands must be terminated with a semicolon
    Previous software said that trans must be set before refl but
    both orders worked in my tests"""
    PORT_MIN = 1
    PORT_MAX = 24

    debounce_time = 0.03  # seconds

    def __init__(self, resource):
        self.resource = resource

    def __del__(self):
        if self.resource is None:
            return

        try:
            self.resource.close()
        except visa.errors.VisaIOError:
            pass
        except visa.errors.InvalidSession:
            pass

    def close(self):
        self.resource.close()

    def initialize(self):
        self.write('*rst')  # reset

    def set_tran(self, port):
        """Port indices are 1-24 inclusive"""
        if port < Switches.PORT_MIN or port > Switches.PORT_MAX:
            raise SwitchInvalidPortException(port)

        self.write(f'tran_{Switches.pad_port_number(port)};')
        time.sleep(Switches.debounce_time)

    def set_refl(self, port):
        """Port indices are 1-24 inclusive"""
        if port < Switches.PORT_MIN or port > Switches.PORT_MAX:
            raise SwitchInvalidPortException(port)

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


class SwitchInvalidPortException(Exception):
    """Raised when attempting to set the switch port outside
    the allowed range."""

    def __init__(self, attempted_port):
        self.attempted_port = attempted_port

    def display_message(self):
        print(f'SwitchInvalidPortException:'
              f'\n\tPort {self.attempted_port} is invalid.')
