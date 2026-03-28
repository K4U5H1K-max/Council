import re

from llm.client import call_personalizer_llm, call_personalizer_final_llm


def _is_error_like_response(text):
    if not isinstance(text, str):
        return False

    lowered = text.strip().lower()
    return (
        lowered.startswith("[error]:")
        or "timed out" in lowered
        or "http 4" in lowered
        or "http 5" in lowered
        or "error code:" in lowered
    )


def _agent_display_name(agent_name):
    name = str(agent_name or "agent")
    if name == "whatif_ambitious":
        return "Ambitious"
    return name.replace("_", " ").title()


def _clean_stance_text(text):
    if not isinstance(text, str):
        return ""

    cleaned = text.strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"(?i)^exchange\s*\d+\s*:\s*", "", cleaned)
    return cleaned.strip()


def _truncate(text, max_len=220):
    cleaned = _clean_stance_text(text)
    if len(cleaned) <= max_len:
        return cleaned
    return cleaned[: max_len - 3].rstrip() + "..."


def _build_agent_evolution(history):
    rows = []

    for agent_name, rounds in history.items():
        valid_rounds = [r for r in rounds if isinstance(r, str) and r.strip() and not _is_error_like_response(r)]
        if not valid_rounds:
            continue

        initial = _truncate(valid_rounds[0])
        evolved = _truncate(valid_rounds[-1])
        changed = _clean_stance_text(valid_rounds[0]) != _clean_stance_text(valid_rounds[-1])

        rows.append(
            {
                "agent": _agent_display_name(agent_name),
                "initial": initial,
                "evolved": evolved,
                "changed": changed,
                "rounds": len(valid_rounds),
            }
        )

    return rows


def _build_conversation_highlights(history, transcript, max_items=8):
    highlights = []

    for agent_name, rounds in history.items():
        valid_rounds = [r for r in rounds if isinstance(r, str) and r.strip() and not _is_error_like_response(r)]
        if not valid_rounds:
            continue

        highlights.append(f"- {_agent_display_name(agent_name)}: {_truncate(valid_rounds[-1], max_len=200)}")

    if highlights:
        return "\n".join(highlights[:max_items])

    transcript_lines = []
    for item in transcript[-max_items:]:
        response = item.get("response", "")
        if _is_error_like_response(response):
            continue
        transcript_lines.append(
            f"- {_agent_display_name(item.get('agent', 'agent'))}: {_truncate(response, max_len=200)}"
        )

    return "\n".join(transcript_lines) if transcript_lines else "- No usable conversation highlights available."


def _format_evolution_rows(rows):
    if not rows:
        return "- No valid evolution rows available."

    lines = []
    for row in rows:
        lines.append(f"- {row['agent']}")
        lines.append(f"  Initial stance: {row['initial']}")
        lines.append(f"  Evolved stance: {row['evolved']}")
        lines.append(
            "  Evolution note: "
            + (
                "Shifted/refined position across rounds."
                if row["changed"]
                else "Maintained core position with added detail."
            )
        )
    return "\n".join(lines)


def generate_follow_up_questions(query, mode):
    """Generate up to two follow-up questions for personal mode; none for what-if mode."""
    if mode == "whatif":
        return []

    prompt = f"""
You are a Personalizer Agent.

The user asked:
"{query}"

Your goal:
- Ask UP TO 2 short, relevant follow-up questions ONLY if needed.
- Questions must clarify:
   • the user's situation
   • constraints
   • preferences
- Focus only on what you need to know to personalize your guidance.
- Questions must be directly related to the user’s query and choice.
- Do NOT include explanations, suggestions, or system info.
- Do NOT ask more than 2 questions.
- Return each question on a separate line.
- Return 0 questions if no clarification is needed.
"""

    questions = call_personalizer_llm(prompt)

    if "[ERROR]" in questions or not questions.strip():
        return ["What is your main goal?"]

    return [q.strip() for q in questions.strip().split("\n") if q.strip()][:2]


