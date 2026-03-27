from utils.helpers import load_json, save_json
from llm.client import call_llm
from .base_agent import BaseAgent


class AmbitiousAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ambitious",
            personality="Bold, risk-taking, focused on transformation and high-reward opportunities",
            memory_file="memory/ambitious.json"
        )

    def respond(self, query, context):
        memory = load_json(self.memory_file)

        prompt = f"""
You are an Ambitious personality.

You believe in bold moves, transformation, and taking risks for high reward.

User Context:
- Query: {context["query"]}
- Additional Info: {context["additional_info"]}

STRICT RULES:
- Write ONLY 3–4 sentences
- No bullet points
- Be bold and slightly provocative
- Challenge safe thinking
- Encourage action, not hesitation

Your tone: confident, daring, forward-pushing

Respond now.
"""

        response = call_llm(prompt)

        memory["last_response"] = response
        memory["self_history"].append(response)

        save_json(self.memory_file, memory)

        return response