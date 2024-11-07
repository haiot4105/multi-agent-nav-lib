"""
This module provides utility functions to support the setup, conversion, and
processing of multi-agent pathfinding experiments with the TSWAP algorithm.
TSWAP is a well-known algorithm for solving the Anonymous Multi-Agent Pathfinding
(AMAPF) problem.

The functions in this module facilitate creating TSWAP instance files, converting
between coordinate systems (real-world and grid-based), and reading experiment
results from TSWAP log files.

For more details on the TSWAP algorithm, visit the open-source implementation:
https://github.com/Kei18/tswap.
"""

import numpy as np
import numpy.typing as npt
from typing import Tuple
import re

INSTANCE_MAP_FILE = "map_file="
INSTANCE_AGENTS_NUM = "agents="
INSTANCE_SEED = "seed="
INSTANCE_RANDOM = "random_problem="
INSTANCE_MAX_STEPS = "max_timestep="
INSTANCE_MAX_TIME = "max_comp_time="
INSTANCE_GROUPS = "flocking_blocks="

LOG_SOLVED = "solved"
LOG_FLOWTIME = "soc"
LOG_MAKESPAN = "makespan"
LOG_RUNTIME = "comp_time"
LOG_SOLUTION = "solution="
LOG_AGENTS = "agents"


def create_tswap_instance_file(
    file_path: str,
    map_file_name: str,
    agents_num: int,
    max_steps: int,
    max_time: int,
    agents_starts: npt.NDArray,
    agents_goals: npt.NDArray,
    random: int = 0,
    seed: int = 0,
    groups: int = 0,
) -> None:
    """
    Creates an instance file for TSWAP algorithm with specified experiment parameters.

    Parameters
    ----------
    file_path : str
        Path to save the instance file.
    map_file_name : str
        Name of the map file.
    agents_num : int
        Number of agents in the experiment.
    max_steps : int
        Maximum number of steps allowed in the experiment.
    max_time : int
        Maximum computation time allowed in the experiment.
    agents_starts : npt.NDArray
        Array of starting positions for each agent.
    agents_goals : npt.NDArray
        Array of goal positions.
    random : int, optional
        Flag to indicate if the problem should be randomly generated (default is 0).
    seed : int, optional
        Random seed for the experiment (default is 0).
    groups : int, optional
        Number of flocking blocks in the experiment (default is 0).
    """
    result_file = open(file_path, "w")
    result_file.write(f"{INSTANCE_MAP_FILE}{map_file_name}\n")
    result_file.write(f"{INSTANCE_AGENTS_NUM}{agents_num}\n")
    result_file.write(f"{INSTANCE_SEED}{seed}\n")
    result_file.write(f"{INSTANCE_RANDOM}{random}\n")
    result_file.write(f"{INSTANCE_MAX_STEPS}{max_steps}\n")
    result_file.write(f"{INSTANCE_MAX_TIME}{max_time}\n")
    result_file.write(f"{INSTANCE_GROUPS}{groups}\n")
    if random == 1:
        return
    for agent_id in range(agents_num):
        result_file.write(
            f"{agents_starts[agent_id, 0]},{agents_starts[agent_id, 1]},{agents_goals[agent_id, 0]},{agents_goals[agent_id, 1]}\n"
        )
    result_file.close()


def convert_ij_position_to_tswap(ij_pos: npt.NDArray) -> npt.NDArray:
    """
    Converts (i, j) grid coordinates to TSWAP grid coordinates.

    Parameters
    ----------
    ij_pos : npt.NDArray
        Array containing the (i, j) position.

    Returns
    -------
    npt.NDArray
        TSWAP grid position as an array.
    """
    tswap_x = ij_pos[1]
    tswap_y = ij_pos[0]
    return np.array((tswap_x, tswap_y), dtype=int)


def convert_ij_positions_to_tswap(ij_positions: npt.NDArray) -> npt.NDArray:
    """
    Converts multiple (i, j) grid coordinates to TSWAP grid coordinates.

    Parameters
    ----------
    ij_positions : npt.NDArray
        Array containing multiple (i, j) positions.

    Returns
    -------
    npt.NDArray
        Array of TSWAP (x, y) positions.
    """
    tswap_positions = np.zeros_like(ij_positions, dtype=int)
    for i, pos in enumerate(ij_positions):
        tswap_positions[i] = convert_ij_position_to_tswap(pos)
    return tswap_positions


