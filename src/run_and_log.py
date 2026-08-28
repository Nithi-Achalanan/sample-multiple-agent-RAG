"""Run the RAG graph and save each result as a Markdown log."""

from datetime import datetime
from pathlib import Path
from typing import Any

from src.graph import graph


LOG_DIRECTORY = Path("run_logs")


def format_raw_context(raw_context: list[dict[str, Any]]) -> str:
    """Format retrieved knowledge-base chunks for a Markdown log."""
    if not raw_context:
        return "No raw retrieval context was returned."

    sections: list[str] = []
    for index, item in enumerate(raw_context, start=1):
        source = item.get("source", "Unknown source")
        matched_keywords = ", ".join(item.get("matched_keywords", []))
        content = item.get("content", "")
        sections.append(
            f"### Context {index}\n\n"
            f"- Source: `{source}`\n"
            f"- Matched keywords: {matched_keywords or 'None'}\n\n"
            f"```text\n{content}\n```"
        )

    return "\n\n".join(sections)


def write_log(query: str, result: dict[str, Any], error: Exception | None = None) -> Path:
    """Write one timestamped Markdown record for a graph run."""
    LOG_DIRECTORY.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
    log_path = LOG_DIRECTORY / f"rag_run_{timestamp}.md"

    relevance_response = result.get("retrieved_context", [])
    response_log = "\n\n".join(
        f"### Retrieval response {index}\n\n{response}"
        for index, response in enumerate(relevance_response, start=1)
    ) or "No retrieval response was returned."

    if error is None:
        output = result.get("final_report", "No final response was returned.")
        error_section = ""
    else:
        output = "No final response was returned because the workflow failed."
        error_section = f"\n\n## Error\n\n`{type(error).__name__}: {error}`"

    log_path.write_text(
        "# RAG Run Log\n\n"
        f"- Generated at: {datetime.now().isoformat(timespec='seconds')}\n"
        f"- Status: {'failed' if error else 'completed'}\n\n"
        "## Input\n\n"
        f"```text\n{query}\n```\n\n"
        "## Output\n\n"
        f"{output}\n\n"
        "## Relevance Response\n\n"
        f"{response_log}\n\n"
        "## Relevance Context Log\n\n"
        f"{format_raw_context(result.get('retrieved_context_raw', []))}"
        f"{error_section}\n",
        encoding="utf-8",
    )
    return log_path


def main() -> None:
    """Prompt for a query, run the graph, and save the result."""
    query = input("Ask a question: ").strip()
    if not query:
        print("Please provide a question.")
        return

    initial_state = {
        "query": query,
        "conversation": [],
        "keywords": [],
        "retrieved_context": [],
        "retrieved_context_raw": [],
        "final_report": "",
        "needs_more_search": False,
        "retrieval_complete": False,
        "search_attempts": 0,
        "max_search_attempts": 2,
    }

    try:
        result = graph.invoke(initial_state)
    except Exception as error:
        log_path = write_log(query, {}, error)
        print(f"Workflow failed. Log saved to: {log_path}")
        return

    log_path = write_log(query, result)
    print("\nResponse:")
    print(result.get("final_report", "No final response was returned."))
    print(f"\nLog saved to: {log_path}")


if __name__ == "__main__":
    main()
