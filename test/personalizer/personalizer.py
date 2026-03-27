from llm.client import call_llm


def get_user_context():
    print("\n--- PERSONALIZER ---")

    # Step 1: Get user query
    query = input("Enter your question: ")

    # Step 2: Generate follow-up questions dynamically
    prompt = f"""
You are a Personalizer Agent.

The user asked:
"{query}"

Ask EXACTLY 2 short, relevant follow-up questions to better understand:
- user's situation
- constraints
- preferences

STRICT RULES:
- Return ONLY the questions
- Each question must be on a new line
- Do NOT add explanations
"""

    questions = call_llm(prompt)

    # Fallback in case of API error
    if "[ERROR]" in questions or not questions.strip():
        questions = "What is your main goal?\nWhat constraints do you have?"

    print("\nAnswer the following:\n")

    # Step 3: Ask questions one by one
    questions_list = questions.strip().split("\n")
    answers_list = []

    for q in questions_list:
        q = q.strip()
        if q:
            ans = input(f"{q} ")
            answers_list.append({"question": q, "answer": ans})

    # Step 4: Store structured context
    context = {
        "query": query,
        "additional_info": answers_list
    }

    return query, context


def generate_final_response(context, agent_responses):
    # Format agent responses cleanly
    formatted_responses = "\n".join(
        [f"{k.upper()}: {v}" for k, v in agent_responses.items()]
    )

    prompt = f"""
You are a Personalizer Agent.

User Context:
- Query: {context["query"]}
- Additional Info: {context["additional_info"]}

Agent Perspectives:
{formatted_responses}

Your job:
- Understand the user's emotional and practical situation
- Identify which advice actually fits THIS specific user
- Recognize conflicts between agents
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
- Do NOT summarize all agents

Output format:

Insight:
(What is really going on in the user's situation)

Advice:
(What the user should realistically do, tailored to them)
"""

    final_response = call_llm(prompt)

    # Fallback if API fails
    if "[ERROR]" in final_response or not final_response.strip():
        final_response = "Key Insight: Unable to generate a response.\nRecommended Action: Please try again."

    return final_response