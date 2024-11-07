"""
This module provides functions for reading and writing map files in the MovingAI format,
which is commonly used for pathfinding and navigation tasks. The current implementation
supports basic map configurations with passable and impassable terrain, and it can process
obstacles represented as specific characters.

Notes
-----
- Only passable and impassable terrains are supported. Extended terrain types (e.g., swamp, water)
  are not currently handled.
- Only basic map files are supported. Additional MovingAI file types may be supported in the future.
"""

from typing import List, Tuple
import numpy as np
import numpy.typing as npt

MAP_FILE_HEADER = "type octile"
MAP_HEADER = "map"
MAP_HEIGHT = "height"
MAP_WIDTH = "width"
MAP_OBSTACLE = "T"
MAP_OBSTACLE_2 = "@"
MAP_EMPTY = "."


def create_map_file(
    file_path: str, height: int, width: int, grid: List[List[int | bool]] | npt.NDArray
) -> None:
    """
    Creates map file in MovingAI format. Only passable/unpassable terrains are supported (swamp, water and etc. not supported)

    Parameters
    ----------
    file_path : str
        Desired path to file with map
    height : int
        Height of grid
    width : int
        Width of grid
    grid : List[List[int | bool]] | np.ndarray
        Grid cells
    """
    result_file = open(file_path, "w")
    result_file.write(MAP_FILE_HEADER + "\n")
    result_file.write(f"{MAP_HEIGHT} {height}\n")
    result_file.write(f"{MAP_WIDTH} {width}\n")
    result_file.write(MAP_HEADER)
    for row in grid:
        result_file.write("\n")
        for col in row:
            if col:
                result_file.write(MAP_OBSTACLE)
            else:
                result_file.write(MAP_EMPTY)
    result_file.close()


def read_map_file(file_path: str) -> Tuple[int, int, npt.NDArray]:
    """
    Read map file in MovingAI format. Only passable/unpassable terrains are supported (swamp, water and etc. not supported).
    Obstacles should be denoted as "@" or "T".

    Parameters
    ----------
    file_path : str
        Path to file with map

    Returns
    -------
    height : int
        Height of grid
    width : int
        Width of grid
    ocuupancy_grid : np.ndarray
        Grid cells
    """

    movingai_obst_chars = {MAP_OBSTACLE, MAP_OBSTACLE_2}
    file = open(file_path)
    file.readline()

    height = int(file.readline().split()[1])
    width = int(file.readline().split()[1])
    occupancy_grid = np.zeros((height, width), dtype=np.bool8)

    file.readline()
    for i in range(height):
        for j in range(width):
            cell = file.read(1)
            if cell in movingai_obst_chars:
                occupancy_grid[i, j] = 1
        file.read(1)
    file.close()
    return height, width, occupancy_grid
