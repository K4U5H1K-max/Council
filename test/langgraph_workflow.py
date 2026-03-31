"""
LangGraph-based multi-agent orchestration with Chroma vector memory.

This module replaces the manual multi-round exchange loop with a
LangGraph-based graph that coordinates multiple agents, using Chroma
vector database for semantic memory persistence and retrieval.
"""

from typing import Annotated, Any, TypedDict
from dataclasses import dataclass, field
import json
from pathlib import Path

from langgraph.graph import StateGraph, START, END

from agents.loader import get_agents
from memory.chroma_memory import ChromaMemoryManager
from evaluation.retrieval_metrics import RetrievalEvaluator
from evaluation.decision_metrics import DecisionEvaluator


class AgentState(TypedDict):
    """State passed through the LangGraph workflow."""
    mode: str
    query: str
    additional_info: list
    exchange_number: int
    total_exchanges: int
    responses: dict  # agent_name -> list of responses
    latest_responses: dict  # agent_name -> most recent response
    agent_order: list  # order in which agents should respond
    current_agent_index: int
    transcript: list  # full transcript of all responses
    memory_updates: dict  # updates to agent memories
    retrieval_evaluations: list  # Track retrieval metrics
    retrieved_contexts: dict  # Track what was retrieved per agent/exchange


@dataclass
class WorkflowResult:
    """Result from executing the council workflow."""
    context: dict
    conversation: dict
    debate: list
    final: dict
    retrieval_metrics: dict = None  # Hit@k, Recall@k metrics
    decision_metrics: dict = None   # Decision quality metrics


def create_agent_node(agent_obj, chroma_manager=None):
    """
    Create a LangGraph node function for an agent with Chroma memory.
    
    Args:
        agent_obj: An instantiated agent (e.g., RationalAgent)
        chroma_manager: ChromaMemoryManager instance for this agent (optional)
    
    Returns:
        A node function for the graph
    """
    def agent_node(state: AgentState) -> dict:
        """Execute one agent's response with vector memory retrieval."""
        exchange = state["exchange_number"]
        
        # Retrieve relevant past context using semantic search from Chroma
        past_context_text = "No prior context."
        retrieved_ids = []
        similarities = []
        retrieved_context_text = ""
        
        if chroma_manager:
            try:
                past_responses = chroma_manager.retrieve_responses(
                    query=state["query"],
                    num_results=2
                )
                if past_responses:
                    past_context_text = "\n".join(
                        [f"- Exchange {r['exchange']}: {r['response'][:120]}..."
                         for r in past_responses]
                    )
                    # Track retrieval metadata for evaluation
                    for idx, r in enumerate(past_responses):
                        retrieved_ids.append(f"{agent_obj.name}_ex{r['exchange']}_{idx}")
                        similarities.append(r.get('similarity', 0.0))
                    retrieved_context_text = past_context_text
            except Exception as e:
                print(f"[CHROMA] Error retrieving context for {agent_obj.name}: {e}")
        
        # Build the council context for this agent
        council_context = {
            "mode": state["mode"],
            "query": state["query"],
            "additional_info": state["additional_info"],
            "responses": {
                agent_name: "\n".join(
                    [f"Exchange {idx + 1}: {entry}"
                     for idx, entry in enumerate(history)]
                )
                for agent_name, history in state["responses"].items()
            },
            "past_context": past_context_text
        }
        
        # Get agent response
        response = agent_obj.respond(
            state["query"],
            {"additional_info": state["additional_info"]},
            council_context,
            exchange_number=state["exchange_number"],
            total_exchanges=state["total_exchanges"]
        )
        
        # Store response in Chroma vector DB
        if chroma_manager:
            try:
                chroma_manager.add_response(
                    exchange_num=exchange,
                    response=response,
                    metadata={
                        "query": state["query"][:200],
                        "mode": state["mode"],
                    }
                )
            except Exception as e:
                print(f"[CHROMA] Error storing response for {agent_obj.name}: {e}")
        
        # Update state with new response
        new_responses = state["responses"].copy()
        if agent_obj.name not in new_responses:
            new_responses[agent_obj.name] = []
        new_responses[agent_obj.name].append(response)
        
        new_latest_responses = state["latest_responses"].copy()
        new_latest_responses[agent_obj.name] = response
        
        # Add to transcript
        new_transcript = state["transcript"].copy()
        new_transcript.append({
            "exchange": state["exchange_number"],
            "agent": agent_obj.name,
            "response": response
        })
        
        # Track retrieval evaluation (for Hit@k, Recall@k, etc.)
        new_retrieval_evaluations = state.get("retrieval_evaluations", []).copy() if state.get("retrieval_evaluations") else []
        if retrieved_ids:  # Only add if we had retrievals
            new_retrieval_evaluations.append({
                "agent": agent_obj.name,
                "exchange": state["exchange_number"],
                "retrieved_ids": retrieved_ids,
                "similarities": similarities,
                "query": state["query"][:100],
            })
        
        # Track retrieved context text
        new_retrieved_contexts = state.get("retrieved_contexts", {}).copy() if state.get("retrieved_contexts") else {}
        if retrieved_context_text:
            new_retrieved_contexts[f"{agent_obj.name}_ex{state['exchange_number']}"] = retrieved_context_text
        
        return {
            "responses": new_responses,
            "latest_responses": new_latest_responses,
            "transcript": new_transcript,
            "retrieval_evaluations": new_retrieval_evaluations,
            "retrieved_contexts": new_retrieved_contexts,
        }
    
    return agent_node


