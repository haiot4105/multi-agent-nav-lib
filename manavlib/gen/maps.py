"""
This module provides functions to create or modify different types of grid maps, which can be used
as environments for multi-agent navigation experiments. The generated grids are represented
as 2D numpy arrays, where each cell can be passable or an obstacle.
"""

import numpy as np
import numpy.typing as npt
from typing import Tuple, Optional


def create_empty_grid(
    x_size: int | Tuple[float, float],
    y_size: int | Tuple[float, float],
    cell_size: float,
) -> Optional[Tuple[int, int, npt.NDArray]]:
    """
    Creates an empty grid with specified dimensions and cell size, represented as a
    2D numpy array where all cells are passable.

    Parameters
    ----------
    x_size : int or tuple[float, float]
        Width of the grid in absolute coordinates (in cells) or as a range `[x_min, x_max]`.
    y_size : int or tuple[float, float]
        Height of the grid in absolute coordinates (in cells) or as a range `[y_min, y_max]`.
    cell_size : float
        Size of each cell in the grid.

    Returns
    -------
    Optional[Tuple[int, int, np.ndarray]]
        A tuple `(height, width, occupancy_grid)` where:
        - `height` is the number of rows in the grid.
        - `width` is the number of columns in the grid.
        - `occupancy_grid` is a 2D numpy array of shape `(height, width)` where all
          cells are `False` (indicating all cells are passable).

    Returns None if the provided dimensions are not compatible with the specified cell size.

    Notes
    -----
    - If `x_size` and `y_size` are provided as integers, they are treated as the absolute
      size of the grid.
    - If `x_size` or `y_size` are tuples, they are treated as coordinate ranges.
    - The function validates that `cell_size` divides evenly into the specified dimensions.
    """
    if type(y_size) is int:
        x_size = [0, x_size]
    if type(y_size) is int:
        y_size = [0, y_size]

    height = int((y_size[1] - y_size[0]) / cell_size)
    width = int((x_size[1] - x_size[0]) / cell_size)

    if not (np.isclose(height * cell_size, y_size[1] - y_size[0])) or not (np.isclose(width * cell_size, x_size[1] - x_size[0])):
        return None

    occupancy_grid = np.zeros((height, width), dtype=np.bool8)

    return height, width, occupancy_grid


def create_gap_scenario_grid(height: int, width: int, gaps: int) -> Tuple[int, int, npt.NDArray]:
    """
    Creates a grid with walls around the edges and a central wall with specified gaps
    for pathfinding scenarios.

    - The grid has a boundary wall on all edges, represented by `1`s in the `occupancy_grid`.
    - A central wall is added in the middle column of the grid.
    - Gaps are distributed evenly in the central wall. If `gaps` is greater than or equal
      to the height of the wall, the function returns a solid central wall.
    - If `gaps` is 1, a single gap is placed at the middle row of the central wall.
    - For multiple gaps, they are evenly spaced along the central wall.

    Parameters
    ----------
    height : int
        Height of the grid in cells.
    width : int
        Width of the grid in cells.
    gaps : int
        Number of gaps in the central wall for agents to pass through.

    Returns
    -------
    Tuple[int, int, np.ndarray]
        A tuple `(height, width, occupancy_grid)` where:
        - `height` is the number of rows in the grid.
        - `width` is the number of columns in the grid.
        - `occupancy_grid` is a 2D numpy array where `1` indicates a wall or obstacle
          cell and `0` indicates a passable cell.
    """
    occupancy_grid = np.zeros((height, width), dtype=np.bool8)
    occupancy_grid[0, :] = 1
    occupancy_grid[-1, :] = 1
    occupancy_grid[:, 0] = 1
    occupancy_grid[:, -1] = 1
    wall_column = width // 2
    occupancy_grid[:, wall_column] = 1

    if gaps >= height - 2:
        return height, width, occupancy_grid
    gap_poses = set()
    if gaps == 1:
        gap_poses.add((height // 2, wall_column))
    else:
        div = (height - 2 - gaps) // (gaps + 1)
        residue = (height - 2 - gaps) % (gaps + 1)
        pos = [0, wall_column]
        for gap in range(gaps):
            pos[0] += div + 1
            if residue > 0:
                pos[0] += 1
                residue -= 1

            gap_poses.add(tuple(pos))

    for gap_pose in gap_poses:
        occupancy_grid[gap_pose] = 0

    return height, width, occupancy_grid


def reduce_cellsize(grid_map: npt.NDArray, cs: float, n: int) -> Tuple[int, int, float, npt.NDArray]:
    """
    Increase the resolution of a grid map by reducing the cell size.

    This function expands the grid by dividing each cell into `n x n` smaller cells, effectively
    reducing the cell size by a factor of `n`. The resulting grid will have a higher resolution.

    Parameters
    ----------
    grid_map : np.ndarray
        The input grid map, where each cell represents some value (e.g., occupancy, cost, etc.).
    cs : float
        The original cell size (grid resolution).
    n : int
        The factor by which to subdivide each cell. Each cell in the original grid is replaced
        by an `n x n` block of smaller cells.

    Returns
    -------
    Tuple[int, int, float, np.ndarray]
        A tuple containing:
        - New height of the grid (`h * n`).
        - New width of the grid (`w * n`).
        - Updated cell size (`cs / n`).
        - The new high-resolution grid map as a NumPy array.
    """
    h, w = grid_map.shape
    new_grid = np.zeros((h*n, w*n), dtype=np.int8)
    for i in range(h):
        for j in range(w):
            new_grid[n*i:n*(i+1), n*j:n*(j+1)] = grid_map[i, j]

    return h * n, w * n, cs / n, new_grid