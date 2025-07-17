"""
This module provides functions to create, read, and manage XML files for multi-agent navigation 
experiments, specifically tailored for handling configuration, map, agent, and log files in XML format.
The utilities assist in setting up experiment parameters, defining agent configurations, and 
storing results in a structured format compatible with XML-based systems.

Notes
-----
These utilities are designed for XML-based experiment configurations files. 
The functions use lxml and xml.dom.minidom for XML parsing and formatting, ensuring files are written 
with proper structure and indentation. Custom agent and algorithm parameters must be defined as in the 
`manavlib.common.params` module for compatibility with this system.

Please note that not all functions are fully implemented. The `create_log_file` function is currently 
a placeholder and will need to be developed further to support log file creation.
"""

from re import A
from lxml import etree
import xml.dom.minidom
import numpy as np
import sys
from copy import copy, deepcopy
import numpy.typing as npt
from typing import List, Optional, Tuple, Union, Iterable
import json

sys.path.append("../../")
import manavlib.common.params as params
from manavlib.common.params import BaseAgentParams, BaseAlgParams, ExperimentParams


# XML Tag and Parameter Constants
SUMMARY_TAG = "summary"
SUCCESS_PARAM = "success"
RUNTIME_PARAM = "time"
COLLISIONS_PARAM = "collisions"
MAKESPAN_PARAM = "makespan"
TASK_ID_PARAM = "task_id"
AGENTS_NUM_PARAM = "number"
LOG_STEP_TAG = "step"
LOG_AGENT_TAG = "agent"
LOG_POS_X_PARAM = "x"
LOG_POS_Y_PARAM = "y"
LOG_POS_I_PARAM = "i"
LOG_POS_J_PARAM = "j"
ROOT_TAG = "root"
NUM_PARAM = "number"
AGENTS_TAG = "agents"
AGENT_TAG = "agent"
DEFAULT_AGENT_TAG = "default_agent"
START_X_PARAM = "s.x"
START_Y_PARAM = "s.y"
START_THETA_PARAM = "s.th"
START_I_PARAM = "s.i"
START_J_PARAM = "s.j"
GOAL_X_PARAM = "g.x"
GOAL_Y_PARAM = "g.y"
GOAL_THETA_PARAM = "g.th"
GOAL_I_PARAM = "g.i"
GOAL_J_PARAM = "g.j"
ID_PARAM = "id"
OCCUPANCY_GRID_TAG = "occupancy_grid"
WIDTH_TAG = "width"
HEIGHT_TAG = "height"
CELL_SIZE_TAG = "cell_size"
GRID_TAG = "grid"
ROW_TAG = "row"
DYN_MODEL_TYPE_PARAM = "model_type"
ALG_NAME_TAG = "name"
EXP_PARAM_TAG = "experiment"
ALG_PARAM_TAG = "algorithm"

POLYGON_OBSTACLES_TAG = "polygon_obstacles"
POLYGON_OBSTACLE_TAG = "obstacle"
POLYGON_VERTEX_TAG = "vertex"
VERTEX_X_PARAM = "v.x"
VERTEX_Y_PARAM = "v.y"


def create_map_file(
    path: str,
    occupancy_grid: npt.NDArray,
    cell_size: float,
    obstacles: List[List[npt.NDArray]] | None = None,
) -> None:
    """
    Creates an XML map file with grid data in occupancy format.

    Parameters
    ----------
    path : str
        The file path where the map XML will be saved.
    occupancy_grid : np.ndarray
        A 2D numpy array representing the map grid, where `1` represents obstacles
        and `0` represents passable areas.
    cell_size : float
        The size of each cell in the grid.
    obstacles : List[List[npt.NDArray]] | None
        A list of polygons, where each polygon is represented as a list of points 
        in Cartesian coordinates (in counterclockwise order). If provided, these 
        polygons will be included as obstacle data in the XML file.
    """
    root_tag = etree.Element(ROOT_TAG)
    height = occupancy_grid.shape[0]
    width = occupancy_grid.shape[1]
    map_tag = etree.SubElement(root_tag, OCCUPANCY_GRID_TAG)

    w_tag = etree.SubElement(map_tag, WIDTH_TAG)
    w_tag.text = str(width)

    h_tag = etree.SubElement(map_tag, HEIGHT_TAG)
    h_tag.text = str(height)

    cs_tag = etree.SubElement(map_tag, CELL_SIZE_TAG)
    cs_tag.text = str(cell_size)

    gridtag = etree.SubElement(map_tag, GRID_TAG)

    for i in range(height):
        row_str = ""
        row_tag = etree.SubElement(gridtag, ROW_TAG)
        for j in range(width):
            if occupancy_grid[i, j]:
                row_str += "1 "
            else:
                row_str += "0 "
        row_tag.text = row_str[:-1]

    if obstacles is not None:
        obstacles_tag = etree.SubElement(root_tag, POLYGON_OBSTACLES_TAG)
        for polygon in obstacles:
            obstacle_tag = etree.SubElement(obstacles_tag, POLYGON_OBSTACLE_TAG)
            for point in polygon:
                vertex_tag = etree.SubElement(obstacle_tag, POLYGON_VERTEX_TAG)
                vertex_tag.set(VERTEX_X_PARAM, str(point[0]))
                vertex_tag.set(VERTEX_Y_PARAM, str(point[1]))

    tree = etree.ElementTree(root_tag)
    file = open(path, "w")
    xml_string = etree.tostring(
        tree, pretty_print=True, xml_declaration=True, encoding="utf-8"
    ).decode()
    pretty_xml_string = "\n".join(
        [
            line
            for line in xml.dom.minidom.parseString(xml_string)
            .toprettyxml()
            .split("\n")
            if line.strip()
        ]
    )
    file.write(pretty_xml_string)
    file.close()


