import json

from langchain_core.messages import AIMessage, ToolMessage

from src.state import GraphState
from src.tools.multiple_keyword_search import search_tool


def test_search_tool_returns_a_tool_message_for_an_ai_tool_call():
    state: GraphState = {
        "summary_agent_state_memory": [
            AIMessage(
                content="",
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

    result = search_tool(state)

    assert result["search_attempts"] == 1
    tool_message = result["search_agent_state_memory"][-1]
    assert isinstance(tool_message, ToolMessage)
    assert tool_message.tool_call_id == "fc_6a337938-e567-41b1-838e-c2778c7b273a"
    assert tool_message.name == "search_data"
    assert tool_message.artifact == json.loads(tool_message.content)
    assert tool_message.artifact[0]["source"] == "mock://multiple_keyword_search"
    assert tool_message.artifact[0]["content"] == "Mock context for: LangGraph, RAG, benefits"
