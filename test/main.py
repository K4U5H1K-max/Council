from personalizer.personalizer import get_user_context
from agents.loader import get_agents


def select_mode():
    """Prompt the user to select the interaction mode."""
    print("Welcome! I am your Personalizer Agent.")
    print("How would you like to proceed?\n")
    print("1. Personal Consult (Practical decisions)")
    print("2. What If Scenario (Creative exploration)")

    while True:
        choice = input("\nEnter your choice (1 or 2): ").strip()
        if choice == "1":
            return "personal"
        if choice == "2":
            return "whatif"
        print("Invalid input. Please enter 1 or 2.")


def main():
    mode = select_mode()

    print(f"\nSelected mode: {mode}\n")

    query, context = get_user_context()

    agents = get_agents(mode)

    print("\n--- AGENT RESPONSES ---\n")

    responses = {}

    for agent in agents:
        response = agent.respond(query, context)
        responses[agent.name] = response
        print(f"{agent.name.upper()}:\n{response}\n")

    # 🔥 PERSONALIZED FINAL OUTPUT
    from personalizer.personalizer import generate_final_response

    final = generate_final_response(context, responses)

    print("\n--- PERSONALIZED FINAL ANSWER ---\n")
    print(final)

if __name__ == "__main__":
    main()