def create_agents_file(
    path: str,
    start_states: npt.NDArray,
    goal_states: npt.NDArray,
    default_agent_params: BaseAgentParams,
    agents_params: Optional[List[BaseAgentParams]] = None,
) -> None:
    """
    Creates an XML file with agent configurations, including start and goal states.

    Parameters
    ----------
    path : str
        The file path where the agents XML will be saved.
    start_states : np.ndarray
        Array of agent starting states.
    goal_states : np.ndarray
        Array of agent goal states.
    default_agent_params : BaseAgentParams
        Default parameters for all agents.
    agents_params : Optional[List[BaseAgentParams]], optional
        List of specific parameters for each agent. Defaults to None, in which case
        all agents use the default parameters.
    """
    default_agent_params_dict = default_agent_params.__dict__
    root_tag = etree.Element(ROOT_TAG)
    default_params_tag = etree.SubElement(root_tag, DEFAULT_AGENT_TAG)
    default_params_tag.set(DYN_MODEL_TYPE_PARAM, default_agent_params.model_name)
    for key, value in default_agent_params_dict.items():
        if type(value) is type(np.zeros(0)):
            value = value.astype(np.float64)
            default_params_tag.set(key, json.dumps(value.tolist()))
        else:
            default_params_tag.set(key, str(value))

    agents_num = len(start_states)

    agents_tag = etree.SubElement(root_tag, AGENTS_TAG)
    agents_tag.set(NUM_PARAM, str(agents_num))

    for id in range(agents_num):
        agent_tag = etree.SubElement(agents_tag, AGENT_TAG)

        agent_tag.set(ID_PARAM, str(id))

        curr_agent_type = (
            type(agents_params[id])
            if (agents_params is not None)
            else type(default_agent_params)
        )

        if issubclass(curr_agent_type, params.BaseDiscreteAgentParams):
            agent_tag.set(START_I_PARAM, str(start_states[id, 0].astype(np.int32)))
            agent_tag.set(START_J_PARAM, str(start_states[id, 1].astype(np.int32)))

            agent_tag.set(GOAL_I_PARAM, str(goal_states[id, 0].astype(np.int32)))
            agent_tag.set(GOAL_J_PARAM, str(goal_states[id, 1].astype(np.int32)))
        else:
            agent_tag.set(START_X_PARAM, str(start_states[id, 0]))
            agent_tag.set(START_Y_PARAM, str(start_states[id, 1]))
            agent_tag.set(START_THETA_PARAM, str(start_states[id, 2]))

            agent_tag.set(GOAL_X_PARAM, str(goal_states[id, 0]))
            agent_tag.set(GOAL_Y_PARAM, str(goal_states[id, 1]))
            agent_tag.set(GOAL_THETA_PARAM, str(goal_states[id, 2]))

        if agents_params is not None:
            agent_params_dict = agents_params[id].__dict__
            agent_tag.set(DYN_MODEL_TYPE_PARAM, agents_params[id].model_name)
            for key, value in agent_params_dict.items():
                if type(value) is type(np.zeros(0)):
                    value = value.astype(np.float64)
                    agent_tag.set(key, json.dumps(value.tolist()))
                else:
                    agent_tag.set(key, str(value))

    tree = etree.ElementTree(root_tag)
    file = open(path, "w")
    xml_string = etree.tostring(
        tree, pretty_print=True, xml_declaration=True, encoding="utf-8"
    ).decode()
    pretty_xml_string = "\n".join(
        [
            line
            for line in xml.dom.minidom.parseString(xml_string)
            .toprettyxml()
            .split("\n")
            if line.strip()
        ]
    )
    file.write(pretty_xml_string)
    file.close()


