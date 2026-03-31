import json
import os
from pathlib import Path

from personalizer.personalizer import get_user_context
from langgraph_workflow import run_council_workflow


def _reset_agent_memories(agents):
    """Reset per-agent memory files so each run starts as a fresh conversation."""
    # This is now handled by langgraph_workflow, kept for compatibility
    pass


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

    print("\n--- AGENT RESPONSES (via LangGraph) ---\n")

    # Execute the workflow using LangGraph
    reset_memory = os.getenv("RESET_MEMORY_ON_START", "1").strip() == "1"
    workflow_result = run_council_workflow(
        mode=mode,
        query=query,
        additional_info=context.get("additional_info", []),
        total_exchanges=4,
        reset_memory=reset_memory
    )

    # Display results
    transcript = workflow_result.conversation["transcript"]
    
    # Group by exchange for readability
    current_exchange = None
    for entry in transcript:
        exchange = entry["exchange"]
        if exchange != current_exchange:
            if current_exchange is not None:
                print()
            print(f"--- EXCHANGE {exchange}/4 ---\n")
            current_exchange = exchange
        
        agent_name = entry["agent"]
        response = entry["response"]
        print(f"{agent_name.upper()}:\n{response}\n")

    # Display final personalized answer
    print("\n--- PERSONALIZED FINAL ANSWER ---\n")
    print(workflow_result.final["text"])

if __name__ == "__main__":
    main()