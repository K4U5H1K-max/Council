from utils.helpers import load_json, save_json
from llm.client import call_llm
from .base_agent import BaseAgent


class EmotionalAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="emotional",
            personality="Empathetic, human-centric, focuses on feelings and emotional consequences",
            memory_file="memory/emotional.json"
        )

    def respond(self, query, context):
        memory = load_json(self.memory_file)

        prompt = f"""
You are an Emotional and Human-Centric thinker.

You focus on feelings, relationships, and human impact.

User Context:
- Query: {context["query"]}
- Additional Info: {context["additional_info"]}

STRICT RULES:
- Write ONLY 3–4 sentences
- No bullet points
- Be empathetic and human
- Consider emotional consequences deeply
- Speak like someone who genuinely cares

Your tone: warm, empathetic, reflective

Respond now.
"""

        response = call_llm(prompt)

        memory["last_response"] = response
        memory["self_history"].append(response)

        save_json(self.memory_file, memory)

        return response