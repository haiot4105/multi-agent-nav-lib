from typing import Callable, Dict, Iterable, List, Optional, Tuple, Type, Union
import numpy as np
from manavlib.utils.node import Node
from manavlib.utils.map import Map, compute_cost
from manavlib.utils.search_tree import SearchTree

def manhattan_distance(i1: int, j1: int, i2: int, j2: int) -> int:
    """
    Computes the Manhattan distance between two cells on a grid.

    Parameters
    ----------
    i1, j1 : int
        (i, j) coordinates of the first cell on the grid.
    i2, j2 : int
        (i, j) coordinates of the second cell on the grid.

    Returns
    -------
    int
        Manhattan distance between the two cells.
    """
    return abs(i1 - i2) + abs(j1 - j2)


def astar_search(
        task_map: Map,
        start_i: int,
        start_j: int,
        goal_i: int,
        goal_j: int,
        heuristic_func: Callable
) -> Tuple[bool, Optional[Node], Optional[int], Dict[Node, Node]]:
    """
    Implements the A* search algorithm.

    Parameters
    ----------
    task_map : Map
        The grid or map being searched.
    start_i, start_j : int, int
        Starting coordinates.
    goal_i, goal_j : int, int
        Goal coordinates.
    heuristic_func : Callable
        Heuristic function for estimating the distance from a node to the goal.

    Returns
    -------
    Tuple[bool, Optional[Node], Optional[int], Dict[Node]]
        Tuple containing:
        - A boolean indicating if a path was found.
        - The last node in the found path or None.
        - Path length if a path is found, else None.
        - Expanded nodes
    """
    ast = SearchTree()
    steps = 0
    start_node = Node(start_i, start_j, g=0, h=heuristic_func(start_i, start_j, goal_i, goal_j))
    ast.add_to_open(start_node)

    while not ast.open_is_empty():
        current = ast.get_best_node_from_open()

        if current is None:
            break

        ast.add_to_closed(current)

        if (current.i, current.j) == (goal_i, goal_j):
            return True, current, current.g, ast.expanded

        for i, j in task_map.get_neighbors(current.i, current.j):
            new_node = Node(i, j)
            if not ast.was_expanded(new_node):
                new_node.g = current.g + compute_cost(current.i, current.j, i, j)
                new_node.h = heuristic_func(i, j, goal_i, goal_j)
                new_node.f = new_node.g + new_node.h
                new_node.parent = current
                ast.add_to_open(new_node)

        steps += 1

    return False, None, None, ast.expanded


def make_path(goal: Node) -> List[Node]:
    """
    Creates a path by tracing parent pointers from the goal node to the start node.

    Parameters
    ----------
    goal : Node
        The goal node from which to trace back to the start node.

    Returns
    -------
    List[Node]
        List of nodes representing the path from start to goal.
    """
    current = goal
    path = []
    while current.parent:
        path.append(np.array((current.i, current.j), dtype=np.int32))
        current = current.parent
    path.append(current)
    return path


def find_path(search_map: Map, pos: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Node]]:
    """
    Finds a path from a starting position to a goal position using A* search.

    Parameters
    ----------
    search_map : Map
        The map on which to perform the search.
    pos : Tuple[int, int]
        The starting position (i, j) coordinates.
    goal : Tuple[int, int]
        The goal position (i, j) coordinates.

    Returns
    -------
    Optional[List[Node]]
        A list of nodes representing the path, or None if no path was found.
    """
    start_i, start_j = pos
    goal_i, goal_j = goal
    path_found, last_node, length = astar_search(search_map, start_i, start_j, goal_i, goal_j, manhattan_distance)

    if path_found:
        return make_path(last_node)[:-1]
    else:
        return None


def find_length(search_map: Map, pos: Tuple[int, int], goal: Tuple[int, int]) -> Optional[int]:
    """
    Finds the length of a path from a starting position to a goal position using A* search.

    Parameters
    ----------
    search_map : Map
        The map on which to perform the search.
    pos : Tuple[int, int]
        The starting position (i, j) coordinates.
    goal : Tuple[int, int]
        The goal position (i, j) coordinates.

    Returns
    -------
    Optional[List[Node]]
        A list of nodes representing the path, or None if no path was found.
    """
    start_i, start_j = pos
    goal_i, goal_j = goal
    path_found, last_node, length = astar_search(search_map, start_i, start_j, goal_i, goal_j, manhattan_distance)

    if path_found:
        return length
    else:
        return None
    

def expand_map_from_pos(search_map: Map, pos: Tuple[int, int]) -> Dict[Node, Node]:
    """
    Expands all reachable nodes from a starting position on the map.

    Parameters
    ----------
    search_map : Map
        The map on which to perform the expansion.
    pos : Tuple[int, int]
        The starting position (i, j) coordinates.

    Returns
    -------
    Dict[Node, Node]
        A dictionary of expanded nodes.
        Allows to get the corresponding node in the search tree, including g-, f-values and the node, 
        through which the shortest path from pos to the selected cell (i, j) passed.
    """
    start_i, start_j = pos
    goal_i, goal_j = (-1, -1)
    path_found, last_node, length, expanded = astar_search(search_map, start_i, start_j, goal_i, goal_j, lambda i1, j1, i2, j2 : 0)
    return expanded