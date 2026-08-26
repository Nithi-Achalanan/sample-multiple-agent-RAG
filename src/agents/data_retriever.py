from pathlib import Path

from src.state import WorkflowState
from src.tools.multiple_keyword_search import multiple_keyword_search


def retrieve_data(state: WorkflowState, knowledge_base: str | Path = "knowledge_base.txt") -> WorkflowState:
    state.retrieved_documents = multiple_keyword_search(state.query, knowledge_base)
    return state

