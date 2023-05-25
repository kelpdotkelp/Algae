"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Author: Noah Stieler, 2023
"""

from ctypes import windll

import gui.core
import gui.tab_hardware
import gui.tab_home
import gui.bottom_bar

# VERY IMPORTANT
# This removes blur on all text.
windll.shcore.SetProcessDpiAwareness(1)
