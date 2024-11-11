from manavlib.utils.astar_algorithm import expand_map_from_pos
from manavlib.utils.map import Map

from typing import Dict, Tuple




class PathTable:
    """
    PathTable for storing and checking connectivity information on a grid map.
    Uses connected components to identify reachable areas within a map.

    Attributes
    ----------
    search_map : Map
        A map representation used for pathfinding and connectivity checking.
    connected_components : Dict[Tuple[int, int], int]
        A dictionary mapping coordinates (i, j) to their connected component IDs.
    """

    def __init__(self, grid_map):
        """
        Initializes the PathTable by calculating connected components on the grid map.
        Each cell in the grid map is assigned a connected component ID based on reachability.

        Parameters
        ----------
        grid_map : array-like
            The grid map representation where each cell indicates traversability.
        """
        self.search_map = Map(grid_map)
        self.connected_components = dict()
        
        curr_component_id = 0
        for i in range(0, self.search_map.get_size()[0]):
            for j in range(0, self.search_map.get_size()[1]):
                if not self.search_map.traversable(i, j):
                    continue
                if (i, j) in self.connected_components:
                    continue
                
                expanded = expand_map_from_pos(self.search_map, (i, j))
                for node in expanded:
                    self.connected_components[(node.i, node.j)] = curr_component_id
                curr_component_id += 1

    def path_exists(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> bool:
        """
        Checks if a path exists between two positions on the grid map.

        Parameters
        ----------
        pos : Tuple[int, int]
            Starting position coordinates (i, j) on the grid map.
        goal : Tuple[int, int]
            Goal position coordinates (i, j) on the grid map.

        Returns
        -------
        bool
            True if a path exists between the starting and goal positions, False otherwise.
        """
        return self.connected_components[tuple(pos)] == self.connected_components[tuple(goal)]
