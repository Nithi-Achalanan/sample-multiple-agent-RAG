from src.state import WorkflowState


def generate_report(state: WorkflowState) -> WorkflowState:
    context = "\n".join(f"- {document}" for document in state.retrieved_documents)
    state.report = (
        f"Query: {state.query}\n\n"
        "Retrieved context:\n"
        f"{context or '- No matching context found.'}"
    )
    return state

