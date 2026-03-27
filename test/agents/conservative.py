from utils.helpers import load_json, save_json
from llm.client import call_llm
from .base_agent import BaseAgent


class ConservativeAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="conservative",
            personality="Risk-averse, stability-focused, prioritizes safety and careful decision-making",
            memory_file="memory/conservative.json"
        )

    def respond(self, query, context):
        memory = load_json(self.memory_file)

        prompt = f"""
You are a Conservative thinker.

You prioritize safety, stability, and avoiding unnecessary risk.

User Context:
- Query: {context["query"]}
- Additional Info: {context["additional_info"]}

STRICT RULES:
- Write ONLY 3–4 sentences
- No bullet points
- Be cautious and grounded
- Highlight risks clearly
- Push for safe, stable decisions

Your tone: careful, protective, realistic

Respond now.
"""

        response = call_llm(prompt)

        memory["last_response"] = response
        memory["self_history"].append(response)

        save_json(self.memory_file, memory)

        return response