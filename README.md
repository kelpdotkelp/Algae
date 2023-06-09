# Algae
Algae is being designed to provide a user-friendly
graphical application that can be extended to control multiple different electromagnetic imaging experiments. Algae automates
the process of positioning the imaging target and scanning it in order to collect large datasets.

`device0` - Scans the 2D cross section of the target (E3-522).

Uses the following hardware:

- Agilent E8363B PNA Network Analyzer
- Agilent 87050A Option K24 Multiport Test Set
- National Instruments GPIB-USB adapter

`device1` - Is the electromagnet scanner (E3-518).

Uses the following hardware:

- Keysight M9019A PXIe Chassis Gen3
- Keysight M9037A PXIe High-Performance Embedded Controller
- Keysight M9802A PXI Vector Network Analyzer, 6 Port (x4)

### Requirements

Please install PyVISA by following the installation guide at:

https://pyvisa.readthedocs.io/en/latest/introduction/getting.html

`device0` requires installation of the following National Instruments software:

NI-VISA: https://www.ni.com/en-ca/support/downloads/drivers/download.ni-visa.html#480875

NI-488.2: https://www.ni.com/en-ca/support/downloads/drivers/download.ni-488-2.html#467646
