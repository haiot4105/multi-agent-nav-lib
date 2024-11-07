# Multi-agent Navigation Library

This repository provides a collection of utility functions and scripts to conduct a multi-agent navigation experiments. It includes tools for generating, reading, and writing XML files to configure experiments, simplifying experiment setup and data handling.

## Installation

Before start using this project you need to install the required dependencies:

1. `Python 3.11`
2. `pip`
3. `numpy`
4. `lxml`
3. `IPython` and `Jupyter Notebook` (for running Jupyter notebooks)

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

Examples of XML files are located in the xml-examples folder. You can find usage examples for the manavlib.common.params and manavlib.io.xml_io modules in the Jupyter Notebook test/xml_io_test.ipynb.

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
