"""
Agent loading and configuration module.

Provides dynamic agent selection based on interaction mode.
"""

from .rational import RationalAgent
from .ambitious import AmbitiousAgent
from .conservative import ConservativeAgent
from .emotional import EmotionalAgent
from .realist import RealistAgent
from .optimist import OptimistAgent
from .pessimist import PessimistAgent


def get_agents(mode):
    """
    Return the appropriate list of agents based on the selected mode.

    Args:
        mode (str): The interaction mode ("personal" or "whatif")

    Returns:
        list: A list of agent objects initialized for the given mode

    Raises:
        ValueError: If mode is not recognized

    Example:
        agents = get_agents("personal")
        # Returns: [RationalAgent(), AmbitiousAgent(), ConservativeAgent(), EmotionalAgent()]

        agents = get_agents("whatif")
        # Returns: [RealistAgent(), AmbitiousAgent(), OptimistAgent(), PessimistAgent()]
    """
    if mode == "personal":
        return [
            RationalAgent(),
            AmbitiousAgent(),
            ConservativeAgent(),
            EmotionalAgent()
        ]
    elif mode == "whatif":
        return [
            RealistAgent(),
            AmbitiousAgent(),
            OptimistAgent(),
            PessimistAgent()
        ]
    else:
        raise ValueError(f"Unknown mode: {mode}. Must be 'personal' or 'whatif'.")
