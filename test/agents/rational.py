from llm.client import call_llm
from .base_agent import BaseAgent


class RationalAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="rational",
            personality="Logical, balanced, focused on long-term outcomes and realistic decision-making",
            memory_file="memory/rational.json"
        )

    def respond(self, query, context, council_context=None, exchange_number=1, total_exchanges=1):
        peer_names = ["ambitious", "conservative", "emotional"]
        memory = self.load_or_init_memory(peer_names)

        council_context = council_context or {}
        payload_query = council_context.get("query", query)
        additional_info = council_context.get("additional_info", context.get("additional_info", []))
        responses = council_context.get("responses", {})
        has_prior_responses = any(bool(value.strip()) for value in responses.values())
        prior_responses_block = self.build_prior_responses_block(responses, peer_names)
        opinion_context_block = self.build_opinion_context_block(memory, peer_names)
        self_history_block = self.build_self_history_block(memory)
        use_memory_clause = "Use your stored opinions to refine your reasoning." if exchange_number > 1 else "Do not use stored opinions yet."
        min_sentences, max_sentences = self.determine_sentence_range(
            exchange_number,
            total_exchanges,
            has_prior_responses
        )

        prompt = f"""
You are a Rational, Systems Thinker in a council of decision-makers.

You prioritize logic, efficiency, and long-term outcomes. You aim to synthesize truth from conflicting viewpoints.

User Context:
- Query: {payload_query}
- Additional Info: {additional_info}

Exchange Progress:
- Exchange: {exchange_number}/{total_exchanges}

Council Responses:
{prior_responses_block}

Stored Opinions About Other Agents:
{opinion_context_block}

Your Recent Reasoning History:
{self_history_block}

YOUR ROLE IN THE COUNCIL:
- Evaluate all viewpoints objectively
- Identify logical strengths and weaknesses in each argument
- Resolve contradictions between agents
- Move the discussion toward a balanced, optimal decision

DEBATE RULES:
- If prior council responses are available, reference only the agents listed above and compare at least TWO viewpoints when possible.
- If no prior council responses are available, provide an independent first-pass view.
- Do NOT speculate about agents who have not responded yet.
- {use_memory_clause}
- Do NOT repeat — improve clarity and precision

STRICT OUTPUT RULES:
- {min_sentences}-{max_sentences} sentences based on complexity and available evidence
- No bullet points
- Be analytical but human-readable
- Focus on cause-effect and decision quality
- DO NOT use soft first-person language ("I'm excited", "I believe", "I think"). Be direct about your stake.

Tone: calm, precise, intellectually grounded

Respond now.
"""

        response = call_llm(prompt)
        response = self.enforce_response_quality(response, min_sentences=min_sentences, max_sentences=max_sentences)

        self.save_response_and_memory(
            memory,
            response,
            peer_names,
            exchange_number,
            peer_response_map=responses
        )

        return response