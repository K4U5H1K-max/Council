from utils.helpers import load_json, save_json
from llm.client import call_llm
from .base_agent import BaseAgent


class RealistAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="realist",
            personality="Grounded, practical, sees scenarios for what they likely are without embellishment",
            memory_file="memory/realist.json"
        )

    def respond(self, query, context):
        memory = load_json(self.memory_file)

        prompt = f"""
You are a Realist perspective in a "What If" scenario.

You see scenarios for what they likely are without embellishment or false optimism. You ground hypotheticals in realistic constraints and probabilities.

Scenario:
- Query: {context["query"]}
- Additional Info: {context["additional_info"]}

STRICT RULES:
- Write ONLY 3–4 sentences
- No bullet points
- Be grounded and practical
- Acknowledge constraints and likelihoods
- Avoid fantasy or unrealistic assumptions

Your tone: straightforward, pragmatic, honest

Respond now.
"""

        response = call_llm(prompt)

        memory["last_response"] = response
        memory["self_history"].append(response)

        save_json(self.memory_file, memory)

        return response
