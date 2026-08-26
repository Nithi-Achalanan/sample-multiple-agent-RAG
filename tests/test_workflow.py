from src.graph import run_workflow


def test_workflow_generates_report(tmp_path):
    knowledge_base = tmp_path / "knowledge_base.txt"
    knowledge_base.write_text("Agents coordinate specialized steps.", encoding="utf-8")

    state = run_workflow("agents", str(knowledge_base))

    assert state.retrieved_documents == ["Agents coordinate specialized steps."]
    assert "Retrieved context" in state.report

