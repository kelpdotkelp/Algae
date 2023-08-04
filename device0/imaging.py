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

from visa import VisaResource
from gui.parameter import input_dict


class VNA(VisaResource):
    s_params = ['S11', 'S21', 'S12', 'S22']

    def __init__(self, address: str):
        super().__init__(address)

        if self.resource is None:
            return

        self.name = ""

        self.sp_to_measure = []
        self.p_ranges = {}

        self._set_parameter_ranges()

    @property
    def freq_list(self) -> list:
        li = []
        inc = (input_dict['freq_stop'].value - input_dict['freq_start'].value) / (input_dict['num_points'].value - 1)
        for i in range(int(input_dict['num_points'].value)):
            li.append(input_dict['freq_start'].value + i * inc)
        return li

    def __del__(self):
        super().__del__()

    def initialize(self) -> None:
        self.resource.read_termination = '\n'
        self.resource.write_termination = '\n'

        self.name = self.query('*IDN?')

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
        self.write('SENSE1:SWEEP:POINTS ' + str(int(input_dict['num_points'].value)))
        self.write('SENSE1:BANDWIDTH ' + str(input_dict['ifbw'].value))
        self.write('SENSE1:FREQUENCY:START ' + str(input_dict['freq_start'].value))
        self.write('SENSE1:FREQUENCY:STOP ' + str(input_dict['freq_stop'].value))
        # This is from the old software but the manual has a different syntax
        self.write('SOURCE1:POWER1 ' + str(input_dict['power'].value) + 'DBM')

        # Kind of arbitrary, chosen like this to ensure plenty of time to complete sweep
        # Extra important if data_point_count is large.
        self.resource.timeout = 100 * 1000  # time in milliseconds

        self.sp_to_measure = []
        for s_param in VNA.s_params:
            if s_param in input_dict:
                if input_dict[s_param].value == 1:
                    self.sp_to_measure.append(s_param)

    def display_on(self, setting: bool) -> None:
        """Old software said VNA runs faster with display off,
        as mentioned in programming guide"""
        if setting:
            self.write('DISPLAY:VISIBLE ON')
        else:
            self.write('DISPLAY:VISIBLE OFF')

    def fire(self) -> dict:
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

    def _set_parameter_ranges(self) -> None:
        """Gets all valid parameter ranges from the VNA.
        this is used when the 'run' button is pressed to ensure the
        user submitted valid data."""
        self.resource.read_termination = '\n'
        self.resource.write_termination = '\n'

        # Testing has confirmed this set up is required.
        self.write('SYSTEM:FPRESET')
        parameter_name = 'parameter_S21'
        self.write('CALCULATE1:PARAMETER:DEFINE \'' + parameter_name + '\', S21')
        self.write('INITIATE:CONTINUOUS OFF')
        self.write('TRIGGER:SOURCE MANUAL')
        self.write('SENSE1:SWEEP:MODE HOLD')
        self.write('SENSE1:AVERAGE OFF')
        self.write('SENSE1:SWEEP:TYPE LINEAR')

        self.p_ranges['num_points'] = (
            int(self.query('SENSE1:SWEEP:POINTS? MIN')),
            int(self.query('SENSE1:SWEEP:POINTS? MAX'))
        )
        self.p_ranges['ifbw'] = (
            float(self.query('SENSE1:BANDWIDTH? MIN')),
            float(self.query('SENSE1:BANDWIDTH? MAX'))
        )
        self.p_ranges['freq_start'] = (
            float(self.query('SENSE1:FREQUENCY:START? MIN')),
            float(self.query('SENSE1:FREQUENCY:START? MAX'))
        )
        self.p_ranges['freq_stop'] = (
            float(self.query('SENSE1:FREQUENCY:STOP? MIN')),
            float(self.query('SENSE1:FREQUENCY:STOP? MAX'))
        )
        self.p_ranges['power'] = (
            float(self.query('SOURCE1:POWER1? MIN')),
            float(self.query('SOURCE1:POWER1? MAX'))
        )

    @staticmethod
    def format_data_one_sweep(str_points: str, freq_list: list) -> list:
        """Returns a list that contains lists of the real and imaginary
        components at each frequency."""
        float_points = str_points.split(',')

        for i in range(len(float_points)):
            float_points[i] = float(float_points[i])

        # Check to ensure no data is missing from vna
        if len(float_points) != 2 * len(freq_list):
            raise MissingDataException(len(float_points), 2 * len(freq_list))

        measurement_set = [[], []]

        for i in range(len(freq_list)):
            # measurement_set.append([freq_list[i], float_points[2 * i], float_points[1 + 2 * i]])
            measurement_set[0].append(float_points[2 * i])  # Real
            measurement_set[1].append(float_points[1 + 2 * i])  # Imaginary

        return measurement_set


class Switches(VisaResource):
    """Commands must be terminated with a semicolon
    Previous software said that trans must be set before refl but
    both orders worked in my tests"""
    PORT_MIN = 1
    PORT_MAX = 5

    debounce_time = 0.03  # seconds

    def __init__(self, address: str):
        super().__init__(address)

    def __del__(self):
        super().__del__()

    def initialize(self) -> None:
        self.write('*rst')  # reset

    def set_tran(self, port: int) -> None:
        """Port indices are 1-24 inclusive"""
        if port < Switches.PORT_MIN or port > Switches.PORT_MAX:
            raise SwitchInvalidPortException(port)

        self.write(f'tran_{Switches.pad_port_number(port)};')
        time.sleep(Switches.debounce_time)

    def set_refl(self, port: int) -> None:
        """Port indices are 1-24 inclusive"""
        if port < Switches.PORT_MIN or port > Switches.PORT_MAX:
            raise SwitchInvalidPortException(port)

        self.write(f'refl_{Switches.pad_port_number(port)}')
        time.sleep(Switches.debounce_time)

    @staticmethod
    def pad_port_number(port: int) -> str:
        """If the port is less than 9, it must be padded with a
        leading 0 in the command"""
        if port <= 9:
            return '0' + str(port)
        else:
            return str(port)


def create_vna(address: str) -> VNA:
    new_vna = VNA(address)
    if new_vna.resource is not None:
        return new_vna
    else:
        return None


def create_switches(address: str) -> VNA:
    new_switches = Switches(address)
    if new_switches.resource is not None:
        return new_switches
    else:
        return None


class SwitchInvalidPortException(Exception):
    """Raised when attempting to set the switch port outside
    the allowed range."""

    def __init__(self, attempted_port):
        self.attempted_port = attempted_port

    def display_message(self) -> None:
        print(f'SwitchInvalidPortException:'
              f'\n\tPort {self.attempted_port} is invalid.')


class MissingDataException(Exception):
    """Raised when the parsed vna data does not match two floats per frequency"""

    def __init__(self, actual_num_count: int, expected_num_count: int):
        self.actual_num_count = actual_num_count
        self.expected_num_count = expected_num_count

    def get_message(self) -> str:
        msg = f'MissingDataException:\n\texpected {self.expected_num_count} floating point numbers' \
              f'\n\treceived from vna {self.actual_num_count} floating point numbers'
        return msg
