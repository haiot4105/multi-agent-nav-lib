"""
Utility functions and classes for detecting and representing obstacle boundaries in a grid. 

This module provides tools for:
- Detecting borders of obstacles in a 2D grid.
- Representing obstacle boundaries as connected segments and polygons.
- Converting grid-based representations to Cartesian coordinates.

Warning!
----------
This is an experimental module and requires further development and debugging.
"""

import numpy as np
import numpy.typing as npt
from typing import List, Optional, Tuple, Union, Set
from manavlib.common.transform import convert_ij_to_xy


MAP_OBSTACLE = 1


class _Segment:
    """
    Represents a line segment with start (`begin`) and end (`end`) points.

    Attributes
    ----------
    begin : np.ndarray or None
        The starting point of the segment.
    end : np.ndarray or None
        The ending point of the segment.
    """
    
    def __init__(self):
        self.begin = None
        self.end = None

    def connect(self, other) -> bool:
        """
        Attempts to connect this segment with another segment.

        Parameters
        ----------
        other : _Segment
            The other segment to connect with.

        Returns
        -------
        bool
            True if the segments were successfully connected, False otherwise.
        """
        if np.array_equal(self.begin, other.begin):
            if np.any(self.end == other.end):
                self.begin = other.end
                return True
        if np.array_equal(self.begin, other.end):
            if np.any(self.end == other.begin):
                self.begin = other.begin
                return True
        if np.array_equal(self.end, other.end):
            if np.any(self.begin == other.begin):
                self.end = other.begin
                return True
        if np.array_equal(self.end, other.begin):
            if np.any(self.begin == other.end):
                self.end = other.end
                return True
        return False


class _Polygon:
    """
    Represents a polygon as a collection of connected segments.

    Attributes
    ----------
    lines : List[_Segment]
        The list of line segments forming the polygon.
    begin : np.ndarray or None
        The starting point of the polygon. (Сoincides with the end, if all the polygon is built correctly)
    end : np.ndarray or None
        The ending point of the polygon. (Сoincides with the begin, if all the polygon is built correctly)
    """
    
    def __init__(self):
        self.lines: List[_Segment] = []
        self.begin = None
        self.end = None

    def __str__(self):
        return "{" + str(self.begin) + "; " + str(self.end) + "}"

    def __repr__(self):
        return "{" + str(self.begin) + "; " + str(self.end) + "}"

    def add(self, segment) -> bool:
        """
        Adds a segment to the polygon, attempting to connect it to existing segments.

        Parameters
        ----------
        segment : _Segment
            The segment to add.

        Returns
        -------
        bool
            True if the segment was successfully added, False otherwise.
        """
        if len(self.lines) == 0:
            self.lines.append(segment)
            self.begin = segment.begin
            self.end = segment.end
            return True
        if np.array_equal(self.begin, segment.begin):
            self.begin = segment.end
            if not self.lines[0].connect(segment):
                self.lines.insert(0, segment)
            return True
        if np.array_equal(self.begin, segment.end):
            self.begin = segment.begin
            if not self.lines[0].connect(segment):
                self.lines.insert(0, segment)
            return True
        if np.array_equal(self.end, segment.end):
            self.end = segment.begin
            if not self.lines[-1].connect(segment):
                self.lines.append(segment)
            return True
        if np.array_equal(self.end, segment.begin):
            self.end = segment.end
            if not self.lines[-1].connect(segment):
                self.lines.append(segment)
            return True
        return False

    def connect(self, polygon) -> bool:
        """
        Connects this polygon with another polygon.

        Parameters
        ----------
        polygon : _Polygon
            The polygon to connect with.

        Returns
        -------
        bool
            True if the polygons were successfully connected, False otherwise.
        """
        if len(self.lines) == 0:
            self.lines = polygon.lines
            self.begin = polygon.begin
            self.end = polygon.end

        if polygon == self:
            if self.lines[0].connect(self.lines[-1]):
                self.lines.pop(-1)
                self.begin = self.end = self.lines[0].begin
            return True

        if np.array_equal(self.begin, polygon.begin):
            polygon.lines = polygon.lines[::-1]
            if self.lines[0].connect(polygon.lines[-1]):
                self.lines = polygon.lines[:-1] + self.lines
            else:
                self.lines = polygon.lines + self.lines
            self.begin = polygon.end
            return True
        if np.array_equal(self.begin, polygon.end):
            if self.lines[0].connect(polygon.lines[-1]):
                self.lines = polygon.lines[:-1] + self.lines
            else:
                self.lines = polygon.lines + self.lines
            self.begin = polygon.begin
            return True
        if np.array_equal(self.end, polygon.end):
            polygon.lines = polygon.lines[::-1]
            if self.lines[-1].connect(polygon.lines[0]):
                self.lines = self.lines + polygon.lines[1:]
            else:
                self.lines = self.lines + polygon.lines
            self.end = polygon.begin
            return True
        if np.array_equal(self.end, polygon.begin):
            if self.lines[-1].connect(polygon.lines[0]):
                self.lines = self.lines + polygon.lines[1:]
            else:
                self.lines = self.lines + polygon.lines
            self.end = polygon.end
            return True
        return False


