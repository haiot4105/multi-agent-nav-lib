"""
This module provides functions for generating start and goal positions for agents in various
scenarios. The utilities are designed to create diverse configurations for 
multi-agent pathfinding experiments, supporting both discrete and continuous position formats.

The functions include:
- Creating circular arrangements of agents with opposing start and goal positions.
- Generating random start and goal positions on an empty grid map.
- Organizing agents into a structured mesh (grid) layout.
- Creating random start and goal positions on a grid map with obstacles, ensuring that paths
  between start and goal positions are valid.

Notes
----------------
The module supports two types of position formats:
1. **Discrete (i, j) Coordinates**: Used in grid-based pathfinding, where each position is 
   defined by row and column indices.
2. **Continuous (x, y, theta, v_x, v_y) Coordinates**: Used in real-world scenarios with 
   additional orientation and velocity components. In continuous format:
   - `(x, y)` represents the position.
   - `theta` represents the orientation (yaw) angle.
   - `(v_x, v_y)` represents velocity components.
"""

import numpy as np
import numpy.typing as npt
import manavlib.utils.map as search_map
from manavlib.utils.path_table import PathTable
from typing import Tuple


def create_circle_instance(
    circ_center: Tuple[float, float],
    circ_r: float,
    agents_num: int,
    angle_offset: float = 0.0,
) -> Tuple[npt.NDArray, npt.NDArray]:
    """
    Creates a circular instance of start and goal states for agents.
    Each state is a five-dimensional vector in the format (x, y, theta, v_x, v_y):
    - `x, y` are the position coordinates.
    - `theta` is the orientation (yaw) angle.
    - `v_x, v_y` are the velocity components.

    The yaw angle of start state is chosen such that the agent is directed towards the goal.
    The yaw angle of goal state is the same. Initial velocity (v_x, v_y) is zero.
    
    Discrete format is not supported.

    Parameters
    ----------
    circ_center : Tuple[float, float]
        The (x, y) coordinates of the circle's center.
    circ_r : float
        The radius of the circle.
    agents_num : int
        The number of agents.
    angle_offset : float, optional
        Offset angle to adjust agent positions around the circle (default is 0.0).

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Two numpy arrays representing the start and goal states of the agents, respectively.
    """
    start_states = np.zeros((agents_num, 5), dtype=np.float64)
    goal_states = np.zeros((agents_num, 5), dtype=np.float64)
    ang_steps = np.linspace(
        0.0 + angle_offset, 2 * np.pi + angle_offset, agents_num + 1
    )

    for i, ang in enumerate(ang_steps):
        if i == agents_num:
            break

        st_x = circ_r * np.cos(ang)
        st_y = circ_r * np.sin(ang)

        g_x = circ_r * np.cos(ang + np.pi)
        g_y = circ_r * np.sin(ang + np.pi)

        st_x += circ_center[0]
        g_x += circ_center[0]

        st_y += circ_center[1]
        g_y += circ_center[1]

        dx = g_x - st_x
        dy = g_y - st_y

        st_theta = np.arctan2(dy, dx)
        g_theta = st_theta

        start_states[i] = np.array([st_x, st_y, st_theta, 0.0, 0.0])
        goal_states[i] = np.array([g_x, g_y, g_theta, 0.0, 0.0])

    return start_states, goal_states


