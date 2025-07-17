# Multi-agent Navigation Library

This repository provides a collection of utility functions and scripts to conduct a multi-agent navigation experiments. It includes tools for generating, reading, and writing XML files to configure experiments, simplifying experiment setup and data handling.

## Installation

Before start using this project you need to install the required dependencies:

1. `Python 3.10`
2. `pip`
3. `setuptools`
4. `numpy`
5. `lxml`
6. `IPython` and `Jupyter Notebook` (for running Jupyter notebooks)

Next, you need to run this script from the root folder of this project to install it across all system:

```bash
pip install .
```

To include support for running Jupyter notebooks, use:
```bash
pip install '.[notebooks]'
```

## Overview of `manavlib`

* `manavlib.common.params`: a set of classes for conveniently storing, reading and passing parameters in multi-agent navigation experiments.
* `manavlib.common.transform`: functions for converting between cartesian (x, y) coordinates and grid indices (i, j).
* `manavlib.gen.maps`: functions to create grid maps with custom layouts.
* `manavlib.gen.tasks`: functions for generating tasks with various patterns of agents' start and goal positions.
* `manavlib.gen.polygon`: functions and classes for detecting and representing obstacle boundaries (contours) in a grid.
* `manavlib.io.xml_io`: functions to create, read, and manage XML files for multi-agent navigation
experiments.
* `manavlib.io.movingai_io`: functions for reading and writing map files in the MovingAI format.
* `manavlib.io.tswap_io`: functions to support the setup, conversion, and processing of multi-agent pathfinding experiments to evaluate the TSWAP algorithm.
* `manavlib.utils`: various auxiliary tools. Сurrently include functions for finding paths on grids.


## Example Usage

The Jupyter Notebook [`test/main_features_test.ipynb`](test/main_features_test.ipynb) demonstrates how to:

- Work with XML-based task and environment descriptions.
- Define and parse custom agent, algorithm and experiment types.
- Use configuration files with custom agent, algorithm and experiment parameters.

## XML File Structure

One of the key components of this repository is a module `manavlib.io.xml_io` that allows to read experiment configurations from XML files of a special structure.  It is assumed that each experiment is described by three types of files: an environment file `map.xml`, an agents/task description file `task.xml`, and an experiment/algorithm configuration file `config.xml`.


Examples of XML files are located in the `xml-examples` folder. For details, see the [example notebook](test/main_features_test.ipynb).


### Environment Description (`map.xml`)

The file includes a description of the environment, namely an obstacle map. Currently only static map description in grid format is supported.

#### Structure

0. **Root Element `<root>`**: The entire content of the XML file is wrapped inside the `<root>` element.
1. **Occupancy Grid Element `<occupancy_grid>`**: Defines the grid map structure and its properties. It contains metadata about the grid, such as its dimensions and cell size, as well as the grid layout itself.
    * **Width Element `<width>`**: Specifies the width of the grid map in the number of cells (columns).
    * **Height Element `<height>`**: Specifies the height of the grid map in the number of cells (rows).
    * **Cell Size Element `<cell_size>`**: Defines the size of each cell in the grid. This value is used for scaling and pathfinding calculations.
    * **Grid Element `<grid>`**: Contains the layout of the map, represented as a matrix of cells.
      * **Row Elements `<row>`**: Each `<row>` element represents a single row of the grid. The values within each row indicate the state of the corresponding cell: `0` represents a free cell (traversable), `1` represents an obstacle (non-traversable).
2. **Polygon Element `<polygon_obstacles>`**: Optional section providing an explicit geometric representation of obstacles using polygons. Useful for continuous motion planning.
    * **Obstacle Elements `<obstacle>`**: Represents a single polygonal obstacle. The obstacle is defined as a closed polygon via its ordered list of vertices.
      * **Vertex Elements <vertex>**: Each vertex defines a point in 2D space using attributes:
        * **`v.x`**: X coordinate of the vertex (float)
        * **`v.y`**: Y coordinate of the vertex (float).

  > [!IMPORTANT]
  > Vertices must be listed in **counter-clockwise** order for regular obstacles. For polygons representing outer boundaries or enclosing voids (e.g., inner contour of boundary walls), vertices must be listed in **clockwise** order. The last vertex is implicitly connected to the first to form a closed polygon.

