"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Part of the gui.
Creates window and main gui frames.

Author: Noah Stieler, 2023
"""
import tkinter
import tkinter as tk
import tkinter.ttk as ttk

import gui.tab_home as tab_home
import gui.tab_hardware as tab_hardware
import gui.bottom_bar as bottom_bar

_ASPECT_RATIO = 4 / 3
_HEIGHT = 900
_WIDTH = int(_ASPECT_RATIO * _HEIGHT)

app_terminated = False
_root = None
_tab_control = None

tab_index = 0


def _config_base_frames(tabs, frame_bottom_bar):
    """Configures the frames which holds the tabs and bottom menu bar."""
    _root.rowconfigure(index=0, weight=10)
    _root.rowconfigure(index=1, weight=1)
    _root.columnconfigure(index=0, weight=1)

    tabs.grid(row=0, column=0, sticky='nsew')
    frame_bottom_bar.grid(row=1, column=0, sticky='nsew')

    # Prevents grid from resize to fit widgets,
    # ie grid would be 0x0 if there were no widgets
    tabs.grid_propagate(False)
    frame_bottom_bar.grid_propagate(False)


def _create_window():
    """Creates main application window."""
    global _root

    def on_closing():
        _root.destroy()
        global app_terminated
        app_terminated = True

    _root = tk.Tk()
    _root.minsize(_WIDTH, _HEIGHT)
    _root.resizable(False, False)
    _root.title('Algae')
    _root.geometry(f'{_WIDTH}x{_HEIGHT}+50+50')
    _root.protocol('WM_DELETE_WINDOW', on_closing)

    try:
        icon = tk.PhotoImage(file='./res/icon_titlebar.png')
        _root.iconphoto(True, icon)
    except tkinter.TclError:
        pass


def create_gui():
    _create_window()

    frame_tabs = tk.Frame(_root)
    frame_bottom_bar = tk.Frame(_root, borderwidth=3, relief=tk.RAISED)
    _config_base_frames(frame_tabs, frame_bottom_bar)

    bottom_bar.create(frame_bottom_bar)

    global _tab_control
    _tab_control = ttk.Notebook(frame_tabs)

    frame_tab_home = tab_home.create(_tab_control)
    frame_tab_hardware = tab_hardware.create(_tab_control)

    _tab_control.add(frame_tab_home, text='Home')
    _tab_control.add(frame_tab_hardware, text='Hardware')
    _tab_control.pack(expand=True, fill='both')
    _tab_control.bind('<<NotebookTabChanged>>', _on_tab_change)
    _tab_control.select(tab_index)


def update():
    _root.update_idletasks()
    _root.update()


def create_popup(message):
    root = tk.Tk()
    root.resizable(False, False)
    root.title('Resource Finder')
    root.geometry(f'{650}x{200}+50+50')

    text = tk.Text(root)
    text.insert('1.0', message)
    text['state'] = tk.DISABLED
    text.pack()


def _on_tab_change(event):
    global tab_index
    tab_index = _tab_control.index(_tab_control.select())
