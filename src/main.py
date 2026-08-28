"""Application entry point for the RAG graph."""

from src.graph import graph


def main() -> None:
    """Run the graph with a user query and print the final response."""
    query = input("Ask a question: ").strip()

    if not query:
        print("Please provide a question.")
        return

    result = graph.invoke(
        {
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
    )

    print("\nResponse:")
    print(result["final_report"])


if __name__ == "__main__":
    main()