#### Example

```xml
<?xml version="1.0" ?>
<root>
	<occupancy_grid>
		<width>10</width>
		<height>10</height>
		<cell_size>1.0</cell_size>
		<grid>
			<row>0 0 0 0 0 0 0 0 0 0</row>
			<row>0 0 0 0 0 0 0 0 0 0</row>
			<row>0 0 1 1 1 1 0 0 0 0</row>
			<row>0 0 0 0 0 0 0 0 0 0</row>
			<row>0 0 0 0 0 0 0 0 0 0</row>
			<row>0 0 0 0 0 0 0 0 0 0</row>
			<row>0 0 0 0 0 0 0 0 0 0</row>
			<row>0 0 0 0 0 0 0 0 0 0</row>
			<row>0 0 0 0 0 0 0 0 0 0</row>
			<row>0 0 0 0 0 0 0 0 0 0</row>
		</grid>
	</occupancy_grid>
	<polygon_obstacles>
		<obstacle>
			<vertex v.x="2.0" v.y="8.0"/>
			<vertex v.x="2.0" v.y="7.0"/>
			<vertex v.x="6.0" v.y="7.0"/>
			<vertex v.x="6.0" v.y="8.0"/>
		</obstacle>
		<obstacle>
			<vertex v.x="0.0" v.y="0.0"/>
			<vertex v.x="0.0" v.y="10.0"/>
			<vertex v.x="10.0" v.y="10.0"/>
			<vertex v.x="10.0" v.y="0.0"/>
		</obstacle>
	</polygon_obstacles>
</root>
```
In this example:
* The `<occupancy_grid>` section defines a $10 \times 10$ grid where obstacle cells (with value 1) form a horizontal block spanning columns 2 to 5 in row 2 (zero-indexed). 
* The first polygon in `<polygon_obstacles>` defines a rectangular solid obstacle using counter-clockwise vertex ordering. It corresponds to the same obstacle as in the grid: from (2.0, 7.0) to (6.0, 8.0) in world coordinates (assuming origin at bottom-left and Y increasing upward).
* The second polygon defines the outer boundary of the map using clockwise vertex ordering. It forms a rectangle from (0.0, 0.0) to (10.0, 10.0), enclosing the full environment and indicating the limits of navigable space.

Additional examples of map descriptions can be found in the [`xml-examples`](xml-examples/) folder.


### Task description (`task.xml`)

The file includes a task description, namely default agent configurations, initial and goal agent positions (there are two possible options to set positions: discrete and continuous) and (optionally) the configuration of each particular agent. This file defines parameters of agents such as type, size, visibility radius, and motion parameters.

The possible agent types are defined in module `manavlib.common.params`. You can define your own agent type by creating a class in your workspace that inherits from `BaseAgentParams`.

For details, see the [example notebook](test/main_features_test.ipynb).

#### Structure

0. **Root Element `<root>`**: The entire content of the XML file is wrapped inside the `<root>` element.
1. **Default Agent Element `<default_agent>`**: Specifies the default parameters that apply to all agents unless explicitly overridden for a particular agent. In general, the particular set of attributes is specified by the agent type, but each agent type basycally includes the following attributes:
    * **`model_type` (mandatory)**: The type of agent model, e.g., `diff_drive`, `holonomic`, or `base_discrete`.
    * **`size`**: The size (radius) of the agent.
    * **`r_vis`**: Visibility radius of the agent, used for determining the communication range.
    * The agent configuration can include custom parameters. The following data types are supported: `str`, `int`, `float`, `bool`, `ndarray`.
2. **Agents Element: `<agents>`**: Contains the list of individual agents, where `N` is the total number of agents specified by the `number` attribute.
    * **Agent Elements: `<agent>`**: Defines an individual agent. The attributes of the element can include:
      * **Identifier `id` (mandatory)**: A unique identifier for the agent.
      * **Initial State (`s.` prefix, mandatory)**:
        * **`s.x, s.y, s.th`**: The initial `x` and `y` coordinates and orientation in radians `theta` (for continuous models).
        * **`s.i, s.j`**: The initial row (`i`) and column (`j`) indices (for discrete models).
      * **Goal State (`g.` prefix, mandatory)**:
        * **`g.x, g.y, g.th`**: The initial `x` and `y` coordinates and orientation in radians `theta` (for continuous models).
        * **`g.i, g.j`**: The initial row (`i`) and column (`j`) indices (for discrete models).
      * **Model-Specific Parameters**: These can override the default agent parameters defined in <default_agent>, such as `model_type`, `size`, `r_vis`, etc. The following data types are supported: `str`, `int`, `float`, `bool`, `ndarray`.