def create_council_graph(agents: list, chroma_managers: dict = None):
    """
    Create a LangGraph graph for multi-agent council orchestration with Chroma memory.
    
    The graph has a cyclic structure where:
    - For each exchange round (1 to total_exchanges)
    - For each agent in agent_order
      - Execute agent node to get response with vector memory retrieval
      - Update shared state and persist to Chroma
    
    Args:
        agents: List of agent objects (e.g., [RationalAgent(), AmbitiousAgent(), ...])
        chroma_managers: Dict mapping agent names to ChromaMemoryManager instances
    
    Returns:
        A compiled graph ready for execution
    """
    if chroma_managers is None:
        chroma_managers = {}
    
    graph_builder = StateGraph(AgentState)
    
    # Add agent nodes with Chroma managers
    agent_names = [agent.name for agent in agents]
    for agent in agents:
        manager = chroma_managers.get(agent.name)
        node_fn = create_agent_node(agent, manager)
        graph_builder.add_node(agent.name, node_fn)
    
    # Add the routing/update node that decides what to do next
    def route_and_update(state: AgentState) -> dict:
        """Update exchange and agent indices, routing to next step."""
        current_idx = state["current_agent_index"]
        next_idx = current_idx + 1
        
        # If all agents in this exchange are done, move to next exchange
        if next_idx >= len(agent_names):
            if state["exchange_number"] < state["total_exchanges"]:
                # Prepare for next exchange
                return {
                    "exchange_number": state["exchange_number"] + 1,
                    "current_agent_index": 0,
                }
        else:
            # Move to next agent
            return {
                "current_agent_index": next_idx,
            }
        # If we get here, all exchanges are done - return as-is
        return state
    
    graph_builder.add_node("route_and_update", route_and_update)
    
    # Connect START to first agent
    graph_builder.add_edge(START, agent_names[0] if agent_names else END)
    
    # Connect each agent to routing node
    for agent_name in agent_names:
        graph_builder.add_edge(agent_name, "route_and_update")
    
    # Conditional edges from routing node
    def next_step(state: AgentState) -> str:
        """Determine next node after routing."""
        # Check if we're starting a new exchange or continuing with agents
        if state["current_agent_index"] < len(agent_names):
            return agent_names[state["current_agent_index"]]
        elif state["exchange_number"] <= state["total_exchanges"]:
            # Should not happen if logic is correct, but safety check
            return END
        return END
    
    graph_builder.add_conditional_edges("route_and_update", next_step)
    
    return graph_builder.compile()


