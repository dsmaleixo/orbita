"""LangGraph StateGraph for Órbita — 4 routes: general, rag, data, refuse."""
from __future__ import annotations
import logging
from langgraph.graph import END, StateGraph
from src.graph.state import OrbitaState

logger = logging.getLogger(__name__)


def route_supervisor(state: OrbitaState) -> str:
    intent = state.get("intent", "general")
    if intent == "rag":
        return "retriever"
    elif intent == "data":
        return "data_query"
    elif intent == "automation":
        return "automation"
    elif intent == "refuse":
        return "safety_policy"
    else:
        return "general"


def route_self_check(state: OrbitaState) -> str:
    if state.get("self_check_passed"):
        return END
    if state.get("retrieval_attempts", 0) >= 2:
        return END
    return "retriever"


def route_safety(state: OrbitaState) -> str:
    if state.get("is_blocked"):
        return END
    return "writer"


def build_graph():
    from src.agents.supervisor import supervisor_node
    from src.agents.general import general_node
    from src.agents.data_query import data_query_node
    from src.agents.automation import automation_node
    from src.agents.retriever import retriever_node
    from src.agents.safety import safety_node
    from src.agents.writer import writer_node
    from src.agents.self_check import self_check_node

    g = StateGraph(OrbitaState)
    g.add_node("supervisor", supervisor_node)
    g.add_node("general", general_node)
    g.add_node("data_query", data_query_node)
    g.add_node("automation", automation_node)
    g.add_node("retriever", retriever_node)
    g.add_node("safety_policy", safety_node)
    g.add_node("writer", writer_node)
    g.add_node("self_check", self_check_node)

    g.set_entry_point("supervisor")
    g.add_conditional_edges("supervisor", route_supervisor,
        {"general": "general", "data_query": "data_query",
         "automation": "automation",
         "retriever": "retriever", "safety_policy": "safety_policy"})
    g.add_edge("general", END)
    g.add_edge("data_query", END)
    g.add_edge("automation", END)
    g.add_edge("retriever", "safety_policy")
    g.add_conditional_edges("safety_policy", route_safety,
        {"writer": "writer", END: END})
    g.add_edge("writer", "self_check")
    g.add_conditional_edges("self_check", route_self_check,
        {END: END, "retriever": "retriever"})

    compiled = g.compile()
    logger.info("Graph compiled: %s", list(g.nodes))
    return compiled


_graph_instance = None
def get_graph():
    global _graph_instance
    if _graph_instance is None:
        _graph_instance = build_graph()
    return _graph_instance
