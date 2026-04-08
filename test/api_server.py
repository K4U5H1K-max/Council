import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from dotenv import load_dotenv

from debate_engine import run_debate


ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)


def validate_user_query(query):
    text = str(query or "").strip()
    if not text:
        return False, "Please enter a scenario or question."

    return True, ""


def _parse_final_evaluation(judge_text):
    """Extract structured analysis from evaluator's final response."""
    if not isinstance(judge_text, str):
        return {
            "summary": "",
            "pro_analysis": "",
            "con_analysis": "",
            "critical_factors": "",
            "winner": "Draw",
            "reasoning": "",
        }

    lines = judge_text.split("\n")
    sections = {
        "summary": "",
        "pro_analysis": "",
        "con_analysis": "",
        "critical_factors": "",
        "winner": "Draw",
        "reasoning": "",
    }

    current_section = None
    content_buffer = []

    key_map = {
        "summary:": "summary",
        "pro_analysis:": "pro_analysis",
        "pro strengths & weaknesses:": "pro_analysis",
        "con_analysis:": "con_analysis",
        "con strengths & weaknesses:": "con_analysis",
        "critical_factors:": "critical_factors",
        "critical factors:": "critical_factors",
        "reasoning:": "reasoning",
    }

    for line in lines:
        lower = line.lower().strip()

        if not lower:
            continue

        if lower.startswith("winner:"):
            if current_section and content_buffer:
                sections[current_section] = "\n".join(content_buffer).strip()
            winner_text = line.split(":", 1)[1].strip() if ":" in line else ""
            if winner_text.lower().startswith("pro"):
                sections["winner"] = "Pro"
            elif winner_text.lower().startswith("con"):
                sections["winner"] = "Con"
            else:
                sections["winner"] = "Draw"
            current_section = None
            content_buffer = []
            continue

        matched_section = None
        for prefix, mapped in key_map.items():
            if lower.startswith(prefix):
                matched_section = mapped
                break

        if matched_section:
            if current_section and content_buffer:
                sections[current_section] = "\n".join(content_buffer).strip()
            current_section = matched_section
            content_buffer = [line.split(":", 1)[1].strip()] if ":" in line else []
            continue

        if line.strip():
            if current_section:
                content_buffer.append(line)

    # Flush remaining buffer
    if current_section and content_buffer:
        sections[current_section] = "\n".join(content_buffer).strip()

    if not sections["summary"]:
        compact = " ".join([part.strip() for part in judge_text.splitlines() if part.strip()])
        sections["summary"] = compact[:280]

    if not sections["reasoning"]:
        sections["reasoning"] = "Decision based on comparative strength, consistency, and evidence quality across all rounds."

    return sections


def _normalize_additional_info(additional_info):
    if not isinstance(additional_info, list):
        return []

    normalized = []
    for item in additional_info:
        if not isinstance(item, dict):
            continue
        question = str(item.get("question", "")).strip()
        answer = str(item.get("answer", "")).strip()
        if question and answer:
            normalized.append({"question": question, "answer": answer})
    return normalized


def run_workflow(mode, query, additional_info):
    del mode
    normalized_info = _normalize_additional_info(additional_info)
    debate_result = run_debate(query, additional_info=normalized_info)
    state = debate_result["state"]
    transcript = debate_result["transcript"]

    response_history = {
        "pro": [entry.get("pro_response", "") for entry in state.get("rounds", [])],
        "con": [entry.get("con_response", "") for entry in state.get("rounds", [])],
        "evaluator": [
            entry.get("evaluator_question", "") for entry in state.get("rounds", [])
        ] + [state.get("judge_result", "")],
    }

    latest_responses = {
        "pro": state.get("pro_response", ""),
        "con": state.get("con_response", ""),
        "evaluator": state.get("judge_result", ""),
    }

    structured_responses = {
        "latest": latest_responses,
        "history": response_history,
        "transcript": transcript,
        "total_exchanges": len(state.get("rounds", [])),
        "mode": "debate",
    }

    debate_cards = [
        {
            "id": "D-pro",
            "agent": "Pro Agent",
            "text": state.get("pro_response", ""),
        },
        {
            "id": "D-con",
            "agent": "Con Agent",
            "text": state.get("con_response", ""),
        },
        {
            "id": "D-evaluator",
            "agent": "Evaluator Agent",
            "text": state.get("judge_result", ""),
        },
    ]

    # Parse evaluator's detailed analysis
    analysis = _parse_final_evaluation(state.get("judge_result", ""))

    return {
        "mode": "debate",
        "query": query,
        "context": {
            "mode": "debate",
            "query": query,
            "additional_info": normalized_info,
        },
        "state": state,
        "conversation": structured_responses,
        "debate": debate_cards,
        "final": {
            "text": state.get("judge_result", ""),
            "winner": analysis["winner"],
            "summary": analysis["summary"],
            "pro_analysis": analysis["pro_analysis"],
            "con_analysis": analysis["con_analysis"],
            "critical_factors": analysis["critical_factors"],
            "reasoning": analysis["reasoning"],
            "insights": [
                f"Winner: {analysis['winner']}",
                f"Critical factors in decision: {analysis['critical_factors'][:80]}..." if analysis["critical_factors"] else "No critical factors identified",
            ],
        },
    }


class CouncilAPIHandler(BaseHTTPRequestHandler):
    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json(self, status_code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def end_headers(self):
        self._set_cors_headers()
        super().end_headers()

    def do_GET(self):
        if self.path == "/api/health":
            self._send_json(200, {"status": "ok"})
            return

        self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path not in ("/api/personalizer/questions", "/api/workflow/run"):
            self._send_json(404, {"error": "Not found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
            payload = json.loads(raw)
        except Exception:
            self._send_json(400, {"error": "Invalid JSON payload"})
            return

        mode = str(payload.get("mode", "debate")).strip().lower()
        query = str(payload.get("query", "")).strip()

        if mode not in ("debate", "personal", "whatif"):
            self._send_json(400, {"error": "mode must be 'debate'"})
            return

        if not query:
            self._send_json(400, {"error": "query is required"})
            return

        is_valid, guardrail_message = validate_user_query(query)
        if not is_valid:
            self._send_json(
                400,
                {
                    "error": guardrail_message,
                    "code": "guardrail_irrelevant_prompt",
                },
            )
            return

        if self.path == "/api/personalizer/questions":
            questions = [
                "What context should the bots consider?",
                "Any hard constraints or priorities?",
            ]

            self._send_json(
                200,
                {
                    "mode": "debate",
                    "query": query,
                    "questions": questions,
                    "message": "Optional context can improve Pro/Con defenses during all 3 rounds.",
                },
            )
            return

        additional_info = payload.get("additional_info", [])
        result = run_workflow(mode, query, additional_info)

        self._send_json(
            200,
            result,
        )


def run_server(host="0.0.0.0", port=8000):
    if port is None:
        port = 8000
    server = HTTPServer((host, port), CouncilAPIHandler)
    print(f"Battle of the Bots API running on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
