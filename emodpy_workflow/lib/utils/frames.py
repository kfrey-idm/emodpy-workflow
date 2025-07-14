from functools import partial
from typing import List

EPSILON = 1e-3

def timestep_from_year(year, base_year):
    return int((year - base_year) * 365)
