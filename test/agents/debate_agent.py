"""Minimal role-based debate agent implementation."""

from llm.client import call_llm
from prompts import CON_PROMPT, EVALUATOR_FINAL_PROMPT, EVALUATOR_QUESTION_PROMPT, PRO_PROMPT


ROLE_PROMPTS = {
    "PRO": PRO_PROMPT,
    "CON": CON_PROMPT,
    "EVALUATOR_QUESTION": EVALUATOR_QUESTION_PROMPT,
    "EVALUATOR_FINAL": EVALUATOR_FINAL_PROMPT,
}


class DebateAgent:
    """A lightweight agent that changes behavior by role-specific prompting."""

    def __init__(self, name, role):
        self.name = name
        self.role = role

    def _build_prompt(self, question, state, task="argument", round_number=1):
        current_round_question = state.get("current_round_question", "")
        
        # Minimal context: just topic and current question
        shared_context = (
            f"Topic: {question}\n"
            f"Round: {round_number}\n"
            f"Current Question: {current_round_question or '[Evaluator question pending]'}"
        )

        if task == "round_question":
            prompt_header = ROLE_PROMPTS["EVALUATOR_QUESTION"]
        elif task == "final_evaluation":
            prompt_header = ROLE_PROMPTS["EVALUATOR_FINAL"]
        else:
            prompt_header = ROLE_PROMPTS[self.role]

        return f"{prompt_header}\n\n{shared_context}\n\nRespond now using the required format only."

    def respond(self, query, context=None, council_context=None, exchange_number=1, total_exchanges=1, task="argument"):
        del context, exchange_number, total_exchanges
        state = council_context or {}
        round_number = int(state.get("current_round", 1))
        prompt = self._build_prompt(query, state, task=task, round_number=round_number)
        return call_llm(prompt)