def __cell_on_map(pos: Tuple[int, int], grid: npt.NDArray) -> bool:
    """
    Checks if a given position is within the bounds of the grid.

    Parameters
    ----------
    pos : Tuple[int, int]
        The grid position as (row, column).
    grid : np.ndarray
        The 2D grid map.

    Returns
    -------
    bool
        True if the position is within the grid bounds, False otherwise.
    """
    h, w = grid.shape
    if 0 <= pos[0] < h and 0 <= pos[1] < w:
        return True
    return False


def __check_is_border(pos: Tuple[int, int], grid: npt.NDArray) -> bool:
    """
    Determines if a cell is on the border of an obstacle.

    Parameters
    ----------
    pos : Tuple[int, int]
        The grid position as (row, column).
    grid : np.ndarray
        The 2D grid map.

    Returns
    -------
    bool
        True if the cell is on the border of an obstacle, False otherwise.
    """
    deltas = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    if not __cell_on_map(pos, grid) or grid[pos] != MAP_OBSTACLE:
        return False

    for delta in deltas:
        new_pos = pos[0] + delta[0], pos[1] + delta[1]
        if not __cell_on_map(new_pos, grid) or grid[new_pos] != MAP_OBSTACLE:
            return True

    return False


def __get_borderlines(pos: Tuple[int, int], grid: npt.NDArray, cell_size: float) -> List[_Segment]:
    """
    Retrieves the border segments of an obstacle at a given position.

    Parameters
    ----------
    pos : Tuple[int, int]
        The grid position as (row, column).
    grid : np.ndarray
        The 2D grid map.
    cell_size : float
        The size of each cell in the grid.

    Returns
    -------
    List[_Segment]
        A list of segments representing the borders of the obstacle.
    """
    deltas = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    deltas_bl = [
        np.array([[0.5, -0.5], [0.5, 0.5]]),
        np.array([[-0.5, -0.5], [0.5, -0.5]]),
        np.array([[-0.5, 0.5], [-0.5, -0.5]]),
        np.array([[0.5, 0.5], [-0.5, 0.5]]),
    ]

    if not __cell_on_map(pos, grid) or grid[pos] != MAP_OBSTACLE:
        return []

    borderlines = []
    h, w = grid.shape
    xy_pos = convert_ij_to_xy(pos, h, cell_size)
    for i, delta in enumerate(deltas):
        new_pos = pos[0] + delta[0], pos[1] + delta[1]

        if not __cell_on_map(new_pos, grid) or grid[new_pos] != MAP_OBSTACLE:
            segment = _Segment()
            segment.begin = np.round(xy_pos + deltas_bl[i][0], 1)
            segment.end = np.round(xy_pos + deltas_bl[i][1], 1)
            borderlines.append(segment)
    return borderlines


def __get_successors(pos: Tuple[int, int], grid: npt.NDArray) -> List[Tuple[int, int]]:
    """
    Finds neighboring border cells for a given position.

    Parameters
    ----------
    pos : tuple of int
        The grid position as (row, column).
    grid : np.ndarray
        The 2D grid map.

    Returns
    -------
    List[Tuple[int, int]]
        A list of neighboring border positions as (row, column).
    """
    deltas = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    successors = []
    for delta in deltas:
        new_pos = pos[0] + delta[0], pos[1] + delta[1]
        if __check_is_border(new_pos, grid):
            if abs(delta[0]) + abs(delta[1]) == 2:
                if grid[pos[0], new_pos[1]] != MAP_OBSTACLE and grid[new_pos[0], pos[1]] != MAP_OBSTACLE:
                    continue

            successors.append(new_pos)
    return successors


