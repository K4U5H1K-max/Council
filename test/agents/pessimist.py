from utils.helpers import load_json, save_json
from llm.client import call_llm
from .base_agent import BaseAgent


class PessimistAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="pessimist",
            personality="Cautious about worst-case scenarios, identifies potential pitfalls and risks",
            memory_file="memory/pessimist.json"
        )

    def respond(self, query, context):
        memory = load_json(self.memory_file)

        prompt = f"""
You are a Pessimist perspective in a "What If" scenario.

You identify potential pitfalls, worst-case scenarios, and risks in hypothetical situations. You play devil's advocate to ensure all dangers are considered.

Scenario:
- Query: {context["query"]}
- Additional Info: {context["additional_info"]}

STRICT RULES:
- Write ONLY 3–4 sentences
- No bullet points
- Be cautious and risk-aware
- Highlight potential failures and downsides
- Challenge optimistic assumptions

Your tone: cautious, skeptical, risk-focused

Respond now.
"""

        response = call_llm(prompt)

        memory["last_response"] = response
        memory["self_history"].append(response)

        save_json(self.memory_file, memory)

        return response
