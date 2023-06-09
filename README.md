# Algae
Algae is being designed to provide a user-friendly
graphical application that can be extended to control multiple different electromagnetic imaging experiments. Algae automates
the process of positioning the imaging target and scanning it in order to collect large datasets.

`device0` - 2-Port VNA, 24-Port Switch, and CNC Machine (E3-522).

Uses the following hardware:

- Agilent E8363B PNA Network Analyzer
- Agilent 87050A Option K24 Multiport Test Set
- National Instruments GPIB-USB adapter
- Custom `grbl` based CNC machine (https://github.com/grbl/grbl)

`device1` - 24-Port VNA (E3-518).

Uses the following hardware:

- Keysight M9019A PXIe Chassis Gen3
- Keysight M9037A PXIe High-Performance Embedded Controller
- Keysight M9802A PXI Vector Network Analyzer, 6 Port (x4)

### Requirements

All devices require PyVISA and PySerial. Please install it 
by following the installation guide at:

https://pyvisa.readthedocs.io/en/latest/introduction/getting.html

`device0` requires installation of the following National Instruments software:

NI-VISA: https://www.ni.com/en-ca/support/downloads/drivers/download.ni-visa.html#480875

NI-488.2: https://www.ni.com/en-ca/support/downloads/drivers/download.ni-488-2.html#467646

`device1` setup guide:

```
Open 'Network Analyzer'
System->System setup->Remote interface
Enable HiSLIP
Enable Legacy HiSLIP
Open 'Connection Expert'
LAN (TCIP0)->Add instrument
Set hostname to Localhost
Set protocol to HiSLIP
Click Ok
```

There should now be a VISA resource set up that PyVISA can
interface with.

'Network Analyzer' must be running for Algae to send commands to it.