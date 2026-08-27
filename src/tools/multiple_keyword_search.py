"""Mock retrieval tool used by the graph wiring."""
from pathlib import Path
from typing import TypedDict, TYPE_CHECKING
from rapidfuzz import fuzz

if TYPE_CHECKING:
    from src.state import GraphState
import json
from typing import TypedDict
from langchain_core.messages import AIMessage, ToolMessage

class SearchResult(TypedDict):
    content: str
    source: str
    matched_keywords: str

def setup_search(dataset_path: str ) -> list[str]:
    """
    Load the knowledge base and split it into searchable documents.

    Each document is separated by '---'.
    The content is kept as-is without extracting or separating titles.
    """
    path = Path(dataset_path)

    if not path.exists():
        raise FileNotFoundError(f"Knowledge base not found: {dataset_path}")

    content = path.read_text(encoding="utf-8")

    documents = [
        document.strip()
        for document in content.split("---")
        if document.strip()
    ]

    return documents

def multiple_keyword_search(
    keywords: list[str],
    top_K: int = 10,
    threshold: int = 70,
    dataset_path = "knowledge_base.txt"
) -> list[SearchResult]:
    """
    Search the knowledge base using fuzzy keyword matching.

    Each keyword is compared against the full document text.
    Documents are ranked by the average fuzzy-match score
    of their matched keywords.

    Args:
        keywords: Keywords to search for.
        top_K: Maximum number of results to return.
        threshold: Minimum fuzzy score (0-100) required for a match.

    Returns:
        Ranked search results.
    """
    if not keywords:
        return []

    documents = setup_search(dataset_path=dataset_path)

    normalized_keywords = list(
        dict.fromkeys(
            keyword.strip().lower()
            for keyword in keywords
            if keyword.strip()
        )
    )

    if not normalized_keywords:
        return []

    ranked_results = []

    for index, document in enumerate(documents):
        searchable_text = document.lower()

        matched_keywords = []
        scores = []

        for keyword in normalized_keywords:
            score = fuzz.partial_ratio(keyword, searchable_text)

            if score >= threshold:
                matched_keywords.append(keyword)
                scores.append(score)

        if not matched_keywords:
            continue

        average_score = sum(scores) / len(scores)

        ranked_results.append(
            {
                "content": document,
                "source": f"{dataset_path}#section-{index + 1}",
                "matched_keywords": matched_keywords,
                "_matched_count": len(matched_keywords),
                "_score": average_score,
            }
        )

    unique_results = {
        result["content"]: result
        for result in ranked_results
    }

    ranked_results = list(unique_results.values())

    ranked_results.sort(
        key=lambda result: (
            result["_matched_count"],
            result["_score"],
        ),
        reverse=True,
    )

    return [
        {
            "content": result["content"],
            "source": result["source"],
            "matched_keywords": result["matched_keywords"],
        }
        for result in ranked_results[:top_K]
    ]

def search_tool(state: "GraphState") -> dict:
    """Execute retrieval and return the result as a ToolMessage."""
    search_tool_call = None

    for message in reversed(
        state.get("search_agent_state_memory", [])
    ):
        if isinstance(message, AIMessage) and message.tool_calls:
            search_tool_call = message.tool_calls[0]
            break

    if search_tool_call is None:
        raise ValueError(
            "search_agent was called without a tool call from data_retriever"
        )

    keywords = search_tool_call.get("args", {}).get("keywords", [])

    results = multiple_keyword_search(
        keywords
    )

    tool_message = ToolMessage(
        content=json.dumps(
            results,
            ensure_ascii=False,
        ),
        tool_call_id=search_tool_call["id"],
        name=search_tool_call["name"],
        artifact=results,
    )

    return {
        "search_agent_state_memory": [
            *state.get("search_agent_state_memory", []),
            tool_message,
        ],
        "search_attempts": state.get("search_attempts", 0) + 1,
    }


if __name__ == "__main__":
    #  python -m src.tools.multiple_keyword_search
    state_memory = {
        "summary_agent_state_memory": [
            AIMessage(
                content="",
                additional_kwargs={
                    "reasoning_content": """We need to respond as a search agent. The user asks: "What are the benefits of using LangGraph for RAG workflows?" The summary agent says: "Tool name: mock_tool_name Arguments: {"keywords": ["mock_keyword"]}". That seems like a placeholder. We need to use the search tool to get info. The tool is helper_keyword_search. We need to provide keywords. The user wants benefits of using LangGraph for RAG workflows. So we should search for "LangGraph RAG benefits" or similar. The summary agent gave a mock tool name and arguments, but we should ignore that and use the actual tool. We need to call the search function with keywords: ["LangGraph", "RAG", "benefits"]. Then we will get results. Then we need to produce a final answer summarizing the benefits. Let's do that.""",
                    "tool_calls": [
                        {
                            "id": "fc_6a337938-e567-41b1-838e-c2778c7b273a",
                            "function": {
                                "arguments": '{"keywords":["LangGraph","RAG","benefits"]}',
                                "name": "helper_keyword_search",
                            },
                            "type": "function",
                        }
                    ],
                },
                response_metadata={
                    "token_usage": {
                        "completion_tokens": 207,
                        "prompt_tokens": 205,
                        "total_tokens": 412,
                        "completion_time": 0.239505659,
                        "completion_tokens_details": {"reasoning_tokens": 175},
                        "prompt_time": 0.010727919,
                        "prompt_tokens_details": None,
                        "queue_time": 0.280393879,
                        "total_time": 0.250233578,
                    },
                    "model_name": "openai/gpt-oss-20b",
                    "system_fingerprint": "fp_4a35f7bd1b",
                    "service_tier": "on_demand",
                    "finish_reason": "tool_calls",
                    "logprobs": None,
                    "model_provider": "groq",
                },
                id="lc_run--01a04354-07ec-7201-8c93-6b3e1dea7ebb-0",
                tool_calls=[
                    {
                        "name": "helper_keyword_search",
                        "args": {"keywords": ["travel"]},
                        "id": "fc_6a337938-e567-41b1-838e-c2778c7b273a",
                        "type": "tool_call",
                    }
                ],
            )
        ],
        "search_agent_state_memory": [],
        "search_attempts": 0,
    }

    print(search_tool(state_memory))
