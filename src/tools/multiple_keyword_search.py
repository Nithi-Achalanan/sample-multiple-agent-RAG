"""Mock retrieval tool used by the graph wiring."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.state import GraphState
import json
from typing import TypedDict
from langchain_core.messages import AIMessage, ToolMessage

class SearchResult(TypedDict):
    content: str
    source: str
    matched_keywords: list[str]


def multiple_keyword_search(keywords: list[str]) -> list[SearchResult]:
    """Return predictable placeholder evidence until real retrieval is connected."""
    if not keywords:
        return []
    result = """[SECTION: Travel Expense Policy]
    Title: Travel Expense Policy

    Employees may claim reasonable expenses incurred during approved business travel.

    Reimbursable expenses include airfare, hotel accommodation,
    local transportation, and meals.

    Receipts are required for expenses greater than THB 500.

Expense claims must be submitted within 30 days after the trip."""
    return [
        {
            "content": f"Mock context for: {', '.join(keywords)}",
            "source": "mock://multiple_keyword_search",
            "matched_keywords": result,
        }
    ]



def search_tool(state: "GraphState") -> dict:
    """Execute retrieval and return the result as a ToolMessage."""
    search_tool_call = None

    for message in reversed(
        state.get("summary_agent_state_memory", [])
    ):
        if isinstance(message, AIMessage) and message.tool_calls:
            search_tool_call = message.tool_calls[0]
            break

    if search_tool_call is None:
        raise ValueError(
            "search_agent was called without a tool call from summary_agent"
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
        name="search_data",
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
                        "args": {"keywords": ["LangGraph", "RAG", "benefits"]},
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
