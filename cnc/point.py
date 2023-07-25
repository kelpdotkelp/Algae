"""
Algae ~ Automated Target Positioning System
Electromagnetic Imaging Lab, University of Manitoba

Author: Noah Stieler, 2023
"""

from dataclasses import dataclass
from math import sqrt, pow


@dataclass
class Point:
    x: float
    y: float
    z: float = 0

    @property
    def mag(self):
        return sqrt(pow(self.x, 2) + pow(self.y, 2) + pow(self.z, 2))

    def dist(self, other) -> float:
        return sqrt(pow(self.x - other.x, 2) + pow(self.y - other.y, 2) + pow(self.z - other.z, 2))
