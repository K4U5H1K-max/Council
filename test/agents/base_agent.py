class BaseAgent:
    """Base class for all agents with common attributes and placeholder methods."""

    def __init__(self, name, personality, memory_file):
        """
        Initialize a BaseAgent.

        Args:
            name (str): The agent's identifier (e.g., "rational")
            personality (str): A description of the agent's personality/role
            memory_file (str): Path to the agent's memory JSON file
        """
        self.name = name
        self.personality = personality
        self.memory_file = memory_file

    def respond(self, query, context):
        """
        Generate a response to the user's query.

        Args:
            query (str): The user's main query
            context (dict): Additional context about the user's situation

        Returns:
            str: The agent's response

        Note:
            Placeholder method. Override in subclasses.
        """
        raise NotImplementedError(f"{self.name} agent has not implemented respond()")

    def critique(self, other_response, other_agent_name):
        """
        Critique another agent's response.

        Args:
            other_response (str): The response to critique
            other_agent_name (str): The name of the agent being critiqued

        Returns:
            str: The agent's critique

        Note:
            Placeholder method. Override in subclasses.
        """
        raise NotImplementedError(f"{self.name} agent has not implemented critique()")
