import pyvisa as visa
import time


def main():
    rm = visa.ResourceManager()
    address = rm.list_resources()[5]

    print(address)

    resource = rm.open_resource(address)
    resource.timeout = 60 * 1000 # Time in milliseconds

    print(resource.query('*IDN?'))

    resource.write('SYSTEM:PRESET')

    calibration = resource.query('CSET:CATALOG?')
    calibration = calibration.replace('\"', '')
    calibration = calibration.replace('\n', '')
    calibration = calibration.split(',')
    print(f'calibration = {calibration}')

    resource.write('SENSE1:CORRECTION:CSET:ACTIVATE \''+calibration[3]+'\', 1')
    resource.query('*OPC?')
    print('Calibrated.')

    resource.write('TRIGGER:SEQUENCE:SOURCE MANUAL')
    resource.write('SENSE1:SWEEP:MODE HOLD')
    resource.query('*OPC?')
    print('Trigger configured.')

    # resource.write('CALCULATE1:PARAMETER:DEFINE:EXTENDED \'parameter_S22_22\', \'S22_22\'')

    # resource.write('DISPLAY:WINDOW1:TRACE1:DELETE')
    # resource.query('*OPC?')
    # resource.write('DISPLAY:WINDOW1:TRACE1:FEED \'parameter_S22_22\'')

    resource.write('SENSE1:SWEEP:POINTS 2101')
    resource.write('SENSE1:CORRECTION:CACHE:MODE 1')
    resource.query('*OPC?')

    resource.write('INITIATE1:IMMEDIATE')
    resource.query('*OPC?')
    print('Scan complete.')

    ports = ''
    for i in range(1, 25):
        if not i == 24:
            ports = ports + str(i) + ','
        else:
            ports = ports + str(i)

    dest = 'C:\\Users\\STIELERN\\Desktop\\out_FAST.s24p'
    start = time.time()
    resource.write(f'CALCULATE1:MEASURE1:DATA:SNP:PORTS:SAVE \'{ports}\', \'{dest}\', fast')
    resource.query('*OPC?')
    print(f'dt (fast) = {time.time()-start}')

    start = time.time()
    resource.write('MMEMORY:STORE \'C:\\Users\\STIELERN\\Desktop\\out_SLOW.s24p\'')
    resource.query('*OPC?')
    print(f'dt (slow) = {time.time()-start}')

    resource.close()
