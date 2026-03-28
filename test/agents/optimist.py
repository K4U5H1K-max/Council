from llm.client import call_llm
from .base_agent import BaseAgent


class OptimistAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="optimist",
            personality="Hopeful, sees potential and positive possibilities in scenarios",
            memory_file="memory/optimist.json"
        )

    def respond(self, query, context, council_context=None, exchange_number=1, total_exchanges=1):
        peer_names = ["realist", "whatif_ambitious", "pessimist"]
        memory = self.load_or_init_memory(peer_names)

        council_context = council_context or {}
        payload_query = council_context.get("query", query)
        additional_info = council_context.get("additional_info", context.get("additional_info", []))
        responses = council_context.get("responses", {})
        has_prior_responses = any(bool(value.strip()) for value in responses.values())
        prior_responses_block = self.build_prior_responses_block(responses, peer_names)
        opinion_context_block = self.build_opinion_context_block(memory, peer_names)
        self_history_block = self.build_self_history_block(memory)
        use_memory_clause = "Use stored opinions to identify credible upside paths." if exchange_number > 1 else "Do not use stored opinions yet."
        min_sentences, max_sentences = self.determine_sentence_range(
            exchange_number,
            total_exchanges,
            has_prior_responses
        )

        prompt = f"""
You are an Optimist perspective in a "What If" scenario.

You see the potential and positive possibilities in hypothetical situations. You explore best-case outcomes and constructive pathways.

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
- If prior council responses are available, reference only the listed agents and build on at least ONE point.
- If no prior council responses are available, provide an independent first-pass optimistic scenario.
- Do not speculate about agents who have not responded yet.
- {use_memory_clause}
- Evolve your reasoning across rounds.

STRICT RULES:
- {min_sentences}-{max_sentences} sentences based on complexity and available evidence
- No bullet points
- Be hopeful and possibilities-focused
- Highlight positive potential
- Explore constructive outcomes
- DO NOT use soft first-person language ("I'm excited", "I believe", "I think"). Be direct about your stance.

Your tone: hopeful, energetic, possibility-oriented

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
