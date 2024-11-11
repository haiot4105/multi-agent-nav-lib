# Multi-agent Navigation Library

This repository provides a collection of utility functions and scripts to conduct a multi-agent navigation experiments. It includes tools for generating, reading, and writing XML files to configure experiments, simplifying experiment setup and data handling.

## Installation

Before start using this project you need to install the required dependencies:

1. `Python 3.11`
2. `pip`
3. `setuptools`
4. `numpy`
5. `lxml`
6. `IPython` and `Jupyter Notebook` (for running Jupyter notebooks)

Next, you need to run this script from the root folder of this project to install it across all system:

```bash
pip install -e .
```

## Overview of `manavlib`

* `manavlib.common.params`: a set of classes for conveniently storing, reading and passing parameters in multi-agent navigation experiments.
* `manavlib.io.xml_io`: functions to create, read, and manage XML files for multi-agent navigation
experiments.
* `manavlib.gen.maps`: functions to create maps with custom layouts.
* `manavlib.gen.tasks`: functions for generating tasks with various patterns of agents' start and goal positions.
* `manavlib.io.movingai_io`: functions for reading and writing map files in the MovingAI format.
* `manavlib.io.tswap_io`: functions to support the setup, conversion, and processing of multi-agent pathfinding experiments to evaluate the TSWAP algorithm.
* `manavlib.utils`: various auxiliary tools. Сurrently include functions for finding paths on grids.

You can find usage examples for the `manavlib.common.params` and `manavlib.io.xml_io` modules in the Jupyter Notebook `test/xml_io_test.ipynb`.

## XML File Structure

One of the key components of this repository is a module `manavlib.io.xml_io` that allows to read experiment configurations from XML files of a special structure.  It is assumed that each experiment is described by three types of files: an environment file `map.xml`, an agents/task description file `task.xml`, and an experiment/algorithm configuration file `config.xml`.

Examples of XML files are located in the `xml-examples` folder. An usage examples for `manavlib.io.xml_io` module (with custom agent, algorithm and experiment parameters) is located in the Jupyter Notebook `test/xml_io_test.ipynb`.

### Environment Description `map.xml`

The file includes a description of the environment, namely an obstacle map. Currently only static map description in grid format is supported.

#### Structure

* **Root Element `<root>`**: The entire content of the XML file is wrapped inside the `<root>` element.
* **Occupancy Grid Element `<occupancy_grid>`**: Defines the grid map structure and its properties. It contains metadata about the grid, such as its dimensions and cell size, as well as the grid layout itself.
  * **Width Element `<width>`**: Specifies the width of the grid map in the number of cells (columns).
  * **Height Element `<height>`**: Specifies the height of the grid map in the number of cells (rows).
  * **Cell Size Element `<cell_size>`**: Defines the size of each cell in the grid. This value is used for scaling and pathfinding calculations.
  * **Grid Element `<grid>`**: Contains the layout of the map, represented as a matrix of cells.
    * **Row Elements `<row>`**: Each `<row>` element represents a single row of the grid. The values within each row indicate the state of the corresponding cell: `0` represents a free cell (traversable), `1` represents an obstacle (non-traversable).

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
</root>
```

### Task description `task.xml`

The file includes a task description, namely default agent configurations, initial and goal agent positions (there are two possible options to set positions: discrete and continuous) and (optionally) the configuration of each particular agent. This file defines parameters of agents such as the agent’s type, size, visibility radius, and motion parameters.

The possible agent types are defined in module `manavlib.common.params`. You can define your own agent type by creating a class in your workspace that inherits from `BaseAgentParams`.

An example of creating and reading of task file with custom agents is located in the Jupyter Notebook `test/xml_io_test.ipynb`.

#### Structure

* **Root Element `<root>`**: The entire content of the XML file is wrapped inside the `<root>` element.
* **Default Agent Element `<default_agent>`**: Specifies the default parameters that apply to all agents unless explicitly overridden for a particular agent. In general, the particular set of attributes is specified by the agent type, but each agent type basycally includes the following attributes:
  * **`model_type` (mandatory)**: The type of agent model, e.g., `diff_drive`, `holonomic`, or `base_discrete`.
  * **`size`**: The size (radius) of the agent.
  * **`r_vis`**: Visibility radius of the agent, used for determining the communication range.
  * The agent configuration can include custom parameters. The following data types are supported: `str`, `int`, `float`, `bool`.
* **Agents Element: `<agents>`**: Contains the list of individual agents, where `N` is the total number of agents specified by the `number` attribute.
  * **Agent Elements: `<agent>`**: Defines an individual agent. The attributes of the element can include:
    * **`id` (mandatory)**: An unique identifier for the agent.
    * **Initial State (`s.` prefix, mandatory)**:
      * **`s.x, s.y, s.th`**: The initial `x` and `y` coordinates and orientation in radians `theta` (for continuous models).
      * **`s.i, s.j`**: The initial row (`i`) and column (`j`) indices (for discrete models).
    * **Goal State (`g.` prefix, mandatory)**:
      * **`g.x, g.y, g.th`**: The initial `x` and `y` coordinates and orientation in radians `theta` (for continuous models).
      * **`g.i, g.j`**: The initial row (`i`) and column (`j`) indices (for discrete models).
    * **Model-Specific Parameters**: These can override the default agent parameters defined in <default_agent>, such as `model_type`, `size`, `r_vis`, etc. The following data types are supported: `str`, `int`, `float`, `bool`.

#### Example (Continuous)

```xml
<?xml version="1.0" ?>
<root>
 <default_agent model_type="diff_drive" size="68.0" r_vis="57.0" v_max="68.0" v_min="64.0" w_max="36.0" w_min="54.0"/>
 <agents number="2">
  <agent id="0" s.x="75.5" s.y="96.5" s.th="3.378" g.x="10.5" g.y="11.5" g.th="2.995" model_type="diff_drive" size="68.0" r_vis="57.0" v_max="68.0" v_min="64.0" w_max="36.0" w_min="54.0"/>
  <agent id="1" s.x="24.5" s.y="41.5" s.th="3.009" g.x="2.5" g.y="43.5" g.th="3.293" model_type="holonomic" size="7.0" r_vis="9.0" vel_max="47.0"/>
 </agents>
