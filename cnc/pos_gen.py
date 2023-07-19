"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Generates and performs operations on a list of positions.

Author: Noah Stieler, 2023
"""
import random
from math import sin, cos, sqrt, pi
from .core import Point

_MAX_ITER = 8000
_MIN_DIST = 0.10  # mm


def rand_uniform(n_points: int, radius: float, order='none') -> list:
    """Generates uniformly distributed points in a circle"""
    li = []
    iter_count = 0

    while len(li) < n_points and iter_count < 8000:
        iter_count += 1
        angle = random.random() * 2 * pi
        mag = (radius / sqrt(radius)) * sqrt(radius * random.random())  # sqrt() is need to make distribution uniform
        new_pos = Point(mag * cos(angle), mag * sin(angle))
        skip = False
        for i in range(len(li)):
            dist = new_pos.dist(li[i])
            if dist < _MIN_DIST:
                skip = True
                break
        if not skip:
            li.append(new_pos)

    if order == 'none':
        return li
    elif order == 'nearest_neighbour':
        li_nn = []
        cur_pos = Point(0, 0)

        while len(li) != 0:
            index = _get_nearest_neighbour(li, cur_pos)
            li_nn.append(li[index])
            cur_pos = li[index]
            del li[index]
        return li_nn


def _get_nearest_neighbour(pos_list: list, pos: Point) -> int:
    """Finds the index of the closest point that has not been visited yet."""
    nn = -1
    best_dist = float('inf')

    for i in range(len(pos_list)):
        dist = pos_list[i].dist(pos)
        if dist <= best_dist:
            nn = i
            best_dist = dist

    return nn


def get_pos_from_file() -> list:
    """Parses a .csv file and returns a list of positions."""
    pass
    # TODO
