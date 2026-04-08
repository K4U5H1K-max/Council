"""Agent loading for the Battle of the Bots workflow."""

from .debate_agent import DebateAgent


def get_agents(mode="debate"):
    """Return the three role-based agents used in the debate pipeline."""
    if mode not in ("debate", "personal", "whatif"):
        raise ValueError(f"Unknown mode: {mode}. Must be 'debate', 'personal', or 'whatif'.")

    return [
        DebateAgent(name="pro", role="PRO"),
        DebateAgent(name="con", role="CON"),
        DebateAgent(name="evaluator", role="EVALUATOR"),
    ]
