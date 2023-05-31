# Algae
Algae is being designed to provide a user-friendly
graphical application that can be extended to control multiple different electromagnetic imaging experiments. The goal is to automate
the process of positioning the target and scanning it in order to collect large datasets.

Experiment 1 - Scans the 2D cross section of the target, and measures the S-parameters.

Uses the following hardware:

- Agilent E8363B PNA Network Analyzer
- Agilent 87050A Option K24 Multiport Test Set
- National Instruments GPIB-USB adapter

### Requirements

Please install PyVISA by following the installation guide at:

https://pyvisa.readthedocs.io/en/latest/introduction/getting.html

PyVISA requires installation of the following National Instruments software:

NI-VISA: https://www.ni.com/en-ca/support/downloads/drivers/download.ni-visa.html#480875

NI-488.2: https://www.ni.com/en-ca/support/downloads/drivers/download.ni-488-2.html#467646
