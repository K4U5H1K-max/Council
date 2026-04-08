"""State helpers for the Battle of the Bots debate flow."""


def create_debate_state(question, additional_info=None):
    """Create a minimal debate state container."""
    return {
        "question": str(question or "").strip(),
        "additional_info": additional_info or [],
        "rounds": [],
        "pro_response": "",
        "con_response": "",
        "judge_result": "",
        "winner": "Draw",
    }
