import json
import os
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from dotenv import load_dotenv

from langgraph_workflow import run_council_workflow
from agents.loader import get_agents
from personalizer.personalizer import generate_follow_up_questions
from personalizer.personalizer import generate_final_response


ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)


IRRELEVANT_OPERATION_PATTERNS = (
    r"\bwrite\s+code\b",
    r"\bbuild\s+(an\s+)?app\b",
    r"\bcreate\s+(a\s+)?website\b",
    r"\bdebug\s+(my\s+)?code\b",
    r"\bfix\s+(the\s+)?bug\b",
    r"\brun\s+(a\s+)?command\b",
    r"\bopen\s+(the\s+)?browser\b",
    r"\bsend\s+(an\s+)?email\b",
    r"\bdownload\s+(a\s+)?file\b",
)

DECISION_CONTEXT_HINTS = (
    " i ",
    " my ",
    " me ",
    "learn",
    "study",
    "career",
    "relationship",
    "health",
    "goal",
    "habit",
    "decision",
    "choose",
    "plan",
    "strategy",
    "what if",
    "should",
)


def validate_user_query(query):
    text = str(query or "").strip()
    if not text:
        return False, "Please enter a scenario or question."

    lowered = f" {text.lower()} "
    is_operational = any(re.search(pattern, lowered) for pattern in IRRELEVANT_OPERATION_PATTERNS)
    has_decision_context = any(hint in lowered for hint in DECISION_CONTEXT_HINTS)

    if is_operational and not has_decision_context:
        return (
            False,
            "This looks like an operational task request. Please rephrase it as a scenario or decision "
            "you want guidance on."
        )

    return True, ""


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


def _format_agent_label(raw_name):
    if raw_name == "whatif_ambitious":
        return "Ambitious"
    return str(raw_name).replace("_", " ").title()


def run_workflow(mode, query, additional_info):
    """Run the council workflow using LangGraph orchestration."""
    reset_memory = os.getenv("RESET_MEMORY_ON_START", "1").strip() == "1"
    additional_info = _normalize_additional_info(additional_info)
    
    # Execute the LangGraph workflow
    workflow_result = run_council_workflow(
        mode=mode,
        query=query,
        additional_info=additional_info,
        total_exchanges=4,
        reset_memory=reset_memory
    )
    
    # Extract and format response for API compatibility
    context = workflow_result.context
    conversation = workflow_result.conversation
    debate = workflow_result.debate
    final = workflow_result.final
    
    # Format agent labels in debate
    formatted_debate = []
    for item in debate:
        formatted_item = item.copy()
        if "agent" in formatted_item and isinstance(formatted_item["agent"], str):
            formatted_item["agent"] = _format_agent_label(formatted_item["agent"])
        formatted_debate.append(formatted_item)
    
    return {
        "mode": mode,
        "query": query,
        "context": context,
        "conversation": conversation,
        "debate": formatted_debate[:4],
        "final": final,
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

        mode = str(payload.get("mode", "personal")).strip().lower()
        query = str(payload.get("query", "")).strip()

        if mode not in ("personal", "whatif"):
            self._send_json(400, {"error": "mode must be 'personal' or 'whatif'"})
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
            questions = generate_follow_up_questions(query, mode)

            self._send_json(
                200,
                {
                    "mode": mode,
                    "query": query,
                    "questions": questions,
                    "message": "Provide a bit more context to help the council." if mode == "personal" else "Optional: add any details you want the council to consider."
                },
            )
            return

        additional_info = payload.get("additional_info", [])
        result = run_workflow(mode, query, additional_info)

        self._send_json(
            200,
            result,
        )


def run_server(host="0.0.0.0", port=None):
    if port is None:
        port = int(os.getenv("PORT", "8000"))
    server = HTTPServer((host, port), CouncilAPIHandler)
    print(f"Council API running on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
