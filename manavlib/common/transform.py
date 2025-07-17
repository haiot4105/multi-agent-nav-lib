"""
This module provides utility functions for converting between Cartesian (x, y) coordinates
and grid indices (i, j).
"""

import numpy.typing as npt
import numpy as np
from typing import List

def convert_xy_to_ij(xy: npt.NDArray, grid_h: int, cs: float=1.0) -> List[int]:
    """
    Convert 2D coordinates (x, y) to grid indices (i, j).

    Parameters
    ----------
    xy : np.ndarray
        Cartesian coordinates of the point as [x, y].
    grid_h : int
        The height of the grid in cells (number of rows).
    cs : float, optional
        The cell size (grid resolution). Default is 1.0.

    Returns
    -------
    List[int]
        Grid indices [i, j], where:
        - `i` is the row index (vertical position, starting from the top).
        - `j` is the column index (horizontal position, starting from the left).
    """
    j = int(xy[0] // cs)
    i = grid_h - int(xy[1] // cs)
    return [i, j]


def convert_ij_to_xy(ij: List[int], grid_h: int, cs: float) -> npt.NDArray:
    """
        Convert grid indices (i, j) to Cartesian coordinates (x, y).

    Parameters
    ----------
    ij : List[int]
        Grid indices as [i, j], where:
        - `i` is the row index (vertical position, starting from the top).
        - `j` is the column index (horizontal position, starting from the left).
    grid_h : int
        The height of the grid in cells (number of rows).
    cs : float
        The cell size (grid resolution).

    Returns
    -------
    np.ndarray
        Cartesian coordinates [x, y] as a NumPy array with dtype float64.
    """
    i = ij[0]
    j = ij[1]
    x = (j + 0.5) * cs
    y = (grid_h - i - 0.5) * cs
    return np.array([x, y], dtype=np.float64)
