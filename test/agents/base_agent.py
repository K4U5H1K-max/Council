import json
import re
from pathlib import Path

from llm.client import call_llm
from utils.helpers import load_json, save_json


class BaseAgent:
    """Base class for all agents with common attributes and placeholder methods."""

    def __init__(self, name, personality, memory_file):
        """
        Initialize a BaseAgent.

        Args:
            name (str): The agent's identifier (e.g., "rational")
            personality (str): A description of the agent's personality/role
            memory_file (str): Path to the agent's memory JSON file
        """
        self.name = name
        self.personality = personality
        if Path(memory_file).is_absolute():
            self.memory_file = str(Path(memory_file))
        else:
            # Resolve relative paths against the test workspace root.
            self.memory_file = str((Path(__file__).resolve().parents[1] / memory_file).resolve())

    def respond(self, query, context):
        """
        Generate a response to the user's query.

        Args:
            query (str): The user's main query
            context (dict): Additional context about the user's situation

        Returns:
            str: The agent's response

        Note:
            Placeholder method. Override in subclasses.
        """
        raise NotImplementedError(f"{self.name} agent has not implemented respond()")

    def load_or_init_memory(self, peer_names):
        """Load memory and migrate legacy structure to the current schema."""
        memory = load_json(self.memory_file)
        if not isinstance(memory, dict):
            memory = {}

        memory.setdefault("self_history", [])
        memory.setdefault("last_response", "")
        memory.setdefault("exchange_snapshots", [])

        legacy_opinions = memory.get("opinions", {})
        normalized_opinions = {}

        for peer in peer_names:
            existing = legacy_opinions.get(peer)

            if isinstance(existing, dict):
                normalized_opinions[peer] = {
                    "score": int(existing.get("score", 0)),
                    "latest_view": existing.get("latest_view", ""),
                    "history": existing.get("history", [])
                }
            elif isinstance(existing, (int, float)):
                normalized_opinions[peer] = {
                    "score": int(existing),
                    "latest_view": "",
                    "history": []
                }
            else:
                normalized_opinions[peer] = {
                    "score": 0,
                    "latest_view": "",
                    "history": []
                }

        memory["opinions"] = normalized_opinions

        return memory

    def build_prior_responses_block(self, responses, peer_names):
        lines = []

        for peer in peer_names:
            peer_response = responses.get(peer, "")
            if peer_response and not self._is_error_response(peer_response):
                lines.append(f"- {peer.capitalize()}: {peer_response}")

        if not lines:
            return "- No prior council responses yet."

        return "\n".join(lines)

    def build_opinion_context_block(self, memory, peer_names):
        lines = []

        for peer in peer_names:
            peer_opinion = memory.get("opinions", {}).get(peer, {})
            score = int(peer_opinion.get("score", 0))
            latest_view = peer_opinion.get("latest_view", "") or "No clear stance yet."
            lines.append(f"- {peer.capitalize()} | score={score}: {latest_view}")

        if not lines:
            return "- No stored opinions yet."

        return "\n".join(lines)

    def build_self_history_block(self, memory, max_items=2):
        history = memory.get("self_history", [])
        if not history:
            return "- No prior stance recorded yet."

        recent = history[-max_items:]
        lines = [f"- Prior stance {idx + 1}: {item}" for idx, item in enumerate(recent)]
        return "\n".join(lines)

    @staticmethod
    def _extract_json_object(raw_text):
        """Extract the first JSON object from a model response."""
        if not raw_text:
            return ""

        start = raw_text.find("{")
        end = raw_text.rfind("}")

        if start == -1 or end == -1 or end <= start:
            return ""

        return raw_text[start:end + 1]

    @staticmethod
    def _clamp(value, min_value, max_value):
        return max(min_value, min(max_value, value))

    @staticmethod
    def _split_sentences(text):
        if not text or not isinstance(text, str):
            return []

        return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]

    @staticmethod
    def _is_error_response(response):
        if not isinstance(response, str):
            return False

        lowered = response.strip().lower()
        return lowered.startswith("[error]:") or "timed out" in lowered or "http 4" in lowered or "http 5" in lowered

    def determine_sentence_range(self, exchange_number, total_exchanges, has_prior_responses):
        """Choose response length based on conversation stage and available context."""
        if not has_prior_responses:
            return 2, 3

        if exchange_number >= total_exchanges:
            return 3, 4

        return 3, 4

    def enforce_response_quality(self, response, min_sentences=4, max_sentences=5):
        """Normalize response length to a high-quality 4-5 sentence answer."""
        if self._is_error_response(response):
            return response.strip()

        sentences = self._split_sentences(response)
        if min_sentences <= len(sentences) <= max_sentences:
            return response.strip()

        rewrite_prompt = f"""
Rewrite the response below to improve clarity and quality.

Rules:
- Keep the same core meaning and stance.
- Output ONLY one paragraph.
- Use exactly {min_sentences} to {max_sentences} sentences.
- No bullet points.
- Be specific, coherent, and persuasive.
- Avoid fluff, repetition, and abrupt fragments.

Original response:
{response}
"""

        rewritten = call_llm(rewrite_prompt)
        rewritten_sentences = self._split_sentences(rewritten)

        if min_sentences <= len(rewritten_sentences) <= max_sentences:
            return rewritten.strip()

        # Deterministic fallback: keep the first max_sentences complete sentences.
        if rewritten_sentences:
            return " ".join(rewritten_sentences[:max_sentences]).strip()

        if sentences:
            return " ".join(sentences[:max_sentences]).strip()

        return response.strip()

    @staticmethod
    def _peer_sentences(response, peer):
        if not response:
            return []

        sentences = re.split(r"(?<=[.!?])\s+", response)
        return [s.strip() for s in sentences if peer.lower() in s.lower() and s.strip()]

    def _infer_fallback_peer_opinion(self, response, peer):
        """Infer opinion delta from direct language cues when JSON parsing is weak."""
        peer_sentences = self._peer_sentences(response, peer)
        if not peer_sentences:
            return 0, ""

        signal_text = " ".join(peer_sentences).lower()

        positive_terms = [
            "agree", "valid", "strong", "useful", "helpful", "good point", "resonates",
            "well-founded", "balanced", "support", "insightful"
        ]
        negative_terms = [
            "disagree", "flaw", "weak", "reckless", "unrealistic", "overly", "wrong",
            "costly", "risky", "naive", "hinder"
        ]
        intensity_terms = ["strongly", "completely", "entirely", "highly"]

        pos_hits = sum(signal_text.count(term) for term in positive_terms)
        neg_hits = sum(signal_text.count(term) for term in negative_terms)
        intensity_hits = sum(signal_text.count(term) for term in intensity_terms)

        delta = 0
        if pos_hits > neg_hits:
            delta = 1
        elif neg_hits > pos_hits:
            delta = -1

        if delta != 0 and intensity_hits > 0 and abs(pos_hits - neg_hits) >= 1:
            delta = 2 if delta > 0 else -2

        updated_view = peer_sentences[-1]
        if len(updated_view) > 180:
            updated_view = updated_view[:177].rstrip() + "..."

        return delta, updated_view

    def _update_peer_opinions(self, memory, response, peer_names, exchange_number, peer_response_map=None):
        """Update per-peer opinion scores and notes using deterministic cues from each iteration."""
        peer_response_map = peer_response_map or {}

        for peer in peer_names:
            peer_is_mentioned = peer.lower() in response.lower()
            fallback_delta, fallback_view = self._infer_fallback_peer_opinion(response, peer)

            delta = fallback_delta

            # Penalize ignoring a peer that has an active recent stance, lightly.
            peer_has_recent_content = bool(peer_response_map.get(peer, "").strip())
            if peer_has_recent_content and not peer_is_mentioned and exchange_number > 1:
                delta = self._clamp(delta - 1, -2, 2)

            delta = self._clamp(delta, -2, 2)

            current_score = int(memory["opinions"][peer].get("score", 0))
            new_score = self._clamp(current_score + delta, -5, 5)

            updated_view = ""

            if peer_is_mentioned and not updated_view.strip() and fallback_view:
                updated_view = fallback_view

            if updated_view.strip():
                memory["opinions"][peer]["latest_view"] = updated_view.strip()

            memory["opinions"][peer]["score"] = new_score
            memory["opinions"][peer]["history"].append(
                {
                    "exchange": exchange_number,
                    "delta": delta,
                    "score": new_score,
                    "view": memory["opinions"][peer].get("latest_view", "")
                }
            )

        return memory

    def save_response_and_memory(self, memory, response, peer_names, exchange_number, peer_response_map=None):
        if self._is_error_response(response):
            memory["last_response"] = response
            memory["exchange_snapshots"].append(
                {
                    "exchange": exchange_number,
                    "response": response,
                    "opinion_scores": {
                        peer: memory["opinions"][peer].get("score", 0)
                        for peer in peer_names
                    },
                    "error": True
                }
            )

            try:
                save_json(self.memory_file, memory)
            except Exception as exc:
                print(f"[MEMORY SAVE ERROR] {self.name} -> {self.memory_file}: {exc}")
            return

        memory["last_response"] = response
        memory["self_history"].append(response)

        if exchange_number >= 1:
            memory = self._update_peer_opinions(
                memory,
                response,
                peer_names,
                exchange_number,
                peer_response_map=peer_response_map
            )

        memory["exchange_snapshots"].append(
            {
                "exchange": exchange_number,
                "response": response,
                "opinion_scores": {
                    peer: memory["opinions"][peer].get("score", 0)
                    for peer in peer_names
                }
            }
        )

        try:
            save_json(self.memory_file, memory)
        except Exception as exc:
            print(f"[MEMORY SAVE ERROR] {self.name} -> {self.memory_file}: {exc}")

    def critique(self, other_response, other_agent_name):
        """
        Critique another agent's response.

        Args:
            other_response (str): The response to critique
            other_agent_name (str): The name of the agent being critiqued

        Returns:
            str: The agent's critique

        Note:
            Placeholder method. Override in subclasses.
        """
        raise NotImplementedError(f"{self.name} agent has not implemented critique()")
