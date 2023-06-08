

class VNA:
    PORT_RANGE = (1, 24)
    port_list = ''

    def __init__(self, resource):
        self.resource = resource
        self.name = ''

        self.data_point_count = 5
        self.if_bandwidth = 5 * 100 # Hz
        self.freq_start = 10000000 # Hz
        self.freq_stop = 2 * 1000000000 # Hz
        self.power = 0 # dBm -> confirm this unit

        self.data_point_count_range = ()
        self.if_bandwidth_range = ()
        self.freq_start_range = ()
        self.freq_stop_range = ()
        self.power_range = ()

        self.calibration = ''
        self.calibration_list = []

        if self.resource is not None:
            self._set_calibration_list()

    def __del__(self):
        if self.resource is None:
            return
        self.resource.close()

    def initialize(self):
        self.resource.timeout = 60 * 1000 # Time in milliseconds

        self.name = self.resource.query('*IDN?')

        self.write('SYSTEM:PRESET')

        # Trigger set up
        self.write('TRIGGER:SEQUENCE:SOURCE MANUAL')
        self.write('SENSE1:SWEEP:MODE HOLD')

        self.query('*OPC?')

        # Parameters
        self.write(f'SENSE1:SWEEP:POINTS {self.data_point_count}')

    def _set_calibration_list(self):
        cal = self.query('CSET:CATALOG?')
        cal = cal.replace('\"', '')
        cal = cal.replace('\n', '')
        self.calibration_list = cal.split(',')

    def calibrate(self):
        pass

    def fire(self):
        self.write('INITIATE1:IMMEDIATE')
        self.query('*OPC?')

    def save_snp(self, path):
        # Manual wants this for .snp save command
        self.write('SENSE1:CORRECTION:CACHE:MODE 1')

        cmd = 'CALCULATE1:MEASURE1:DATA:SNP:PORTS:SAVE'
        args = f' \'{VNA.port_list}\', \'{path}\', fast'
        self.write(cmd + args)

        self.query('*OPC?')

    def write(self, cmd):
        self.resource.write(cmd)

    def query(self, cmd):
        return self.resource.query(cmd)

    @staticmethod
    def set_port_list():
        VNA.port_list = ''
        for i in range(VNA.PORT_RANGE[0], VNA.PORT_RANGE[1]+1):
            VNA.port_list = VNA.port_list + str(i)
            if not i == 24:
                VNA.port_list = VNA.port_list + ','

