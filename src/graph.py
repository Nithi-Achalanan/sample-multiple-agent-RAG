from src.agents.data_retriever import retrieve_data
from src.agents.report_generator import generate_report
from src.state import WorkflowState


def run_workflow(query: str, knowledge_base: str = "knowledge_base.txt") -> WorkflowState:
    state = WorkflowState(query=query)
    retrieve_data(state, knowledge_base)
    return generate_report(state)