def create_random_empty_instance(
    agents_num: int,
    grid_height: int,
    grid_width: int,
    cell_size: float,
    empty_cells_around: bool = True,
    discrete: bool = False,
) -> Tuple[npt.NDArray, npt.NDArray]:
    """
    Generates random start and goal positions for agents on an empty map.

    In the discrete case, each states are represented by (i, j) grid coordinates.
    In the continuous case, each state is a five-dimensional vector in the format (x, y, theta, v_x, v_y):
    - `x, y` are the position coordinates.
    - `theta` is the orientation (yaw) angle.
    - `v_x, v_y` are the velocity components.

    For all agents, initial and goal yaw angles (theta) are uniformly randomized, and initial velocities
    (v_x, v_y) are set to zero.

    Parameters
    ----------
    agents_num : int
        Number of agents.
    grid_height : int
        Height of the grid.
    grid_width : int
        Width of the grid.
    cell_size : float
        Size of each grid cell.
    empty_cells_around : bool, optional
        Whether to leave surrounding cells empty around each agent's start and goal positions
        (default is True).
    discrete : bool, optional
        If True, generates positions in discrete grid coordinates (i, j);
        if False, uses continuous coordinates (x, y, theta, v_x, v_y) (default is False).

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Two numpy arrays representing the start and goal states of the agents, respectively.
    """
    dim = 2 if discrete else 5
    dtype = np.int32 if discrete else np.float64

    start_states = np.zeros((agents_num, dim), dtype=dtype)
    goal_states = np.zeros((agents_num, dim), dtype=dtype)

    occupied_start_cells = set()
    occupied_goal_cells = set()

    if empty_cells_around:
        ds = [
            [0, 0],
            [0, 1],
            [1, 0],
            [0, -1],
            [-1, 0],
            [-1, -1],
            [-1, 1],
            [1, -1],
            [1, 1],
        ]
    else:
        ds = [[0, 0]]

    for agent_id in range(agents_num):
        while True:
            curr_start = (
                np.random.randint(0, grid_height),
                np.random.randint(0, grid_width),
            )

            correct = True

            for d in ds:
                curr_n = (curr_start[0] + d[0], curr_start[1] + d[1])
                if curr_n in occupied_start_cells:
                    correct = False
                    break

            if correct:
                occupied_start_cells.add(curr_start)
                if discrete:
                    start_states[agent_id, 0] = curr_start[0]
                    start_states[agent_id, 1] = curr_start[1]
                else:
                    start_states[agent_id, 0] = cell_size * (curr_start[1] + 0.5)
                    start_states[agent_id, 1] = cell_size * (
                        grid_height - curr_start[0] - 0.5
                    )
                    start_states[agent_id, 2] = np.random.uniform(0, 2 * np.pi)
                    start_states[agent_id, 3] = 0.0
                    start_states[agent_id, 4] = 0.0
                break

        while True:
            curr_goal = (
                np.random.randint(0, grid_height),
                np.random.randint(0, grid_width),
            )

            correct = True
            for d in ds:
                curr_n = (curr_goal[0] + d[0], curr_goal[1] + d[1])
                if curr_n in occupied_goal_cells:
                    correct = False
                    break

            if correct:
                occupied_goal_cells.add(curr_goal)
                if discrete:
                    goal_states[agent_id, 0] = curr_goal[0]
                    goal_states[agent_id, 1] = curr_goal[1]
                else:
                    goal_states[agent_id, 0] = cell_size * (curr_goal[1] + 0.5)
                    goal_states[agent_id, 1] = cell_size * (
                        grid_height - curr_goal[0] - 0.5
                    )
                    goal_states[agent_id, 2] = np.random.uniform(0, 2 * np.pi)
                    goal_states[agent_id, 3] = 0.0
                    goal_states[agent_id, 4] = 0.0
                break
    return start_states, goal_states


def create_mesh_instance(
    agents_num: int, distance_between: float, offset: Tuple[float, float]
) -> Tuple[npt.NDArray, npt.NDArray]:
    """
    Creates an instance of start and goal states for agents arranged in a grid (mesh) pattern.
    Each state is a five-dimensional vector in the format (x, y, theta, v_x, v_y):
    - `x, y` are the position coordinates.
    - `theta` is the orientation (yaw) angle.
    - `v_x, v_y` are the velocity components.

    For all agents, initial and goal yaw angles (theta) are set to zero, and initial velocities
    (v_x, v_y) are also set to zero.

    This function organizes a specified number of agents into a square mesh and assigns
    them randomized goal positions on the same mesh. The positions for both start and goal
    states are calculated based on the specified spacing between agents and an (x, y) offset
    to position the grid within a larger coordinate system.


    Parameters
    ----------
    agents_num : int
        The total number of agents, which must be a perfect square. This allows the agents
        to be organized into a square grid layout.
    distance_between : float
        The distance between adjacent agents in the grid, defining the spacing of the mesh.
    offset : Tuple[float, float]
        A tuple (x, y) representing the offset from the origin to position the bottom-left
        corner of the grid in the global coordinate system.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, np.ndarray]
        Two numpy arrays representing the start and goal states of the agents, respectively. One numpy array with shuffled agent IDs indicating the goal assignment on the mesh.
    """
    start_states = np.zeros((agents_num, 5), dtype=np.float64)
    goal_states = np.zeros((agents_num, 5), dtype=np.float64)

    grid_h = int(agents_num**0.5)

    if grid_h * grid_h != agents_num:
        print("Illegal number of agents")
        return

    start_ids = np.arange(agents_num).reshape((grid_h, grid_h))
    goal_ids = np.arange(agents_num)
    np.random.shuffle(goal_ids)
    goal_ids = goal_ids.reshape((grid_h, grid_h))

    for i in range(grid_h):
        for j in range(grid_h):
            st_agent = start_ids[i, j]
            gl_agent = goal_ids[i, j]

            x = offset[0] + j * distance_between
            y = offset[1] + (grid_h - i - 1) * distance_between

            start_states[st_agent, 0] = x
            start_states[st_agent, 1] = y
            start_states[st_agent, 2] = 0.0
            start_states[st_agent, 3] = 0.0
            start_states[st_agent, 4] = 0.0

            goal_states[gl_agent, 0] = x
            goal_states[gl_agent, 1] = y
            goal_states[gl_agent, 2] = 0.0
            goal_states[gl_agent, 3] = 0.0
            goal_states[gl_agent, 4] = 0.0

    return start_states, goal_states, goal_ids