def create_config_file(
    path: str, alg_params: Union[BaseAlgParams, Iterable[BaseAlgParams]], exp_params: ExperimentParams
) -> None:
    """
    Creates an XML file with experiment and algorithm configurations.

    Parameters
    ----------
    path : str
        The file path where the configuration XML will be saved.
    alg_params : BaseAlgParams | Iterable[BaseAlgParams]
        Algorithms parameters for the experiment.
    exp_params : ExperimentParams
        Experiment parameters.
    """
    root_tag = etree.Element(ROOT_TAG)
    exp_params_dict = exp_params.__dict__
    exp_params_tag = etree.SubElement(root_tag, EXP_PARAM_TAG)
    for key, value in exp_params_dict.items():
        curr_exp_param_tag = etree.SubElement(exp_params_tag, key)
        if type(value) is type(np.zeros(0)):
            value = value.astype(np.float64)
            curr_exp_param_tag.text = json.dumps(value.tolist())
        else:
            curr_exp_param_tag.text = str(value)



    if issubclass(type(alg_params), BaseAlgParams):
        alg_params = [alg_params]

    for curr_params in alg_params:
        alg_params_dict = curr_params.__dict__
        alg_params_tag = etree.SubElement(root_tag, ALG_PARAM_TAG)
        alg_params_tag.set(ALG_NAME_TAG, curr_params.alg_name)
        for key, value in alg_params_dict.items():
            curr_alg_params_tag = etree.SubElement(alg_params_tag, key)
            if type(value) is type(np.zeros(0)):
                value = value.astype(np.float64)
                curr_alg_params_tag.text = json.dumps(value.tolist())
            else:
                curr_alg_params_tag.text = str(value)
            

    tree = etree.ElementTree(root_tag)
    file = open(path, "w")
    xml_string = etree.tostring(
        tree, pretty_print=True, xml_declaration=True, encoding="utf-8"
    ).decode()
    pretty_xml_string = "\n".join(
        [
            line
            for line in xml.dom.minidom.parseString(xml_string)
            .toprettyxml()
            .split("\n")
            if line.strip()
        ]
    )
    file.write(pretty_xml_string)
    file.close()


def create_log_file(path: str) -> None:
    """
    Placeholder function for creating an XML log file.

    Parameters
    ----------
    path : str
        The file path where the log XML will be saved.

    Raises
    ------
    NotImplementedError
        This function is not yet implemented.
    """
    raise NotImplementedError


def read_log_file(
    path: str, read_paths: bool = True
) -> Tuple[Tuple[int, int, int, float, int, int], Optional[npt.NDArray]]:
    """
    Reads an XML log file and extracts summary and path data if available.

    Parameters
    ----------
    path : str
        The path to the log file.
    read_paths : bool, optional
        If True, reads and returns path data. Defaults to True.

    Returns
    -------
    Tuple[Tuple[int, int, int, float, int, int], Optional[np.ndarray]]
        A summary containing (success, runtime, collisions, makespan, agent count, task ID).
        If `read_paths` is True, also returns path data as a numpy array.
    """
    tree = etree.parse(path)
    root_tag = tree.getroot()

    summary_tag = root_tag.find(SUMMARY_TAG)

    summary = [0, 0, 0, 0, 0, 0]

    success = int(summary_tag.get(SUCCESS_PARAM))
    runtime = float(summary_tag.get(RUNTIME_PARAM))
    collisions = int(summary_tag.get(COLLISIONS_PARAM))
    makespan = int(summary_tag.get(MAKESPAN_PARAM))
    agents_num = int(summary_tag.get(AGENTS_NUM_PARAM))
    task_id = int(summary_tag.get(TASK_ID_PARAM))

    summary[0] = success
    summary[1] = collisions
    summary[2] = int(makespan)
    summary[3] = runtime
    summary[4] = agents_num
    summary[5] = task_id

    if read_paths:
        steps_log = np.zeros((makespan, agents_num, 2))

        for step_tag in root_tag.findall(LOG_STEP_TAG):
            step_id = int(step_tag.get(ID_PARAM))

            for agent_tag in step_tag.findall(LOG_AGENT_TAG):
                agent_id = int(agent_tag.get(ID_PARAM))

                steps_log[step_id, agent_id, 0] = float(agent_tag.get(LOG_POS_X_PARAM))
                steps_log[step_id, agent_id, 1] = float(agent_tag.get(LOG_POS_Y_PARAM))

        return tuple(summary), steps_log
    else:
        return tuple(summary)


