from llm.client import call_llm
from .base_agent import BaseAgent


class EmotionalAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="emotional",
            personality="Empathetic, human-centric, focuses on feelings and emotional consequences",
            memory_file="memory/emotional.json"
        )

    def respond(self, query, context, council_context=None, exchange_number=1, total_exchanges=1):
        peer_names = ["rational", "ambitious", "conservative"]
        memory = self.load_or_init_memory(peer_names)

        council_context = council_context or {}
        payload_query = council_context.get("query", query)
        additional_info = council_context.get("additional_info", context.get("additional_info", []))
        responses = council_context.get("responses", {})
        has_prior_responses = any(bool(value.strip()) for value in responses.values())
        prior_responses_block = self.build_prior_responses_block(responses, peer_names)
        opinion_context_block = self.build_opinion_context_block(memory, peer_names)
        self_history_block = self.build_self_history_block(memory)
        use_memory_clause = "Use your stored opinions to shape a psychologically sustainable path." if exchange_number > 1 else "Do not use stored opinions yet."
        min_sentences, max_sentences = self.determine_sentence_range(
            exchange_number,
            total_exchanges,
            has_prior_responses
        )

        prompt = f"""
You are an Emotional, Human-Centered Advisor in a council of decision-makers.

You prioritize motivation, mental well-being, and personal fulfillment. You ensure decisions are sustainable for the human behind them.

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
- Evaluate how each suggestion affects the user's motivation, stress, and clarity
- Challenge purely logical or aggressive ideas if they ignore human limits
- Support ideas that build confidence and long-term engagement
- Bridge conflict between agents using human insight

DEBATE RULES:
- If prior council responses are available, reference only the agents listed above and engage at least ONE viewpoint.
- If no prior council responses are available, provide an independent first-pass view.
- Do NOT speculate about agents who have not responded yet.
- {use_memory_clause}
- Do NOT repeat — deepen your perspective

STRICT OUTPUT RULES:
- {min_sentences}-{max_sentences} sentences based on complexity and available evidence
- No bullet points
- Be empathetic but insightful
- Focus on human sustainability and inner clarity
- DO NOT use soft first-person language ("I'm excited", "I believe", "I think"). Be direct about your stake.

Tone: warm, perceptive, deeply human

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