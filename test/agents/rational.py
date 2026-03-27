from utils.helpers import load_json, save_json
from llm.client import call_llm
from .base_agent import BaseAgent


class RationalAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="rational",
            personality="Logical, balanced, focused on long-term outcomes and realistic decision-making",
            memory_file="memory/rational.json"
        )

    def respond(self, query, context):
        memory = load_json(self.memory_file)

        prompt = f"""
You are a Rational thinker.

You prioritize logic, long-term outcomes, and realistic decision-making.

User Context:
- Query: {context["query"]}
- Additional Info: {context["additional_info"]}

STRICT RULES:
- Write ONLY 3–4 sentences (no bullet points)
- Be concise but thoughtful
- Speak like a human giving advice, not a list
- Focus on cause-effect reasoning
- Do NOT agree blindly with emotional or risky choices

Your tone: calm, analytical, grounded

Respond now.
"""

        response = call_llm(prompt)

        memory["last_response"] = response
        memory["self_history"].append(response)

        save_json(self.memory_file, memory)

        return response