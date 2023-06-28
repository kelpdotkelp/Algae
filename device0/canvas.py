"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Handles the drawing the canvas.
Implemented here rather than in the gui package so that
multiple graphics can easily be written for different experiments.

Author: Noah Stieler, 2023
"""

import gui
import math

from .imaging import Switches
import cnc.core
from cnc import *

_init = False

_background_color = 'white'

_g_padding = 50

_radius_in = 0.85
_radius_out = 1.10

_port_state = []
_line_list = []

_tran = -1
_refl = -1

# Red cross over coordinate axis
_cross = []
_cross_state = 'red'

# For checking if gui should update
_wa_radius, _wa_pad = 0, 0

_target = None
_target_radius = 0

for j in range(0, Switches.PORT_MAX):
    _port_state.append(0)


def update() -> None:
    if not _init:
        _init_draw()

    # Not updating these on function calls because
    # There has to be a check for the changing of these values.
    if _wa_radius != input_dict['wa_radius'].value \
            or _wa_pad != input_dict['wa_pad'].value \
            or _target_radius != cnc.core.target_radius:
        _init_draw()

    for i in range(0, Switches.PORT_MAX):
        if _port_state[i] == 0:
            fill = '#2E2E2E'  # black
        else:
            fill = '#F6F6F6'  # gray

        if _tran == i:
            fill = '#30C03F'  # green
        if _refl == i and _refl != _tran:
            fill = '#ABEDD0'  # blue

        gui.tab_home.canvas.itemconfigure(_line_list[i], fill=fill)

    if cnc.core.target_radius > 0:
        gui.tab_home.canvas.itemconfigure(_target, width=2)
    else:
        gui.tab_home.canvas.itemconfigure(_target, width=0)


def _init_draw(target_x: float = 0, target_y: float = 0) -> None:
    global _line_list, _init

    dim = gui.tab_home.canvas_size
    centre = (dim / 2, dim / 2)
    radius = dim / 2 - _g_padding

    # Clear canvas
    gui.tab_home.canvas.delete('all')
    gui.tab_home.canvas.create_rectangle(0, 0, dim, dim, fill=_background_color)

    _create_circle(centre[0], centre[1], radius=radius, width=8)

    global _wa_radius, _wa_pad
    _wa_radius = input_dict['wa_radius'].value
    _wa_pad = input_dict['wa_pad'].value
    if _wa_radius > 0 and 0 <= _wa_pad / _wa_radius <= 1:
        in_width = (1 - (_wa_pad / _wa_radius)) * radius * _radius_in
        _create_circle(centre[0], centre[1], radius=radius, width=0, fill='#D1D1D1')
        _create_circle(centre[0], centre[1], radius=in_width,
                       width=0, fill=_background_color)

    _line_list = []
    for i in range(0, Switches.PORT_MAX):
        angle = i * (2 * math.pi) / Switches.PORT_MAX
        pos_in = (centre[0] + _radius_in * radius * math.cos(angle),
                  centre[1] + _radius_in * radius * math.sin(angle))
        pos_out = (centre[0] + _radius_out * radius * math.cos(angle),
                   centre[1] + _radius_out * radius * math.sin(angle))
        line = gui.tab_home.canvas.create_line(pos_in[0], pos_in[1], pos_out[0], pos_out[1], width=15, fill='blue')
        _line_list.append(line)

    # Axis red cross
    a_len = 35
    gui.tab_home.canvas.create_line(centre[0], centre[1], centre[0] + a_len, centre[1],
                                    width=4, fill='red')
    gui.tab_home.canvas.create_line(centre[0], centre[1], centre[0], centre[1] - a_len,
                                    width=4, fill='#00FF00')
    a_len = a_len / 2
    line = gui.tab_home.canvas.create_line(centre[0] - a_len, centre[1] + a_len, centre[0] + a_len,
                                           centre[1] - a_len, width=4, fill=_cross_state)
    _cross.append(line)
    line = gui.tab_home.canvas.create_line(centre[0] - a_len, centre[1] - a_len, centre[0] + a_len,
                                           centre[1] + a_len, width=4, fill=_cross_state)
    _cross.append(line)

    if _wa_radius != 0:
        global _target, _target_radius
        _target_radius = cnc.core.target_radius
        con = radius * _radius_in / _wa_radius
        x = target_x * con
        y = target_y * con
        _target = _create_circle(centre[0] + x,
                                 centre[1] - y, radius=cnc.core.target_radius * con,
                                 width=2, outline='black', fill='')

    _init = True


def port_reset() -> None:
    global _tran, _refl
    for i in range(0, Switches.PORT_MAX):
        _port_state[i] = 0
    _tran = -1
    _refl = -1


def port_complete(port: int) -> None:
    _port_state[port - 1] = 1


def port_pair(tran: int, refl: int) -> None:
    global _tran, _refl
    _tran = tran - 1
    _refl = refl - 1


def set_state_origin(state: bool) -> None:
    global _cross_state
    if state == 1:
        _cross_state = 'red'
    elif state == 0:
        _cross_state = ''

    for i in range(len(_cross)):
        gui.tab_home.canvas.itemconfigure(_cross[i], fill=_cross_state)


def set_target_pos(x: float, y: float) -> None:
    _init_draw(x, y)


def _create_circle(x: float, y: float, radius: float, width: float,
                   outline: str = '#2E2E2E', fill: str = _background_color) -> int:
    """Because tkinter only supports
    drawing ovals with upper-left and bottom-right coors?"""
    return gui.tab_home.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                           fill=fill, outline=outline, width=width)
