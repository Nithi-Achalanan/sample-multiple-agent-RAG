"""State shared by every node in the mock RAG workflow."""

from typing import TypedDict
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from src.tools.multiple_keyword_search import SearchResult


class GraphState(TypedDict, total=False):
    conversation: list[str]
    query: str

# first agent artifacts
    summary_agent_state_memory: list[HumanMessage | SystemMessage | ToolMessage | AIMessage]
    final_report: str

# second agent artifacts
    search_agent_state_memory: list[HumanMessage | SystemMessage | ToolMessage | AIMessage]
    retrieved_context: list
    retrieved_context_raw: list[SearchResult]
    search_attempts: int
    max_search_attempts: int