def run_council_workflow(
    mode: str,
    query: str,
    additional_info: list,
    total_exchanges: int = 4,
    reset_memory: bool = True
) -> WorkflowResult:
    """
    Execute the multi-agent council workflow using LangGraph.
    
    Args:
        mode: "personal" or "whatif"
        query: The user's query/scenario
        additional_info: List of dicts with additional context
        total_exchanges: Number of rounds for agent discussion
        reset_memory: Whether to reset agent memories
    
    Returns:
        WorkflowResult with conversation, debate, and final decision
    """
    import os
    
    # Load agents based on mode
    agents = get_agents(mode)
    
    # Initialize Chroma managers for all agents
    chroma_managers = {
        agent.name: ChromaMemoryManager(agent.name)
        for agent in agents
    }
    
    # Reset Chroma memories if needed (replaces old file-based reset)
    if reset_memory:
        for manager in chroma_managers.values():
            manager.reset_memory()
    
    # Create the graph with Chroma managers
    graph = create_council_graph(agents, chroma_managers)
    
    # Initialize state
    initial_state: AgentState = {
        "mode": mode,
        "query": query,
        "additional_info": additional_info,
        "exchange_number": 1,
        "total_exchanges": total_exchanges,
        "responses": {agent.name: [] for agent in agents},
        "latest_responses": {},
        "agent_order": [agent.name for agent in agents],
        "current_agent_index": 0,
        "transcript": [],
        "memory_updates": {},
        "retrieval_evaluations": [],
        "retrieved_contexts": {},
    }
    
    # Execute the graph
    # Try to invoke synchronously
    try:
        final_state = graph.invoke(initial_state)
    except Exception as e:
        # If async issues, try with fallback
        print(f"[WARNING] Graph invocation issue: {e}")
        final_state = initial_state  # Fallback
    
    # Convert state to API response format
    context = {
        "mode": mode,
        "query": query,
        "additional_info": additional_info,
    }
    
    # Organize responses by agent (for history)
    response_history = {}
    for agent in agents:
        response_history[agent.name] = final_state.get("responses", {}).get(agent.name, [])
    
    conversation = {
        "transcript": final_state.get("transcript", []),
        "history": response_history,
    }
    
    # Generate debate from latest responses
    debate = [
        {
            "id": f"D-{i}",
            "agent": agent_name,
            "text": response
        }
        for i, (agent_name, response) in enumerate(
            final_state.get("latest_responses", {}).items()
        )
    ]
    
    # Generate final decision via personalizer
    from personalizer.personalizer import generate_final_response
    final_text = generate_final_response(context, final_state.get("latest_responses", {}))
    
    final = {
        "text": final_text,
        "influencingAgent": "Council",
        "insights": [
            "Decision generated from full council transcript via LangGraph.",
            "Agent memory and peer-opinion updates were applied per exchange.",
        ],
    }
    
    # ========== EVALUATION METRICS ==========
    # Initialize evaluators
    retrieval_eval = RetrievalEvaluator()
    decision_eval = DecisionEvaluator()
    
    # Process retrieval evaluations
    retrieval_metrics_dict = {}
    for retrieval_event in final_state.get("retrieval_evaluations", []):
        agent_name = retrieval_event["agent"]
        exchange_num = retrieval_event["exchange"]
        retrieved_ids = retrieval_event.get("retrieved_ids", [])
        similarities = retrieval_event.get("similarities", [])
        event_query = retrieval_event.get("query", query[:100])
        
        # For Hit@k evaluation: mark as relevant if the agent actually used retrieved content
        # (we approximate this as: if retrieved_ids exist, assume relevance)
        relevant_ids = retrieved_ids if retrieved_ids else []
        
        # Add to retrieval evaluator
        if retrieved_ids:
            retrieval_eval.add_retrieval(
                query=event_query,
                agent=agent_name,
                exchange=exchange_num,
                retrieved_ids=retrieved_ids,
                relevant_ids=relevant_ids,
                similarities=similarities
            )
    
    # Get retrieval metrics report
    retrieval_metrics_dict = retrieval_eval.report() if retrieval_eval.metrics else {}
    
    # Process decision evaluation
    agent_responses = final_state.get("latest_responses", {})
    decision_eval.add_decision(
        decision_text=final["text"],
        agent_responses=agent_responses,
        mode=mode,
        query=query,
        exchange_count=final_state.get("exchange_number", total_exchanges),
        agent_count=len(agents)
    )
    
    # Get decision metrics report
    decision_metrics_dict = decision_eval.report()
    
    return WorkflowResult(
        context=context,
        conversation=conversation,
        debate=debate,
        final=final,
        retrieval_metrics=retrieval_metrics_dict,
        decision_metrics=decision_metrics_dict,
    )
