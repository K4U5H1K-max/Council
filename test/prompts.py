"""Role-specific prompts for the Battle of the Bots debate system."""

PRO_PROMPT = """
Argue strongly FOR the topic. Provide 3-4 sentences with concrete reasoning.
Answer the evaluator's specific question first with evidence or logic.
Then explain why your position is superior to the opposing view.
""".strip()


CON_PROMPT = """
Argue strongly AGAINST the topic. Provide 3-4 sentences with concrete reasoning.
Answer the evaluator's specific question first with evidence or logic.
Then explain why the opposing view's argument fails or is incomplete.
""".strip()


EVALUATOR_QUESTION_PROMPT = """
Ask ONE sharp question testing argument quality or evidence. Keep it under 20 words.
""".strip()


EVALUATOR_FINAL_PROMPT = """
You are the final evaluator after 3 rounds. Produce a structured, balanced, high-quality analysis.

Rules:
- Use concrete reasoning from the debate, not generic statements.
- Mention at least one strength and one weakness for BOTH sides.
- Keep each section concise and specific.

Output exactly in this format:
SUMMARY: <2-3 sentences on the core disagreement and overall result>
PRO_ANALYSIS: <2-3 sentences covering strongest point + key weakness>
CON_ANALYSIS: <2-3 sentences covering strongest point + key weakness>
CRITICAL_FACTORS: <2-3 short factors that determined outcome>
WINNER: <Pro|Con|Draw>
REASONING: <2-3 sentences justifying winner with direct comparison>
""".strip()
