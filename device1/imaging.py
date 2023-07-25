"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Manages VNA state and VNA communication.

Hardware:
    Keysight M9019A PXIe Chassis Gen3
    Keysight M9037A PXIe High-Performance Embedded Controller
    Keysight M9802A PXI Vector Network Analyzer, 6 Port (x4)

Author: Noah Stieler, 2023
"""
import threading
import gui
from visa import VisaResource
from gui.parameter import input_dict


class VNA(VisaResource):
    PORT_RANGE = (1, 24)
    port_list = ''

    def __init__(self, address: str):
        super().__init__(address)

        if self.resource is None:
            return

        self.name = ''
        self.p_ranges = {}
        self.calibration = ''
        self.calibration_list = []
        self._trigger_set = False

        self._set_parameter_ranges()

    def __del__(self):
        super().__del__()

    def initialize(self) -> None:
        """Set up VISA, trigger settings,
        and input parameters."""
        self.resource.timeout = 60 * 1000  # Time in milliseconds

        self.name = self.resource.query('*IDN?')

        if self.calibration == '':
            self.write('SYSTEM:PRESET')

        # Trigger set up
        # Doing this every scan causes large slowdowns
        if not self._trigger_set:
            def cmd():
                self.write('TRIGGER:SEQUENCE:SOURCE MANUAL')
                self.write('INITIATE:CONTINUOUS OFF')
                self.write('SENSE1:SWEEP:MODE CONTINUOUS')
                self.write('SENSE1:SWEEP:TYPE LINEAR')
                self.query('*OPC?')

            t = threading.Thread(target=cmd)
            t.start()

            gui.bottom_bar.message_display('Setting up measurement...', 'blue')
            gui.core.update_during_thread_wait(t)

            self._trigger_set = True

        # Parameters
        self.write('SENSE1:SWEEP:POINTS ' + str(input_dict['num_points'].value))
        self.write('SENSE1:BANDWIDTH ' + str(input_dict['ifbw'].value))
        self.write('SENSE1:FREQUENCY:START ' + str(input_dict['freq_start'].value))
        self.write('SENSE1:FREQUENCY:STOP ' + str(input_dict['freq_stop'].value))

    def _set_parameter_ranges(self) -> None:
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

    def set_calibration_list(self) -> None:
        """Query list of VNA calibrations and parse them."""
        cal = self.query('CSET:CATALOG?')
        self.query('*OPC?')
        cal = cal.replace('\"', '')
        cal = cal.replace('\n', '')
        self.calibration_list = cal.split(',')

    def calibrate(self) -> None:
        self.write('SYSTEM:PRESET')
        self.write('SENSE1:CORRECTION:CSET:ACTIVATE \'' + self.calibration + '\', 1')
        self.query('*OPC?')

    def fire(self) -> None:
        self.write('INITIATE1:IMMEDIATE')
        self.query('*OPC?')

    def save_snp(self, path: str) -> None:
        """Writes VNA data to a .s24p at path"""
        # Manual wants this for .snp save command
        self.write('SENSE1:CORRECTION:CACHE:MODE 1')

        cmd = 'CALCULATE1:MEASURE1:DATA:SNP:PORTS:SAVE'
        args = f' \'{VNA.port_list}\', \'{path}\\output.s24p\', fast'
        self.write(cmd + args)

        self.query('*OPC?')

    @staticmethod
    def set_port_list() -> None:
        """Creates comma delimited list of ports,
        needed for save_snp command."""
        VNA.port_list = ''
        for i in range(VNA.PORT_RANGE[0], VNA.PORT_RANGE[1] + 1):
            VNA.port_list = VNA.port_list + str(i)
            if not i == 24:
                VNA.port_list = VNA.port_list + ','


def create_vna(address: str) -> VNA:
    new_vna = VNA(address)
    if new_vna.resource is not None:
        return new_vna
    else:
        return None
