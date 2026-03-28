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

    query, context = get_user_context(mode)

    agents = get_agents(mode)

    print("\n--- AGENT RESPONSES ---\n")

    responses = {}

    if mode in ["personal", "whatif"]:
        total_exchanges = 4
        response_history = {agent.name: [] for agent in agents}
        round_transcript = []

        council_context = {
            "mode": mode,
            "query": query,
            "additional_info": context.get("additional_info", []),
            "responses": {}
        }

        for exchange_number in range(1, total_exchanges + 1):
            print(f"--- EXCHANGE {exchange_number}/{total_exchanges} ---\n")

            for agent in agents:
                council_context["responses"] = {
                    agent_name: "\n".join(
                        [
                            f"Exchange {idx + 1}: {entry}"
                            for idx, entry in enumerate(history)
                        ]
                    )
                    for agent_name, history in response_history.items()
                }

                response = agent.respond(
                    query,
                    context,
                    council_context,
                    exchange_number=exchange_number,
                    total_exchanges=total_exchanges
                )

                response_history[agent.name].append(response)
                responses[agent.name] = response
                round_transcript.append(
                    {
                        "exchange": exchange_number,
                        "agent": agent.name,
                        "response": response
                    }
                )

                print(f"{agent.name.upper()}:\n{response}\n")

        responses = {
            "latest": responses,
            "history": response_history,
            "transcript": round_transcript,
            "total_exchanges": total_exchanges,
            "mode": mode
        }
    else:
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