def read_xml_map(path: str) -> Union[Tuple[int, int, float, np.ndarray], Tuple[int, int, float, np.ndarray, List[List[npt.NDArray]]]]:
    """
    Reads an XML file containing environment data and returns map dimensions, cell size, and occupancy grid.

    Parameters
    ----------
    path : str
        The path to the map XML file.

    Returns
    -------
    Tuple[int, int, float, np.ndarray] | Tuple[int, int, float, np.ndarray, List[List[npt.NDArray]]]
        Width, height, cell size, occupancy grid, polygon obstacles (optional).
    """

    tree = etree.parse(path)
    root_tag = tree.getroot()

    occupancy_grid_tag = root_tag.find(OCCUPANCY_GRID_TAG)

    w_tag = occupancy_grid_tag.find(WIDTH_TAG)
    width = int(w_tag.text)

    h_tag = occupancy_grid_tag.find(HEIGHT_TAG)
    height = int(h_tag.text)

    cs_tag = occupancy_grid_tag.find(CELL_SIZE_TAG)
    cell_size = float(cs_tag.text)

    occupancy_grid = np.zeros(shape=(height, width), dtype=np.int32)

    grid_tag = occupancy_grid_tag.find(GRID_TAG)

    for i, row_tag in enumerate(grid_tag.findall(ROW_TAG)):
        row = row_tag.text
        occupancy_grid[i] = np.array(list(map(int, row.split())))

    obstacles = []
    obstacles_tag = root_tag.find(POLYGON_OBSTACLES_TAG)

    if obstacles_tag is None:
        return width, height, cell_size, occupancy_grid

    for obstacle_tag in obstacles_tag.findall(POLYGON_OBSTACLE_TAG):
        vertices = []
        for vertex_tag in obstacle_tag.findall(POLYGON_VERTEX_TAG):
            x = float(vertex_tag.get(VERTEX_X_PARAM))
            y = float(vertex_tag.get(VERTEX_Y_PARAM))
            vertices.append(np.array((x, y), dtype=np.float64))
        obstacles.append(vertices)

    return width, height, cell_size, occupancy_grid, obstacles


def get_agent_params_type(agent_type: str) -> Optional[type]:
    """
    Retrieves the class with parameters for a specified agent type.

    Parameters
    ----------
    agent_type : str
        The name of the agent model type.

    Returns
    -------
    Optional[type]
        The class representing the agent type, or None if not found.
    """
    subclasses = set()
    work = [params.BaseAgentParams]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child.model_name == agent_type:
                return child
            if child not in subclasses:
                subclasses.add(child)
                work.append(child)
    return None


