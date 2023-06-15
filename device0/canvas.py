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

_init = False

_background_color = 'white'

_g_padding = 75

_radius_in = 0.75
_radius_out = 1.10

_port_state = []
_line_list = []

_tran = -1
_refl = -1

for j in range(0, Switches.PORT_MAX):
    _port_state.append(0)


def update() -> None:
    if not _init:
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


def _init_draw() -> None:
    global _line_list, _init

    dim = gui.tab_home.canvas_size
    centre = (dim / 2, dim / 2)
    radius = dim / 2 - _g_padding

    # Clear canvas
    gui.tab_home.canvas.create_rectangle(0, 0, dim, dim, fill=_background_color)

    _create_circle(centre[0], centre[1], radius=radius, width=8)

    for i in range(0, Switches.PORT_MAX):
        angle = i * (2 * math.pi) / Switches.PORT_MAX
        pos_in = (centre[0] + _radius_in * radius * math.cos(angle),
                  centre[1] + _radius_in * radius * math.sin(angle))
        pos_out = (centre[0] + _radius_out * radius * math.cos(angle),
                   centre[1] + _radius_out * radius * math.sin(angle))
        line = gui.tab_home.canvas.create_line(pos_in[0], pos_in[1], pos_out[0], pos_out[1], width=15, fill='blue')
        _line_list.append(line)

    _init = True


def _create_circle(x: float, y: float, radius: float, width: float,
                   outline: str = '#2E2E2E', fill: str = _background_color) -> None:
    """Because tkinter only supports
    drawing ovals with upper-left and bottom-right coors?"""
    gui.tab_home.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                    fill=fill, outline=outline, width=width)


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