</root>
```

#### Example (Discrete)

```xml
<?xml version="1.0" ?>
<root>
 <default_agent model_type="base_discrete" size="57.0" r_vis="64"/>
 <agents number="3">
  <agent id="0" s.i="0" s.j="5" g.i="3" g.j="9"/>
  <agent id="1" s.i="5" s.j="4" g.i="0" g.j="2"/>
  <agent id="2" s.i="2" s.j="4" g.i="4" g.j="7"/>
 </agents>
</root>
```

### Experiment configuration `config.xml`

This file defines the configuration for the experiment and the algorithm used in multi-agent pathfinding tasks. It specifies both general experiment settings and the parameters of the algorithm to be applied to all agents in the experiment. Currently, only the configuration of single algorithm is supported.

The base algorithm's parameters class is defined in module `manavlib.common.params`. You need to define your own algorithm's parameters class that inherits from `BaseAlgParams`.

The class with the experiment parameters `ExperimentParams` is also defined in module `manavlib.common.params`. If it is necessary to add custom parameters of the experiment, you need to define your own class, which will globally overwrite the name `ExperimentParams`.

An example of creating and reading of config file with custom agents is located in the Jupyter Notebook `test/xml_io_test.ipynb`.

#### Structure

* **Root Element `<root>`**: The entire content of the XML file is wrapped inside the `<root>` element.
* **Experiment Element `<experiment>`**: Contains general settings for the experiment. It includes parameters that control the overall behavior of the simulation
  * **`timestep`**: Defines the duration of each discrete time step in the experiment.
  * **`xy_goal_tolerance`**: Defines the tolerance for reaching the goal position. Agents are considered to have reached their goal if they are within this distance
  * **`max_steps`**: The maximum number of time steps allowed for the experiment. If this limit is reached, the simulation terminates even if not all agents have reached their goals.
  * The experiment configuration can include custom parameters. The following data types are supported: `str`, `int`, `float`, `bool`.
* **Algorithm Element `<algorithm>`**: Specifies the configuration for the algorithm to be applied to all agents in the experiment. The `name` attribute defines the algorithm’s name (e.g., "example_alg"), which should match the implemented algorithm class in the code. Only one `<algorithm>` element is currently supported per configuration file, and its settings are applied uniformly to all agents.
  * The parameters listed under the `<algorithm>` element are specific to the selected algorithm and are used to control its behavior during the simulation. The following data types are supported: `str`, `int`, `float`, `bool`.

#### Example

```xml
<?xml version="1.0" ?>
<root>
 <experiment>
  <timestep>0.1</timestep>
  <xy_goal_tolerance>0.3</xy_goal_tolerance>
  <max_steps>100</max_steps>
  <custom_param>42</some_param1>
 </experiment>
 <algorithm name="example_alg">
  <a_param>85</a_param>
  <b_param>89.0</b_param>
  <c_param>False</c_param>
  <d_param>direct</d_param>
 </algorithm>
</root>
```

## Scripts

### Running of the TSWAP Algorithm

> [!Important]
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
