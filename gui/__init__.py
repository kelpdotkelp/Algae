from ctypes import windll

# VERY IMPORTANT
# This removes blur on all text.
windll.shcore.SetProcessDpiAwareness(1)
