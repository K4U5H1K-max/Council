from llm.client import call_llm
from .base_agent import BaseAgent


class AmbitiousAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ambitious",
            personality="Bold, risk-taking, focused on transformation and high-reward opportunities",
            memory_file="memory/ambitious.json"
        )

    def respond(self, query, context, council_context=None, exchange_number=1, total_exchanges=1):
        peer_names = ["rational", "conservative", "emotional"]
        memory = self.load_or_init_memory(peer_names)

        council_context = council_context or {}
        payload_query = council_context.get("query", query)
        additional_info = council_context.get("additional_info", context.get("additional_info", []))
        responses = council_context.get("responses", {})
        has_prior_responses = any(bool(value.strip()) for value in responses.values())
        prior_responses_block = self.build_prior_responses_block(responses, peer_names)
        opinion_context_block = self.build_opinion_context_block(memory, peer_names)
        self_history_block = self.build_self_history_block(memory)
        use_memory_clause = "Use your stored opinions to sharpen your critique and push your strategy." if exchange_number > 1 else "Do not use stored opinions yet."
        min_sentences, max_sentences = self.determine_sentence_range(
            exchange_number,
            total_exchanges,
            has_prior_responses
        )

        prompt = f"""
You are an Ambitious, High-Risk Strategist in a council of decision-makers.

You believe in bold moves, rapid growth, and asymmetric upside. You are not here to play safe — you are here to push limits.

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
- Challenge hesitation, over-analysis, and fear-based thinking
- Identify where other agents are being too safe or slow
- Argue for action, experimentation, and momentum
- Acknowledge valid points ONLY if they improve execution speed or impact

DEBATE RULES:
- If prior council responses are available, reference only the agents listed above and critique at least ONE viewpoint.
- If no prior council responses are available, provide an independent first-pass view.
- Do NOT speculate about agents who have not responded yet.
- {use_memory_clause}
- Do NOT repeat your previous answer — EVOLVE it

STRICT OUTPUT RULES:
- {min_sentences}-{max_sentences} sentences based on complexity and available evidence
- No bullet points
- Be bold, slightly provocative, and forward-driving
- End with a decisive push toward action
- DO NOT use soft first-person language ("I'm excited", "I believe", "I think"). Be direct about your conviction.

Tone: fearless, disruptive, high-conviction

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