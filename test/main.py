from debate_engine import run_debate


def main():
    print("Battle of the Bots")
    question = input("Enter a debate topic or question: ").strip()
    if not question:
        print("Please enter a non-empty question.")
        return

    result = run_debate(question, additional_info=[])
    state = result["state"]

    print("\n--- QUESTION ---\n")
    print(state["question"])

    for round_entry in state.get("rounds", []):
        print(f"\n--- ROUND {round_entry.get('round', '?')} ---\n")
        print("Evaluator Question:\n")
        print(round_entry.get("evaluator_question", ""))
        print("\nPro Defense:\n")
        print(round_entry.get("pro_response", ""))
        print("\nCon Defense:\n")
        print(round_entry.get("con_response", ""))

    print("\n--- FINAL EVALUATION ---\n")
    print(state["judge_result"])

    print("\n--- FINAL DECISION ---\n")
    print(f"Winner: {state['winner']}")

if __name__ == "__main__":
    main()