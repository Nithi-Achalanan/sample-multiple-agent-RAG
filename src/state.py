from dataclasses import dataclass, field


@dataclass
class WorkflowState:
    query: str
    retrieved_documents: list[str] = field(default_factory=list)
    report: str = ""

