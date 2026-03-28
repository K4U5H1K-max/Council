from llm.client import call_personalizer_llm, call_personalizer_final_llm


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
    prompt = f"""
You are a Personalizer Agent.

The user asked:
"{query}"

Ask UP TO 2 short, relevant follow-up questions ONLY if needed to better understand:
- user's situation
- constraints
- preferences

STRICT RULES:
- Return 0, 1, or 2 questions
- Each question must be on a new line
- Do NOT add explanations
"""

    questions = call_personalizer_llm(prompt)

    # Fallback in case of API error
    if "[ERROR]" in questions or not questions.strip():
        questions = "What is your main goal?"

    print("\nAnswer the following:\n")

    # Step 3: Ask at most two optional follow-up questions
    questions_list = [q.strip() for q in questions.strip().split("\n") if q.strip()][:2]
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

    # For what-if mode: extract characteristic points per agent
    if mode == "whatif":
        summary_lines = []
        summary_lines.append(f"SCENARIO: {context['query']}")
        summary_lines.append("\n--- AGENT PERSPECTIVES ---\n")
        
        # Extract first and last stance from each agent's history
        for agent_name in sorted(history.keys()):
            rounds = history.get(agent_name, [])
            if not rounds:
                continue
            
            first_response = rounds[0] if len(rounds) > 0 else ""
            last_response = rounds[-1] if len(rounds) > 0 else ""
            
            agent_display = agent_name.replace("_", " ").title()
            summary_lines.append(f"{agent_display}:")
            
            if first_response:
                truncated = first_response[:120] + "..." if len(first_response) > 120 else first_response
                summary_lines.append(f"  {truncated}")
            
            if len(rounds) > 1 and last_response != first_response:
                truncated = last_response[:120] + "..." if len(last_response) > 120 else last_response
                summary_lines.append(f"  (evolved) {truncated}")
            
            summary_lines.append("")
        
        return "\n".join(summary_lines)

    # For personal mode: personalize based on user context
    formatted_latest = "\n".join([f"{k.upper()}: {v}" for k, v in latest_responses.items()])

    evolution_lines = []
    for agent_name, rounds in history.items():
        if not rounds:
            continue
        first = rounds[0]
        last = rounds[-1]
        evolution_lines.append(f"- {agent_name.upper()} first stance: {first}")
        if len(rounds) > 1:
            evolution_lines.append(f"- {agent_name.upper()} latest stance: {last}")

    if not evolution_lines and transcript:
        for item in transcript[-8:]:
            evolution_lines.append(
                f"- Exchange {item.get('exchange')} {item.get('agent', '').upper()}: {item.get('response', '')}"
            )

    formatted_evolution = "\n".join(evolution_lines) if evolution_lines else "- No multi-round evolution available."

    prompt = f"""
You are a Personalizer Agent.

User Context:
- Query: {context["query"]}
- Additional Info: {context["additional_info"]}

Latest Agent Perspectives:
{formatted_latest}

How Perspectives Evolved Across Rounds:
{formatted_evolution}

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