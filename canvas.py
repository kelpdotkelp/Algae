"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Handles the drawing the canvas.
Implemented here rather than in the gui package so that
multiple graphics can easily be written for different experiments.

Author: Noah Stieler, 2023
"""

import tkinter
import gui

_background_color = 'white'

_g_padding = 75


def update():
    if gui.tab_home.canvas is not None and gui.tab_home.canvas_size != 0:
        try:
            _update()
        except tkinter.TclError:  # Thrown when closing window
            pass


def _update():
    dim = gui.tab_home.canvas_size
    centre = (dim / 2, dim / 2)

    # Clear canvas
    gui.tab_home.canvas.create_rectangle(0, 0, dim, dim, fill=_background_color)

    _create_circle(centre[0], centre[1], radius=dim / 2 - _g_padding, width=5)


def _create_circle(x, y, radius, width, outline='black', fill=_background_color):
    """Because tkinter only supports
    drawing ovals with upper-left and bottom-right coors?"""
    gui.tab_home.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                    fill=fill, outline=outline, width=width)