def convert_real_position_to_tswap(
    real_xy: npt.NDArray, grid_height: int, cell_size: float
) -> npt.NDArray:
    """
    Converts real-world (x, y) coordinates to TSWAP grid coordinates.

    Parameters
    ----------
    real_xy : npt.NDArray
        Real-world (x, y) coordinates.
    grid_height : int
        Height of the grid in cells.
    cell_size : float
        Size of each cell in the grid.

    Returns
    -------
    npt.NDArray
        TSWAP grid coordinates as an array.
    """
    real_x = real_xy[0]
    real_y = real_xy[1]
    tswap_x = real_x // cell_size
    tswap_y = (grid_height * cell_size - real_y) // cell_size
    return np.array((tswap_x, tswap_y), dtype=int)


def convert_real_positions_to_tswap(
    real_xy_positions: npt.NDArray, grid_height: int, cell_size: float
) -> npt.NDArray:
    """
    Converts multiple real-world (x, y) coordinates to TSWAP grid coordinates.

    Parameters
    ----------
    real_xy_positions : npt.NDArray
        Array of real-world (x, y) coordinates.
    grid_height : int
        Height of the grid in cells.
    cell_size : float
        Size of each cell in the grid.

    Returns
    -------
    npt.NDArray
        Array of TSWAP (x, y) grid coordinates.
    """
    tswap_positions = np.zeros_like(real_xy_positions, dtype=int)
    for i, pos in enumerate(real_xy_positions):
        tswap_positions[i] = convert_real_position_to_tswap(pos, grid_height, cell_size)
    return tswap_positions


def convert_tswap_to_real_position(
    tswap_position: npt.NDArray, grid_height: int, cell_size: float
) -> npt.NDArray:
    """
    Converts TSWAP (x, y) grid coordinates to real-world (x, y) coordinates.

    Parameters
    ----------
    tswap_position : npt.NDArray
        TSWAP grid coordinates.
    grid_height : int
        Height of the grid in cells.
    cell_size : float
        Size of each cell in the grid.

    Returns
    -------
    npt.NDArray
        Real-world (x, y) coordinates as an array.
    """
    tswap_x = tswap_position[0]
    tswap_y = tswap_position[1]
    real_x = (tswap_x + 0.5) * cell_size
    real_y = (grid_height - tswap_y - 0.5) * cell_size
    return np.array((real_x, real_y), dtype=np.float64)


def convert_tswap_to_real_positions(
    tswap_positions: npt.NDArray, grid_height: int, cell_size: float
) -> npt.NDArray:
    """
    Converts multiple TSWAP  grid coordinates to real-world (x, y) coordinates.

    Parameters
    ----------
    tswap_positions : npt.NDArray
        Array of TSWAP (x, y) grid coordinates.
    grid_height : int
        Height of the grid in cells.
    cell_size : float
        Size of each cell in the grid.

    Returns
    -------
    npt.NDArray
        Array of real-world (x, y) coordinates.
    """
    real_xy_positions = np.zeros_like(tswap_positions, dtype=np.float64)
    for i, pos in enumerate(tswap_positions):
        real_xy_positions[i] = convert_tswap_to_real_position(
            pos, grid_height, cell_size
        )
    return real_xy_positions


def read_tswap_log(file_path: str) -> Tuple[int, bool, int, int, int, npt.NDArray]:
    """
    Reads a TSWAP log file and extracts experiment results.

    Parameters
    ----------
    file_path : str
        Path to the TSWAP log file.

    Returns
    -------
    Tuple[int, bool, int, int, int, npt.NDArray]
        A tuple containing:
        - Number of agents (int)
        - Solved status (bool)
        - Flowtime (int)
        - Makespan (int)
        - Runtime (int)
        - Solution as an ndarray of shape (agents_num, makespan + 1, 2) with positions.
    """
    solved = False
    flowtime = 0
    makespan = 0
    runtime = 0
    agents_num = 0
    log_file = open(file_path, "r")
    for line in log_file:
        if line.find(LOG_SOLUTION) != -1:
            break
        ind_val = line.split("=")
        if len(ind_val) == 2:
            indicator, value = ind_val
            if indicator == LOG_SOLVED:
                solved = bool(value)
            elif indicator == LOG_FLOWTIME:
                flowtime = int(value)
            elif indicator == LOG_MAKESPAN:
                makespan = int(value)
            elif indicator == LOG_RUNTIME:
                runtime = int(value)
            elif indicator == LOG_AGENTS:
                agents_num = int(value)
    solution = np.zeros((agents_num, makespan + 1, 2), dtype=int)
    for line in log_file:
        step, positions = line.split(":(")
        step = int(step)
        positions = positions.replace("),\n", "")
        positions = positions.split("),(")
        for agent_id, pos_str in enumerate(positions):
            pos = list(map(int, pos_str.split(",")))
            solution[agent_id, step] = np.array(pos, dtype=int)
    return agents_num, solved, flowtime, makespan, runtime, solution
