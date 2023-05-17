import tkinter as tk
import tkinter.ttk as ttk
import tab_home
import tab_hardware

_ASPECT_RATIO = 4 / 3
_HEIGHT = 900
_WIDTH = int(_ASPECT_RATIO * _HEIGHT)

_app_terminated = False
_root = None


def _config_base_frames(tabs, bottom_bar):
    """Configures the frames which holds the tabs and bottom menu bar."""
    _root.rowconfigure(index=0, weight=25)
    _root.rowconfigure(index=1, weight=1)
    _root.columnconfigure(index=0, weight=1)

    tabs.grid(row=0, column=0, sticky='nsew')
    bottom_bar.grid(row=1, column=0, sticky='nsew')

    # Prevents grid from resize to fit widgets,
    # i.e grid would be 0x0 if there were no widgets
    tabs.grid_propagate(False)
    bottom_bar.grid_propagate(False)


def _create_window():
    """Creates main application window."""
    global _root

    def on_closing():
        _root.destroy()
        global _app_terminated
        _app_terminated = True

    _root = tk.Tk()
    _root.minsize(_WIDTH, _HEIGHT)
    _root.resizable(False, False)
    _root.title('Gloo')
    _root.geometry(f'{_WIDTH}x{_HEIGHT}+50+50')
    _root.protocol('WM_DELETE_WINDOW', on_closing)


def create_gui():
    _create_window()

    frame_tabs = tk.Frame(_root)
    frame_bottom_bar = tk.Frame(_root, borderwidth=3, relief=tk.RAISED)
    _config_base_frames(frame_tabs, frame_bottom_bar)

    tab_control = ttk.Notebook(frame_tabs)

    frame_tab_home = tab_home.create(tab_control)
    e_num_points = tab_home.add_parameter('Number of points')
    e_if_bandwidth = tab_home.add_parameter('IF bandwidth (Hz)')
    e_start_freq = tab_home.add_parameter('Start frequency (Hz)')
    e_stop_freq = tab_home.add_parameter('Stop frequency (Hz)')
    e_power = tab_home.add_parameter('Power (dBm)')

    frame_tab_hardware = tab_hardware.create(tab_control)

    tab_control.add(frame_tab_home, text='Home')
    tab_control.add(frame_tab_hardware, text='Hardware')
    tab_control.pack(expand=True, fill='both')

    while not _app_terminated:
        _root.update_idletasks()
        _root.update()

    # print(page_home._input_widgets['Power (dBm)'].get())


if __name__ == '__main__':
    # VERY IMPORTANT
    # This removes blur on all text.
    from ctypes import windll

    windll.shcore.SetProcessDpiAwareness(1)

    create_gui()
