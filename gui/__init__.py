from ctypes import windll

import gui.core
import gui.tab_hardware
import gui.tab_home

# VERY IMPORTANT
# This removes blur on all text.
windll.shcore.SetProcessDpiAwareness(1)
