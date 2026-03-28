from llm.client import call_llm
from .base_agent import BaseAgent


class PessimistAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="pessimist",
            personality="Cautious about worst-case scenarios, identifies potential pitfalls and risks",
            memory_file="memory/pessimist.json"
        )

    def respond(self, query, context, council_context=None, exchange_number=1, total_exchanges=1):
        peer_names = ["realist", "whatif_ambitious", "optimist"]
        memory = self.load_or_init_memory(peer_names)

        council_context = council_context or {}
        payload_query = council_context.get("query", query)
        additional_info = council_context.get("additional_info", context.get("additional_info", []))
        responses = council_context.get("responses", {})
        has_prior_responses = any(bool(value.strip()) for value in responses.values())
        prior_responses_block = self.build_prior_responses_block(responses, peer_names)
        opinion_context_block = self.build_opinion_context_block(memory, peer_names)
        self_history_block = self.build_self_history_block(memory)
        use_memory_clause = "Use stored opinions to prioritize failure modes and downside controls." if exchange_number > 1 else "Do not use stored opinions yet."
        min_sentences, max_sentences = self.determine_sentence_range(
            exchange_number,
            total_exchanges,
            has_prior_responses
        )

        prompt = f"""
You are a Pessimist perspective in a "What If" scenario.

You identify potential pitfalls, worst-case scenarios, and risks in hypothetical situations. You play devil's advocate to ensure all dangers are considered.

Scenario:
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

DEBATE RULES:
- If prior council responses are available, reference only the listed agents and stress-test at least ONE claim.
- If no prior council responses are available, provide an independent first-pass risk assessment.
- Do not speculate about agents who have not responded yet.
- {use_memory_clause}
- Evolve your reasoning across rounds.

STRICT RULES:
- {min_sentences}-{max_sentences} sentences based on complexity and available evidence
- No bullet points
- Be cautious and risk-aware
- Highlight potential failures and downsides
- Challenge optimistic assumptions
- DO NOT use soft first-person language ("I'm excited", "I believe", "I think"). Be direct about your stance.

Your tone: cautious, skeptical, risk-focused

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
