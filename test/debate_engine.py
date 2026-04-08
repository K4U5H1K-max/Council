"""Debate flow orchestration for Battle of the Bots."""

import re

from agents.loader import get_agents
from state import create_debate_state


def _extract_winner(judge_text):
    if not isinstance(judge_text, str):
        return "Draw"

    match = re.search(r"winner\s*:\s*(pro|con|draw)", judge_text, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip().capitalize()

    lowered = judge_text.lower()
    if "winner: pro" in lowered or "winner is pro" in lowered:
        return "Pro"
    if "winner: con" in lowered or "winner is con" in lowered:
        return "Con"
    return "Draw"


def run_debate(question, additional_info=None):
    """Run a complete evaluator-led 3-round debate."""
    state = create_debate_state(question, additional_info=additional_info)
    agents = get_agents("debate")
    role_map = {agent.role: agent for agent in agents}

    pro_agent = role_map["PRO"]
    con_agent = role_map["CON"]
    evaluator_agent = role_map["EVALUATOR"]

    transcript = []
    total_rounds = 3

    exchange_number = 1
    for round_number in range(1, total_rounds + 1):
        state["current_round"] = round_number

        evaluator_question = evaluator_agent.respond(
            question,
            council_context=state,
            task="round_question",
        )
        state["current_round_question"] = evaluator_question

        transcript.append(
            {
                "exchange": exchange_number,
                "agent": evaluator_agent.name,
                "agent_display": "Evaluator Agent",
                "response": evaluator_question,
            }
        )
        exchange_number += 1

        pro_response = pro_agent.respond(
            question,
            council_context=state,
            task="argument",
        )
        state["pro_response"] = pro_response
        transcript.append(
            {
                "exchange": exchange_number,
                "agent": pro_agent.name,
                "agent_display": "Pro Agent",
                "response": pro_response,
            }
        )
        exchange_number += 1

        con_response = con_agent.respond(
            question,
            council_context=state,
            task="argument",
        )
        state["con_response"] = con_response
        transcript.append(
            {
                "exchange": exchange_number,
                "agent": con_agent.name,
                "agent_display": "Con Agent",
                "response": con_response,
            }
        )
        exchange_number += 1

        state["rounds"].append(
            {
                "round": round_number,
                "evaluator_question": evaluator_question,
                "pro_response": pro_response,
                "con_response": con_response,
            }
        )

    final_evaluation = evaluator_agent.respond(
        question,
        council_context=state,
        task="final_evaluation",
    )
    state["judge_result"] = final_evaluation
    state["winner"] = _extract_winner(final_evaluation)

    transcript.append(
        {
            "exchange": exchange_number,
            "agent": evaluator_agent.name,
            "agent_display": "Evaluator Agent",
            "response": final_evaluation,
        }
    )

    return {
        "state": state,
        "transcript": transcript,
        "winner": state["winner"],
    }
