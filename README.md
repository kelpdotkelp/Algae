# Algae
Algae is designed to provide a user-friendly
graphical application that can be extended to control multiple different electromagnetic imaging experiments. Algae automates
the process of positioning the imaging target and scanning it in order to collect large datasets.

`device0` - 2-Port VNA, 24-Port Switch, and CNC Machine (E3-522).

Uses the following hardware:

- Agilent E8363B PNA Network Analyzer
- Agilent 87050A Option K24 Multiport Test Set
- National Instruments GPIB-USB adapter

`device1` - 24-Port VNA (E3-518).

Uses the following hardware:

- Keysight M9019A PXIe Chassis Gen3
- Keysight M9037A PXIe High-Performance Embedded Controller
- Keysight M9802A PXI Vector Network Analyzer, 6 Port (x4)

Both devices use custom `grbl` based cartesian robots.
(https://github.com/grbl/grbl)

### Requirements

All devices require PyVISA, pygrbl, and PySerial.

PyVISA: https://pyvisa.readthedocs.io/en/latest/introduction/getting.html
pygrbl: https://github.com/kelpdotkelp/pygrbl

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

### Building

`build.bat` runs PyInstaller as a python module with all the needed build options.
Building an executable may not work currently, so the best way to use the software is to run:

`python ./Algae/main.py`

### Documentation

Read the wiki for details on working with Algae!