#### Example (Continuous)

```xml
<?xml version="1.0" ?>
<root>
	<default_agent model_type="unc_diff_drive" size="0.3" r_vis="30.0" v_max="1.0" v_min="-1.0" w_max="2.0" w_min="-2.0" control_noise_std="[[1.0, 0.0], [0.0, 1.0]]"/>
	<agents number="2">
		<agent id="0" s.x="9.5" s.y="3.5" s.th="6.196061607632843" g.x="5.5" g.y="7.5" g.th="2.5873340299187277"/>
		<agent id="1" s.x="6.5" s.y="5.5" s.th="5.989807426336923" g.x="5.5" g.y="4.5" g.th="0.32535540553561915"/>
	</agents>
</root>
```

This example defines two agents operating in a continuous environment. The `<default_agent>` element specifies a model of type `unc_diff_drive` (uncertain differential drive) with motion constraints (velocity and angular velocity limits) and control noise defined by a $2 \times 2$ covariance matrix.

Each agent is defined by:

* A unique `id`.
* Initial state: `s.x`, `s.y`, `s.th` — position and orientation in radians.
* Goal state: `g.x`, `g.y`, `g.th` — position and orientation in radians.

All agents share the same type and parameters values, inherited from the `<default_agent>` definition.

#### Example (Discrete)

```xml
<?xml version="1.0" ?>
<root>
 <default_agent model_type="base_discrete" size="1.0" r_vis="30.0"/>
 <agents number="3">
  <agent id="0" s.i="0" s.j="5" g.i="3" g.j="9"/>
  <agent id="1" s.i="5" s.j="4" g.i="0" g.j="2"/>
  <agent id="2" s.i="2" s.j="4" g.i="4" g.j="7"/>
 </agents>
</root>
```

This example defines three agents using a discrete model (`base_discrete`), meaning their states are represented as grid coordinates.

Each agent is defined by:

* A unique `id`.
* Initial position: `s.i`, `s.j` — row and column indices.
* Goal position: `g.i`, `g.j` — row and column indices.

All agents share the same type and parameters values, inherited from the `<default_agent>` definition.

Additional examples of task definitions can be found in the [`xml-examples`](xml-examples/) folder.



### Experiment configuration (`config.xml`)

This file defines the configuration for the experiment and the algorithm used in multi-agent pathfinding tasks. It specifies both general experiment settings and the parameters of the algorithm to be applied to all agents in the experiment. Currently, only the configuration of single algorithm is supported.

The base algorithm's parameters class is defined in module `manavlib.common.params`. You need to define your own algorithm's parameters class that inherits from `BaseAlgParams`.

The class with the experiment parameters `ExperimentParams` is also defined in module `manavlib.common.params`. If it is necessary to add custom parameters of the experiment, you need to define your own class, which will globally overwrite the name `ExperimentParams`.

For details, see the [example notebook](test/main_features_test.ipynb).

#### Structure

0. **Root Element `<root>`**: The entire content of the XML file is wrapped inside the `<root>` element.
1. **Experiment Element `<experiment>`**: Contains general settings for the experiment. It includes parameters that control the overall behavior of the simulation
    * **`timestep`**: Defines the duration of each discrete time step in the experiment.
    * **`xy_goal_tolerance`**: Defines the tolerance for reaching the goal position. Agents are considered to have reached their goal if they are within this distance
    * **`max_steps`**: The maximum number of time steps allowed for the experiment. If this limit is reached, the simulation terminates even if not all agents have reached their goals.
    * The experiment configuration can include custom parameters. The following data types are supported: `str`, `int`, `float`, `bool`, `ndarray`.