def __compute_border_cells(grid: npt.NDArray) -> List[Set[Tuple[int, int]]]:
    """
    Identifies all border cells grouped by connected obstacles.

    Parameters
    ----------
    grid : np.ndarray
        The 2D grid map.

    Returns
    -------
    List[Set[Tuple[int, int]]]
        A list of sets, where each set contains the positions of connected border cells.
    """
    h, w = grid.shape
    closed = set()
    queue = []
    obstacles = []
    for i in range(h):
        for j in range(w):
            if (i, j) in closed or not __check_is_border((i, j), grid):
                continue

            obstacle = {(i, j)}
            queue.append((i, j))
            while len(queue) != 0:
                curr = queue.pop()
                closed.add(curr)
                obstacle.add(curr)

                for successor in __get_successors(curr, grid):
                    if successor in closed:
                        continue
                    queue.append(successor)

            obstacles.append(obstacle)
    return obstacles


def compute_poligons(grid: npt.NDArray, cell_size: float) -> List[List[npt.NDArray]]:
    """
    Computes polygons representing obstacles in a grid.

    Parameters
    ----------
    grid : np.ndarray
        The 2D grid map.
    cell_size : float
        The size of each cell in the grid.

    Returns
    -------
    List[List[np.ndarray]]
        A list of polygons, where each polygon is a list of points in Cartesian coordinates.
    """
    obstacles = __compute_border_cells(grid)
    result = []
    for obstacle in obstacles:
        polygons = dict()
        polygon = None

        for obst_cell in obstacle:
            borderlines = __get_borderlines(obst_cell, grid, cell_size)

            for s_id, segment in enumerate(borderlines):
                if tuple(segment.begin) not in polygons and tuple(segment.end) not in polygons:
                    polygon = _Polygon()
                    polygon.add(segment)
                    polygons[tuple(polygon.begin)] = polygon
                    polygons[tuple(polygon.end)] = polygon
                    continue

                if tuple(segment.begin) in polygons:
                    point = segment.begin
                    polygon = polygons[tuple(point)]
                    polygons.pop(tuple(point), None)
                    polygon.add(segment)

                    if tuple(segment.end) in polygons:
                        point2 = segment.end
                        another_polygon = polygons[tuple(point2)]
                        polygons.pop(tuple(point2), None)
                        polygon.connect(another_polygon)

                    polygons[tuple(polygon.begin)] = polygon
                    polygons[tuple(polygon.end)] = polygon
                    continue

                if tuple(segment.end) in polygons:
                    point = segment.end
                    polygon = polygons[tuple(point)]
                    polygons.pop(tuple(point), None)
                    polygon.add(segment)

                    if tuple(segment.begin) in polygons:
                        point2 = segment.begin
                        another_polygon = polygons[tuple(point2)]
                        polygons.pop(tuple(point2), None)
                        polygon.connect(another_polygon)

                    polygons[tuple(polygon.begin)] = polygon
                    polygons[tuple(polygon.end)] = polygon
        if len(polygons) != 1:
            print("Error", polygons)
        result = result + list(polygons.values())
    result = __convert_to_points_list(result)

    h, w = grid.shape
    boundary = [np.array([0, 0], dtype=np.float64), np.array([0, h], dtype=np.float64), np.array([w, h], dtype=np.float64), np.array([w, 0], dtype=np.float64)]
    result.append(boundary)
    return result


def __convert_to_points_list(polygons: List[_Polygon]) -> List[List[npt.NDArray]]:
    """
    Converts a list of _Polygon objects into a list of points.

    Parameters
    ----------
    polygons : List[pPolygon]
        The list of _Polygon objects.

    Returns
    -------
    List[List[np.ndarray]]
        A list of polygons, where each polygon is represented as a list of points.
    """
    result = []
    for polygon in polygons:
        polygon_points = []
        for segment in polygon.lines:
            p = segment.end
            polygon_points.append(p)
        result.append(polygon_points)
    return result