def create_random_grid_map_instance(
    agents_num: int,
    grid_map: npt.NDArray,
    cell_size: float,
    empty_cells_around: bool = True,
    discrete: bool = False,
) -> Tuple[npt.NDArray, npt.NDArray]:
    """
    This function generates random start and goal positions for a given number of agents on a
    grid map that includes obstacles. Each agent’s start and goal positions are selected to
    ensure they are in passable areas and that a path exists between them. The function supports
    both discrete and continuous coordinates for start and goal states.

    In the discrete case, each states are represented by (i, j) grid coordinates.
    In the continuous case, each state is a five-dimensional vector in the format (x, y, theta, v_x, v_y):
    - `x, y` are the position coordinates.
    - `theta` is the orientation (yaw) angle.
    - `v_x, v_y` are the velocity components.

    For all agents, initial and goal yaw angles (theta) are uniformly randomized, and initial velocities
    (v_x, v_y) are set to zero.

    Parameters
    ----------
    agents_num : int
        Number of agents.
    grid_map : np.ndarray
        A 2D numpy array representing the grid map, where non-zero values indicate obstacles, and
        zero values indicate free cells.
    cell_size : float
        Size of each grid cell.
    empty_cells_around : bool, optional
        Whether to leave surrounding cells empty around each agent's start and goal positions
        (default is True).
    discrete : bool, optional
        If True, generates positions in discrete grid coordinates (i, j);
        if False, uses continuous coordinates (x, y, theta, v_x, v_y) (default is False).

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Two numpy arrays representing the start and goal states of the agents, respectively.
    """
    dim = 2 if discrete else 5
    dtype = np.int32 if discrete else np.float64
    astar_map = search_map.Map(grid_map)
    grid_height, grid_width = grid_map.shape

    start_states = np.zeros((agents_num, dim), dtype=dtype)
    grid_start_states = np.zeros((agents_num, 2), dtype=np.int32)
    goal_states = np.zeros((agents_num, dim), dtype=dtype)

    occupied_start_cells = set()
    occupied_goal_cells = set()

    path_table = PathTable(grid_map)

    if empty_cells_around:
        ds = [
            [0, 0],
            [0, 1],
            [1, 0],
            [0, -1],
            [-1, 0],
            [-1, -1],
            [-1, 1],
            [1, -1],
            [1, 1],
        ]
    else:
        ds = [[0, 0]]

    for agent_id in range(agents_num):
        while True:
            curr_start = (
                np.random.randint(0, grid_height),
                np.random.randint(0, grid_width),
            )

            correct = True
            for d in ds:
                curr_n = (curr_start[0] + d[0], curr_start[1] + d[1])
                if curr_n in occupied_start_cells:
                    correct = False
                    break

            if not correct:
                continue
            if grid_map[curr_start[0], curr_start[1]]:
                continue

            occupied_start_cells.add(curr_start)
            grid_start_states[agent_id] = curr_start
            if discrete:
                start_states[agent_id, 0] = curr_start[0]
                start_states[agent_id, 1] = curr_start[1]
            else:
                start_states[agent_id, 0] = cell_size * (curr_start[1] + 0.5)
                start_states[agent_id, 1] = cell_size * (
                    grid_height - curr_start[0] - 0.5
                )
                start_states[agent_id, 2] = np.random.uniform(0, 2 * np.pi)
                start_states[agent_id, 3] = 0.0
                start_states[agent_id, 4] = 0.0
            break

    for agent_id in range(agents_num):
        while True:
            curr_goal = (
                np.random.randint(0, grid_height),
                np.random.randint(0, grid_width),
            )

            correct = True
            for d in ds:
                curr_n = (curr_goal[0] + d[0], curr_goal[1] + d[1])
                if curr_n in occupied_goal_cells:
                    correct = False
                    break

            if not correct or grid_map[curr_goal[0], curr_goal[1]]:
                continue

            path_exists = path_table.path_exists(curr_goal, grid_start_states[agent_id])
            if not path_exists:
                continue

            occupied_goal_cells.add(curr_goal)
            if discrete:
                goal_states[agent_id, 0] = curr_goal[0]
                goal_states[agent_id, 1] = curr_goal[1]
            else:
                goal_states[agent_id, 0] = cell_size * (curr_goal[1] + 0.5)
                goal_states[agent_id, 1] = cell_size * (
                    grid_height - curr_goal[0] - 0.5
                )
                goal_states[agent_id, 2] = np.random.uniform(0, 2 * np.pi)
                goal_states[agent_id, 3] = 0.0
                goal_states[agent_id, 4] = 0.0
            break
    return start_states, goal_states