2. **Algorithm Elements `<algorithm>`**: Specifies the configuration for the algorithm to be applied to all agents in the experiment. The `name` attribute defines the algorithm’s name (e.g., "example_alg"), which should match the implemented algorithm class in the code. One or more <algorithm> elements can be defined. Each one specifies a set of parameters for a given algorithm:
    * The parameters listed under the `<algorithm>` element are specific to the selected algorithm and are used to control its behavior during the simulation. The following data types are supported: `str`, `int`, `float`, `bool`, `ndarray`.

#### Example

```xml
 <experiment>
  <timestep>0.1</timestep>
  <xy_goal_tolerance>0.3</xy_goal_tolerance>
  <max_steps>100</max_steps>
  <custom_param>42</some_param1>
 </experiment>
	<algorithm name="example_alg">
		<a_param>17</a_param>
		<b_param>43.0</b_param>
		<c_param>False</c_param>
		<d_param>abc</d_param>
		<array_param>[1.0, 2.0, 3.0, 4.0]</array_param>
		<matrix_param>[[-1.0, -1.0, -1.0], [-1.0, -1.0, -1.0]]</matrix_param>
	</algorithm>
	<algorithm name="example_alg2">
		<a_param>25</a_param>
		<b_param>26.0</b_param>
		<c_param>False</c_param>
		<d_param>abc</d_param>
	</algorithm>
```

In this example:

* The `<experiment>` element defines general parameters for the simulation:
  * The `timestep` is set to `0.1`.
  * Agents are considered to have reached their goals if they are within `0.3` units of the goal position.
  * The simulation is limited to `100 steps`.
  * A custom parameter `custom_param` is also included as an integer value (`42`).
* Two algorithms are defined:
  * `example_alg` includes various parameter types:
    * Integer (`a_param`), float (`b_param`), boolean (`c_param`), string (`d_param`), 
    * 1D array (`array_param`), and 2D array (`matrix_param`).
  * `example_alg2` includes a simpler set of parameters (integer, float, boolean, string).


Additional examples of experiment configurations can be found in the [`xml-examples`](xml-examples/) folder.


## Scripts

### Running of the TSWAP Algorithm

> [!IMPORTANT]
>
> **Before running the experiment you need to download and build the TSWAP implementation **[[GitHub](https://github.com/Kei18/tswap)]**. You also need to create XML files with input tasks and maps.**

The repository includes a setup for executing the TSWAP algorithm. To run TSWAP experiments, follow these steps:

1. Open the Jupyter Notebook `scripts/run-tswap-experiments/run_experiments.ipynb`
2. **Specify the variables with information about TSWAP folder location and location of maps and task files.**
3. Configure experiment parameters. Specify the parameters for your TSWAP experiment, such as the number of agents and number of tasks.
4. Run the experiment and get the results. Results are saved in text files. Each result file will contain data like:

```txt
number         collision       collision_obst  flowtime       makespan       runtime        success       sum_of_dists   max_dist
5              0               0               1200           150            2.50           100           1500.0         300.0
```

#### Configuration example

Suppose you cloned the TSWAP repository at `/some/path/tswap/` and created the folder `/some/path/tswap/build_folder/`, where you then built the project according to the TSWAP repository instructions. The `app` binary file should appear in `/some/path/tswap/build_folder/`.

Next, you created 10 XML task files for the grid map `some_map1` and 10 XML task files for `some_map2`. Store them in `/other/path/tasks/`, placing task files for `some_map1` in `/other/path/tasks/some_map1/` and those for `some_map2` in `/other/path/tasks/some_map2/`.

Name task files following this pattern:

```txt
0_task.xml, 
1_task.xml, 
..., 
n_task.xml
```

Each folder should also contain a file named `map.xml` with map data.

Create a folder `/other/path/results/` to store experiment results.

After setting up these folders, open and modify `scripts/run-tswap-experiments/run_experiments.ipynb` as follows:

```python
TSWAP_DIR = "/some/path/tswap" 
TSWAP_BUILD_DIR = "build_folder"  
XML_TASKS_DIR = "/other/path/tasks"  
MAPS_NAMES = [
    "some_map1",
    "some_map2",
] 
EXPERIMENT_RESULTS_DIR = "/other/path/results" 
```

Examples of input and output files can be found in the `scripts/run-tswap-experiments/tasks` and `scripts/run-tswap-experiments/results` folders respectively.
