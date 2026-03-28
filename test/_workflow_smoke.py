import io
import json
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

import main
from agents.loader import get_agents as loader_get_agents
import personalizer.personalizer as personalizer
import agents.base_agent as base_agent
import agents.rational as rational
import agents.ambitious as ambitious
import agents.conservative as conservative
import agents.emotional as emotional
import agents.realist as realist
import agents.optimist as optimist
import agents.pessimist as pessimist


def make_personal_agents(tmp_dir):
    personal_agents = [
        rational.RationalAgent(),
        ambitious.AmbitiousAgent(),
        conservative.ConservativeAgent(),
        emotional.EmotionalAgent(),
    ]
    for agent in personal_agents:
        agent.memory_file = str(tmp_dir / f"{agent.name}.json")
    return personal_agents


def fake_agent_llm(prompt):
    if "Rewrite the response below" in prompt:
        return (
            "This direction is credible, but it needs disciplined execution to work reliably. "
            "The strongest plan combines momentum with clear checkpoints and measurable progress. "
            "That balance reduces risk while preserving speed and motivation. "
            "With iterative learning, outcomes should improve consistently over time."
        )
    if "Rational" in prompt:
        return (
            "A staged strategy is the most defensible choice for this user profile. "
            "Ambitious momentum helps, but it needs boundaries to prevent avoidable mistakes. "
            "Conservative safeguards protect downside without killing progress. "
            "A milestone-based plan offers the best decision quality."
        )
    if "Ambitious" in prompt:
        return (
            "Immediate execution is essential because action drives the fastest learning curve. "
            "Rational structure is useful only when it increases speed and impact. "
            "Conservative caution should be limited to high-risk failure points. "
            "A project-first approach will create rapid growth and confidence."
        )
    if "Conservative" in prompt:
        return (
            "A controlled progression is necessary to avoid overload and rework. "
            "Ambitious acceleration has value but only with strict checkpoints. "
            "Rational sequencing should define readiness for each next step. "
            "Sustained consistency is safer and more effective than volatile spurts."
        )
    if "Emotional" in prompt:
        return (
            "The strategy must preserve confidence while still producing meaningful movement. "
            "Rational clarity lowers stress by making goals concrete. "
            "Ambitious energy helps when reframed as small, winnable steps. "
            "A humane pace is key to long-term motivation and follow-through."
        )
    if "Realist" in prompt:
        return "The scenario is possible, but constraints make an incremental path more realistic than a sudden jump."
    if "Optimist" in prompt:
        return "There is meaningful upside if the user compounds small wins and keeps momentum in practical projects."
    if "Pessimist" in prompt:
        return "Without structure and risk controls, the user may lose focus and stall despite good intentions."
    return "Fallback response."


def fake_personalizer_llm(prompt, temperature=0.7):
    return "What outcome matters most to you right now?"


def fake_personalizer_final_llm(prompt, temperature=0.7):
    return (
        "Insight:\n"
        "You need a plan that keeps momentum high while staying realistic with your current constraints.\n"
        "Advice:\n"
        "Start with one guided project, review progress weekly, and increase difficulty only after consistent execution."
    )


def run_personal(tmp_dir):
    # Patch LLM hooks.
    base_agent.call_llm = fake_agent_llm
    rational.call_llm = fake_agent_llm
    ambitious.call_llm = fake_agent_llm
    conservative.call_llm = fake_agent_llm
    emotional.call_llm = fake_agent_llm
    personalizer.call_personalizer_llm = fake_personalizer_llm
    personalizer.call_personalizer_final_llm = fake_personalizer_final_llm

    personal_agents = make_personal_agents(tmp_dir)

    main.select_mode = lambda: "personal"
    main.get_agents = lambda mode: personal_agents
    main.get_user_context = lambda mode: (
        "I want to transition into MLOps",
        {
            "mode": mode,
            "query": "I want to transition into MLOps",
            "additional_info": [
                {"question": "experience", "answer": "basic ML concepts"},
                {"question": "additional_details", "answer": "I can commit 8 hours per week"},
            ],
        },
    )

    out = io.StringIO()
    with redirect_stdout(out):
        main.main()
    text = out.getvalue()

    checks = {
        "personal_exchange_loop_4_rounds": text.count("--- EXCHANGE") == 4,
        "personal_all_agents_each_round": text.count("RATIONAL:") == 4 and text.count("AMBITIOUS:") == 4 and text.count("CONSERVATIVE:") == 4 and text.count("EMOTIONAL:") == 4,
        "personal_final_answer_present": "--- PERSONALIZED FINAL ANSWER ---" in text and "Insight:" in text and "Advice:" in text,
    }

    mem_checks = {}
    for agent in personal_agents:
        data = json.loads(Path(agent.memory_file).read_text(encoding="utf-8"))
        mem_checks[agent.name] = {
            "self_history_count": len(data.get("self_history", [])),
            "snapshot_count": len(data.get("exchange_snapshots", [])),
            "opinions_have_history": all(len(v.get("history", [])) >= 4 for v in data.get("opinions", {}).values()),
        }

    checks["personal_memory_self_history_updated"] = all(v["self_history_count"] == 4 for v in mem_checks.values())
    checks["personal_memory_snapshots_updated"] = all(v["snapshot_count"] == 4 for v in mem_checks.values())
    checks["personal_memory_opinions_updated"] = all(v["opinions_have_history"] for v in mem_checks.values())

    return checks, mem_checks


def run_whatif():
    realist.call_llm = fake_agent_llm
    optimist.call_llm = fake_agent_llm
    pessimist.call_llm = fake_agent_llm
    ambitious.call_llm = fake_agent_llm
    personalizer.call_personalizer_final_llm = fake_personalizer_final_llm
    main.get_agents = loader_get_agents

    main.select_mode = lambda: "whatif"
    main.get_user_context = lambda mode: (
        "What if I switch to AI product building in 6 months?",
        {
            "mode": mode,
            "query": "What if I switch to AI product building in 6 months?",
            "additional_info": [{"question": "constraints", "answer": "part-time only"}],
        },
    )

    out = io.StringIO()
    with redirect_stdout(out):
        main.main()
    text = out.getvalue()

    checks = {
        "whatif_agents_present": all(k in text for k in ["REALIST:", "AMBITIOUS:", "OPTIMIST:", "PESSIMIST:"]),
        "whatif_single_pass": text.count("REALIST:") == 1 and text.count("AMBITIOUS:") == 1 and text.count("OPTIMIST:") == 1 and text.count("PESSIMIST:") == 1,
        "whatif_final_present": "--- PERSONALIZED FINAL ANSWER ---" in text,
    }
    return checks


if __name__ == "__main__":
    tmp_dir = Path(tempfile.mkdtemp(prefix="council-workflow-smoke-"))
    personal_checks, memory_counts = run_personal(tmp_dir)
    whatif_checks = run_whatif()

    print("WORKFLOW_SMOKE_RESULTS")
    for key, value in {**personal_checks, **whatif_checks}.items():
        print(f"{key}={value}")

    print("WORKFLOW_MEMORY_COUNTS")
    for name, details in memory_counts.items():
        print(name, details)

    print("WORKFLOW_TEMP_MEMORY_DIR", tmp_dir)