def read_xml_agents(
    path: str,
) -> Tuple[BaseAgentParams, npt.NDArray, npt.NDArray, List[BaseAgentParams]]:
    """
    Reads an XML file defining agent configurations and extracts start states, goal states,
    and agent-specific parameters.

    Parameters
    ----------
    path : str
        The path to the agents XML file.

    Returns
    -------
    Tuple[BaseAgentParams, np.ndarray, np.ndarray, List[BaseAgentParams]]
        Default agent parameters, start states, goal states, and a list of specific agent parameters.
    """

    tree = etree.parse(path)
    root_tag = tree.getroot()

    default_agent_tag = root_tag.find(DEFAULT_AGENT_TAG)

    agent_type = default_agent_tag.get(DYN_MODEL_TYPE_PARAM)
    default_agent_params = get_agent_params_type(agent_type)()
    for key, value in default_agent_params.__dict__.items():
        field_type = type(value)
        if field_type is bool:
            default_agent_params.__dict__[key] = default_agent_tag.get(key).lower() in {
                "true",
                "1",
            }
        elif field_type is type(np.zeros(0)):
            array_str = default_agent_tag.get(key)
            default_agent_params.__dict__[key] = np.array(json.loads(array_str), dtype=np.float64)
        else:
            default_agent_params.__dict__[key] = field_type(default_agent_tag.get(key))

    agents_tag = root_tag.find(AGENTS_TAG)
    agents_num = int(agents_tag.get(NUM_PARAM))

    dim = (
        2
        if issubclass(type(default_agent_params), params.BaseDiscreteAgentParams)
        else 5
    )
    dtype = (
        np.int32
        if issubclass(type(default_agent_params), params.BaseDiscreteAgentParams)
        else np.float64
    )
    start_states = np.zeros((agents_num, dim), dtype=dtype)
    goal_states = np.zeros((agents_num, dim), dtype=dtype)

    agents_params = []

    for agent_tag in agents_tag.findall(AGENT_TAG):
        a_id = int(agent_tag.get(ID_PARAM))

        current_params = copy(default_agent_params)
        if DYN_MODEL_TYPE_PARAM in agent_tag.keys():
            new_agent_type = agent_tag.get(DYN_MODEL_TYPE_PARAM)
            if new_agent_type != agent_type:
                current_params = get_agent_params_type(new_agent_type)()

            for key, value in current_params.__dict__.items():
                field_type = type(value)
                if field_type is bool:
                    current_params.__dict__[key] = agent_tag.get(key).lower() in {
                        "true",
                        "1",
                    }
                elif field_type is type(np.zeros(0)):
                    array_str = agent_tag.get(key)
                    current_params.__dict__[key] = np.array(json.loads(array_str), dtype=np.float64)
                else:
                    current_params.__dict__[key] = field_type(agent_tag.get(key))

        if issubclass(type(current_params), params.BaseDiscreteAgentParams):
            start_states[a_id, 0] = float(agent_tag.get(START_I_PARAM))
            start_states[a_id, 1] = float(agent_tag.get(START_J_PARAM))

            goal_states[a_id, 0] = float(agent_tag.get(GOAL_I_PARAM))
            goal_states[a_id, 1] = float(agent_tag.get(GOAL_J_PARAM))
        else:
            start_states[a_id, 0] = float(agent_tag.get(START_X_PARAM))
            start_states[a_id, 1] = float(agent_tag.get(START_Y_PARAM))
            start_states[a_id, 2] = float(agent_tag.get(START_THETA_PARAM))

            goal_states[a_id, 0] = float(agent_tag.get(GOAL_X_PARAM))
            goal_states[a_id, 1] = float(agent_tag.get(GOAL_Y_PARAM))
            goal_states[a_id, 2] = float(agent_tag.get(GOAL_THETA_PARAM))

        agents_params.append(current_params)

    return default_agent_params, start_states, goal_states, agents_params


def get_alg_params_name(alg_name: str) -> Optional[type]:
    """
    Retrieves the class with parameters for a specified algorithm name.

    Parameters
    ----------
    alg_name : str
        The name of the algorithm.

    Returns
    -------
    Optional[type]
        The class with parameters for a specified algorithm name, or None if not found.
    """
    subclasses = set()
    work = [params.BaseAlgParams]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():

            if child.alg_name == alg_name:
                return child
            if child not in subclasses:
                subclasses.add(child)
                work.append(child)
    return None


def read_xml_config(path: str) -> Tuple[ExperimentParams, BaseAlgParams]:
    """
    Reads an XML file containing experiment and algorithm parameters, returning their configurations.

    Parameters
    ----------
    path : str
        The path to the configuration XML file.

    Returns
    -------
    Tuple[ExperimentParams, BaseAlgParams | List[BaseAlgParams]]
        Experiment parameters and algorithms parameters.
    """

    tree = etree.parse(path)
    root_tag = tree.getroot()

    experiment_tag = root_tag.find(EXP_PARAM_TAG)
    exp_params = params.ExperimentParams()
    for key, value in exp_params.__dict__.items():
        field_type = type(value)
        if field_type is bool:
            exp_params.__dict__[key] = experiment_tag.find(key).text.lower() in {
                "true",
                "1",
            }
        elif field_type is type(np.zeros(0)):
            array_str = experiment_tag.find(key).text
            exp_params.__dict__[key] = np.array(json.loads(array_str), dtype=np.float64)
        else:
            exp_params.__dict__[key] = field_type(experiment_tag.find(key).text)

    all_alg_params = []
    for alg_tag in root_tag.findall(ALG_PARAM_TAG):
        alg_name = alg_tag.get(ALG_NAME_TAG)
        alg_params = get_alg_params_name(alg_name)()
        for key, value in alg_params.__dict__.items():
            field_type = type(value)
            if field_type is bool:
                alg_params.__dict__[key] = alg_tag.find(key).text.lower() in {"true", "1"}
            elif field_type is type(np.zeros(0)):
                array_str = alg_tag.find(key).text
                alg_params.__dict__[key] = np.array(json.loads(array_str), dtype=np.float64)
            else:
                alg_params.__dict__[key] = field_type(alg_tag.find(key).text)
        all_alg_params.append(alg_params)

    if len(all_alg_params) == 1:
        all_alg_params = all_alg_params[0]
    return exp_params, all_alg_params
