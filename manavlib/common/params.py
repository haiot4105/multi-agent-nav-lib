"""
This module defines classes that encapsulate parameter configurations for agents,
experiments, and algorithms in multi-agent navigation scenarios. The classes
provide a structured way to set up and manage properties relevant to different
types of agents (e.g., holonomic, differential-drive) and experimental setups.

Classes
-------
BaseAgentParams : A base class for agents' configurations, defines a basic parameters for an agent. May be 
HolonomicAgentParams : Defines parameters specific to a holonomic agent.
DiffDriveAgentParams : Defines parameters specific to a differential-drive agent.
BaseDiscreteAgentParams : Defines parameters for a basic agent in grid-based environments.
ExperimentParams : Defines parameters for experiment configuration.
BaseAlgParams : A base class for a navigation algorithm' configurations.

Usage
-----
Each class can be instantiated and used to define specific parameters for
agents, experiments, and algorithms. These classes can be extended or modified
to support additional parameter configurations as needed.

Example
-------
# Creating and displaying parameters for a holonomic agent
holonomic_params = HolonomicAgentParams()
holonomic_params.vel_max = 1.5
print(holonomic_params)
"""

class BaseAgentParams:
    """
    Base class for an agent parameters in multi-agent navigation experiments.
    
    The class is necessary for convenient organisation of reading and writing 
    agent configurations to files and for launching experiments. 
    
    It should be inherited when defining a new agent type! 
    
    When adding a new attribute for new agent type, it should 
    be created inside the __init__ method and initialised with 
    a value of the corresponding type.
   
    For example, a default value of 0.0 can be used for an attribute of 
    type float, a value of 0 for an attribute of type int, etc.

    Attributes
    ----------
    model_name : str
        The name of the agent model. 
        Should be modified in corresponding inheritor class when defining a new agent type.
    size : float
        The physical size (radius) of the agent modeled as an open disk.
    r_vis : float
        The visibility radius of the agent.
    """
    model_name = "base"

    def __init__(self):
        """
        Initializes BaseAgentParams with default size and visibility radius.
        """
        self.size = 0.0
        self.r_vis = 0.0

    def __str__(self) -> str:
        """
        Returns a string representation of the agent parameters.

        Returns
        -------
        str
            A string with the model name and parameter values.
        """
        return self.model_name + ": " + str(self.__dict__)
    
    def __repr__(self) -> str:
        """
        Returns a representation of the agent parameters.

        Returns
        -------
        str
            A string with the model name and parameter values.
        """
        return self.model_name + ": " + str(self.__dict__)


class HolonomicAgentParams(BaseAgentParams):
    """
    Parameters for a holonomic agent, a type of agent with unrestricted movement.

    Attributes
    ----------
    vel_max : float
        The maximum velocity of the holonomic agent.
    """
    model_name = "holonomic"

    def __init__(self) -> None:
        """
        Initializes HolonomicAgentParams with default maximum velocity.
        """
        super().__init__()
        self.vel_max = 0.0


class DiffDriveAgentParams(BaseAgentParams):
    """
    Parameters for an agent with differential-drive movement constraints.

    Attributes
    ----------
    v_max : float
        The maximum linear velocity of the agent.
    v_min : float
        The minimum linear velocity of the agent.
    w_max : float
        The maximum angular velocity of the agent.
    w_min : float
        The minimum angular velocity of the agent.
    """
    model_name = "diff_drive"

    def __init__(self) -> None:
        """
        Initializes DiffDriveAgentParams with default velocity constraints.
        """
        super().__init__()
        self.v_max = 0.0
        self.v_min = 0.0
        self.w_max = 0.0
        self.w_min = 0.0


class BaseDiscreteAgentParams(BaseAgentParams):
    """
    Parameters for a base agent in a grid-based environment.

    Attributes
    ----------
    r_vis : int
        The visibility radius of the agent, as an integer.
    """
    model_name = "base_discrete"

    def __init__(self):
        """
        Initializes BaseDiscreteAgentParams with default visibility radius.
        """
        super().__init__()
        self.r_vis = 0

    def __str__(self) -> str:
        """
        Returns a string representation of the discrete agent parameters.

        Returns
        -------
        str
            A string with the model name and parameter values.
        """
        return self.model_name + ": " + str(self.__dict__)

    def __repr__(self) -> str:
        """
        Returns a representation of the discrete agent parameters.

        Returns
        -------
        str
            A string with the model name and parameter values.
        """
        return self.model_name + ": " + str(self.__dict__)


class ExperimentParams:
    """
    Parameters for an experiment setup in multi-agent navigation.

    Attributes
    ----------
    timestep : float
        The time duration of each step in the experiment.
    xy_goal_tolerance : float
        The position tolerance for reaching the goal.
    max_steps : int
        The maximum number of steps in the experiment.
    """

    def __init__(self) -> None:
        """
        Initializes ExperimentParams with default timestep, goal tolerance, and max steps.
        """
        self.timestep = 0.0
        self.xy_goal_tolerance = 0.0
        self.max_steps = 0

    def __str__(self) -> str:
        """
        Returns a string representation of the experiment parameters.

        Returns
        -------
        str
            A string with the experiment parameter values.
        """
        return str(self.__dict__)
    
    def __repr__(self) -> str:
        """
        Returns a representation of the experiment parameters.

        Returns
        -------
        str
            A string with the experiment parameter values.
        """
        return str(self.__dict__)


class BaseAlgParams:
    """
    Base class for an algorithm parameters in multi-agent navigation experiments.
    
    The class is necessary for convenient organisation of reading and writing 
    algorithm configurations to files and for launching experiments. 
    
    It should be inherited when defining a new algorithm type! 
    
    When adding a new attribute for new algorithm type, it should 
    be created inside the __init__ method and initialised with 
    a value of the corresponding type.
   
    For example, a default value of 0.0 can be used for an attribute of 
    type float, a value of 0 for an attribute of type int, etc.

    Attributes
    ----------
    alg_name : str
        The name of the algorithm.
        Should be modified in corresponding inheritor class when defining a new algorithm type.
    """
    alg_name = "base"

    def __init__(self):
        """
        Initializes BaseAlgParams.
        """
        pass

    def __str__(self) -> str:
        """
        Returns a string representation of the algorithm parameters.

        Returns
        -------
        str
            A string with the algorithm name and parameter values.
        """
        return self.alg_name + ": " + str(self.__dict__)
    
    def __repr__(self) -> str:
        """
        Returns a representation of the algorithm parameters.

        Returns
        -------
        str
            A string with the algorithm name and parameter values.
        """
        return self.alg_name + ": " + str(self.__dict__)