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
import pyvisa

import threading
import gui


class VNA:
    PORT_RANGE = (1, 24)
    port_list = ''

    def __init__(self, resource: pyvisa.Resource):
        self.resource = resource
        if self.resource is not None:
            self.resource.timeout = 60 * 1000  # Time in milliseconds

        self.name = ''

        self.data_point_count = 5
        self.if_bandwidth = 5 * 100  # Hz
        self.freq_start = 10000000  # Hz
        self.freq_stop = 2 * 1000000000  # Hz

        self.data_point_count_range = ()
        self.if_bandwidth_range = ()
        self.freq_start_range = ()
        self.freq_stop_range = ()
        self.power_range = ()

        self.calibration = ''
        self.calibration_list = []

        self._trigger_set = False

    def __del__(self):
        if self.resource is None:
            return
        self.resource.close()

    def initialize(self) -> None:
        """Set up VISA, trigger settings,
        and input parameters."""
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
        self.write(f'SENSE1:SWEEP:POINTS {self.data_point_count}')
        self.write(f'SENSE1:BANDWIDTH {self.if_bandwidth}')
        self.write(f'SENSE1:FREQUENCY:START {self.freq_start}')
        self.write(f'SENSE1:FREQUENCY:STOP {self.freq_stop}')

    def set_parameter_ranges(self) -> None:
        self.data_point_count_range = (
            int(self.query('SENSE1:SWEEP:POINTS? MIN')),
            int(self.query('SENSE1:SWEEP:POINTS? MAX'))
        )
        self.if_bandwidth_range = (
            float(self.query('SENSE1:BANDWIDTH? MIN')),
            float(self.query('SENSE1:BANDWIDTH? MAX'))
        )
        self.freq_start_range = (
            float(self.query('SENSE1:FREQUENCY:START? MIN')),
            float(self.query('SENSE1:FREQUENCY:START? MAX'))
        )
        self.freq_stop_range = (
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

    def write(self, cmd: str) -> None:
        self.resource.write(cmd)

    def query(self, cmd: str) -> str:
        return self.resource.query(cmd)

    @staticmethod
    def set_port_list() -> None:
        """Creates comma delimited list of ports,
        needed for save_snp command."""
        VNA.port_list = ''
        for i in range(VNA.PORT_RANGE[0], VNA.PORT_RANGE[1] + 1):
            VNA.port_list = VNA.port_list + str(i)
            if not i == 24:
                VNA.port_list = VNA.port_list + ','