def get_user_context(mode):
    print("\n--- PERSONALIZER ---")

    # Step 1: Get user query
    query = input("Enter your question: ")

    # For what-if mode: skip additional info collection
    if mode == "whatif":
        context = {
            "mode": mode,
            "query": query,
            "additional_info": []
        }
        return query, context

    # For personal mode: collect additional context via questions
    # Step 2: Generate follow-up questions dynamically
    questions_list = generate_follow_up_questions(query, mode)

    print("\nAnswer the following:\n")

    # Step 3: Ask at most two optional follow-up questions
    answers_list = []

    for q in questions_list:
        q = q.strip()
        if q:
            ans = input(f"{q} ")
            answers_list.append({"question": q, "answer": ans})

    freeform = input("Any additional details you want the council to consider? (press Enter to skip): ").strip()
    if freeform:
        answers_list.append({"question": "additional_details", "answer": freeform})

    # Step 4: Store structured context
    context = {
        "mode": mode,
        "query": query,
        "additional_info": answers_list
    }

    return query, context


def generate_final_response(context, agent_responses):
    mode = context.get("mode", "personal")
    latest_responses = agent_responses
    history = {}
    transcript = []

    if isinstance(agent_responses, dict) and "latest" in agent_responses:
        latest_responses = agent_responses.get("latest", {})
        history = agent_responses.get("history", {})
        transcript = agent_responses.get("transcript", [])

    conversation_highlights = _build_conversation_highlights(history, transcript)

    # For what-if mode: return structured and personalized synthesis.
    if mode == "whatif":
        prompt = f"""
You are a Personalizer Agent preparing a concise final brief for a what-if scenario.

Scenario:
{context.get("query", "")}

Additional info (if any):
{context.get("additional_info", [])}

Council conversation highlights:
{conversation_highlights}

Your goals:
- Provide a personalized recommendation directly to the user.
- Be realistic about constraints and trade-offs.

STRICT FORMAT (must follow exactly):
Council Decision Summary:
(2-3 sentences with the main verdict)

Consensus:
(2-3 sentences summarizing where the council broadly aligns)

Personalized Recommendation:
(2-3 sentences speaking directly to the user: use "you")

Risk Watchouts:
(1-2 short sentences)

Constraints:
- Max 220 words total.
- Keep structure and headings.
- Do not output markdown code blocks.
"""

        final_response = call_personalizer_final_llm(prompt, temperature=0.5)
        if "[ERROR]" in final_response or not final_response.strip():
            fallback_lines = [
                "Council Decision Summary:",
                f"The council sees {context.get('query', '')} as feasible only with staged experimentation and clear limits.",
                "",
                "Consensus:",
                "The council broadly aligns on testing this scenario incrementally, using practical checkpoints before any full commitment.",
                "",
                "Personalized Recommendation:",
                "You should test this scenario in a bounded way first, then scale only if practical constraints and benefits both hold up.",
                "",
                "Risk Watchouts:",
                "Watch for hidden execution costs, social impact, and long-term sustainability risks.",
            ]
            return "\n".join(fallback_lines)

        return final_response.strip()

    # For personal mode: personalize based on user context and highlights.
    formatted_latest = "\n".join([f"{k.upper()}: {v}" for k, v in latest_responses.items()])

    prompt = f"""
You are a Personalizer Agent.

User Context:
- Query: {context["query"]}
- Additional Info: {context["additional_info"]}

Latest Agent Perspectives:
{formatted_latest}

Council conversation highlights:
{conversation_highlights}

Your job:
- Understand the user's emotional and practical situation
- Identify which advice actually fits THIS specific user
- Recognize how conflicts changed through the rounds
- Choose a direction and justify it

CRITICAL:
- This is a human situation, not just logic
- The user is vulnerable → respond thoughtfully
- Balance realism with empathy

STRICT RULES:
- Max 120 words
- No bullet points
- Speak directly to the user
- Be clear and decisive
- Use additional info from the beginning explicitly

Output format:

Insight:
(What is really going on in the user's situation)

Advice:
(What the user should realistically do, tailored to them)

Consensus Snapshot:
(One concise line summarizing the council's overall alignment for this user)
"""

    final_response = call_personalizer_final_llm(prompt)

    # Fallback if API fails
    if "[ERROR]" in final_response or not final_response.strip():
        error_detail = final_response.strip() if final_response else "Unknown error"
        if len(error_detail) > 220:
            error_detail = error_detail[:217].rstrip() + "..."
        final_response = (
            "Key Insight: Unable to generate a response.\n"
            f"Recommended Action: Check Featherless final-model settings. Details: {error_detail}"
        )

    return final_response