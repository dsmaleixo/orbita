"""Typed state definition for the Órbita LangGraph."""
from __future__ import annotations
from typing import Literal, Optional, TypedDict
from langchain_core.documents import Document


class OrbitaState(TypedDict):
    user_query: str
    intent: Optional[Literal["general", "rag", "data", "refuse", "automation"]]
    retrieved_docs: list[Document]
    retrieval_attempts: int
    draft_response: Optional[str]
    citations: list[dict]
    self_check_passed: bool
    unsupported_claims: list[str]
    disclaimers: list[str]
    is_blocked: bool
    block_reason: Optional[str]
    automation_type: Optional[Literal["categorize", "goal_alert", "report"]]
    automation_input: Optional[dict]
    automation_output: Optional[dict]
    mcp_tool_calls: list[dict]
    final_response: str


def make_initial_state(
    user_query: str,
    intent: Optional[Literal["general", "rag", "data", "refuse", "automation"]] = None,
    automation_type: Optional[Literal["categorize", "goal_alert", "report"]] = None,
    automation_input: Optional[dict] = None,
) -> OrbitaState:
    return OrbitaState(
        user_query=user_query,
        intent=intent,
        retrieved_docs=[],
        retrieval_attempts=0,
        draft_response=None,
        citations=[],
        self_check_passed=False,
        unsupported_claims=[],
        disclaimers=[],
        is_blocked=False,
        block_reason=None,
        automation_type=automation_type,
        automation_input=automation_input,
        automation_output=None,
        mcp_tool_calls=[],
        final_response="",
    )
