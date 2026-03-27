from utils.helpers import load_json, save_json
from llm.client import call_llm
from .base_agent import BaseAgent


class OptimistAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="optimist",
            personality="Hopeful, sees potential and positive possibilities in scenarios",
            memory_file="memory/optimist.json"
        )

    def respond(self, query, context):
        memory = load_json(self.memory_file)

        prompt = f"""
You are an Optimist perspective in a "What If" scenario.

You see the potential and positive possibilities in hypothetical situations. You explore best-case outcomes and constructive pathways.

Scenario:
- Query: {context["query"]}
- Additional Info: {context["additional_info"]}

STRICT RULES:
- Write ONLY 3–4 sentences
- No bullet points
- Be hopeful and possibilities-focused
- Highlight positive potential
- Explore constructive outcomes

Your tone: hopeful, energetic, possibility-oriented

Respond now.
"""

        response = call_llm(prompt)

        memory["last_response"] = response
        memory["self_history"].append(response)

        save_json(self.memory_file, memory)

        return response
