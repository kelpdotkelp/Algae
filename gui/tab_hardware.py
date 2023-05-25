"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Part of the gui.
Sets up and handles the hardware tab.

Author: Noah Stieler, 2023
"""

import tkinter as tk
import tkinter.ttk as ttk

_frame_hardware_box = None
_status_indicators = []
_button_hw_scan, _button_c_connect = None, None
_hardware_count = 0


def add_hardware(display_name, default_value=''):
    global _hardware_count
    padding_x = 15
    padding_y = 10

    _frame_hardware_box.rowconfigure(index=_hardware_count, weight=1)

    new_frame = tk.Frame(_frame_hardware_box)
    new_frame.grid(row=_hardware_count, column=0, pady=padding_y, sticky='nsew')

    _status_indicators.append(tk.Label(new_frame, text=''))
    _status_indicators[_hardware_count].pack(padx=padding_x, side=tk.LEFT)

    tk.Label(new_frame, text=display_name).pack(padx=padding_x, side=tk.LEFT)

    text = tk.StringVar()
    text.set(default_value)
    entry = tk.Entry(new_frame, textvariable=text, width=40, justify=tk.RIGHT)
    entry.pack(padx=padding_x, side=tk.RIGHT)
    tk.Label(new_frame, text='\t\t\tAddress: ').pack(padx=padding_x, side=tk.RIGHT)

    _hardware_count += 1

    return entry


def set_indicator(index, message, color):
    _status_indicators[index].configure(text=message, foreground=color)


def create(frame_content_base):
    frame_page_base = tk.Frame(frame_content_base)

    frame_hardware = tk.Frame(frame_page_base)

    frame_page_base.rowconfigure(index=0, weight=1)
    frame_page_base.columnconfigure(index=0, weight=1)
    frame_hardware.grid(row=0, column=0, sticky='new')

    label_hardware = tk.Label(frame_hardware, text='Hardware Setup',
                              background=frame_hardware['background'],
                              font=('Arial', 12))
    label_hardware.pack(padx=50, pady=(60, 10), anchor='w')

    global _frame_hardware_box
    _frame_hardware_box = tk.Frame(frame_hardware, width=400, height=300,
                                   borderwidth=3, relief=tk.SUNKEN)
    _frame_hardware_box.pack(padx=50, anchor='w')

    global _button_hw_scan, _button_c_connect
    frame_buttons = tk.Frame(frame_hardware)
    frame_buttons.rowconfigure(index=0, weight=1)
    frame_buttons.columnconfigure(index=1, weight=1)
    frame_buttons.pack(padx=50, pady=15, anchor='w')

    _button_hw_scan = ttk.Button(frame_buttons, text='Scan for hardware')
    _button_c_connect = ttk.Button(frame_buttons, text='Check for connections')

    _button_hw_scan.grid(row=0, column=0)
    _button_c_connect.grid(row=0, column=1, padx=15)

    return frame_page_base


def on_hardware_scan(function):
    _button_hw_scan.configure(command=function)


def on_check_connection(function):
    _button_c_connect.configure(command=function)


def create_message(message):
    root = tk.Tk()
    root.resizable(False, False)
    root.title('Resource Finder')
    root.geometry(f'{650}x{200}+50+50')

    text = tk.Text(root)
    text.insert('1.0', message)
    text['state'] = tk.DISABLED
    text.pack()
