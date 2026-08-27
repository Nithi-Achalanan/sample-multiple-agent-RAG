import os
from typing import List

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.messages import SystemMessage, HumanMessage,AIMessage,ToolMessage
import json
from langchain_groq import ChatGroq

from src.state import GraphState

load_dotenv()

def helper_keyword_search(keywords: List[str]) -> str:
    """write the keyword that you want to search for."""
    return f"Search result for: {keywords}"

def setup_search_agent():
    """Setup the search agent model with available tools."""

    # llm = ChatOpenAI(
    #     model=os.getenv("MAIN_MODEL"),
    #     api_key=os.getenv("OPENAI_API_KEY"),
    # )
    llm = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0,
        api_key = os.getenv("GROQ_API_KEY")
        )


    return llm.bind_tools([helper_keyword_search])

def data_retriever(state: GraphState) -> dict:
    """
    Search agent.

    Case 1:
        Search agent requires another search.
        -> Return AIMessage containing tool_calls.
        -> Route to search_tool.

    Case 2:
        Search agent has enough information.
        -> Return ToolMessage for the original summary_agent tool call.
        -> Route back to summary_agent.
    """
    summary_tool_call = None

    for message in reversed(
        state.get("summary_agent_state_memory", [])
    ):
        if isinstance(message, AIMessage) and message.tool_calls:
            summary_tool_call = message.tool_calls[0]
            break

    if summary_tool_call is None:
        # raise ValueError(
        #     "search_agent was called without a tool call from summary_agent"
        # )
        summary_tool_call = {
            "id": "mock_tool_call_id",
            "name": "mock_tool_name",
            "args": {"keywords": ["mock_keyword"]},
        }
    search_agent = setup_search_agent()
    messages = [
            SystemMessage(
                content=(
                    "You are a search agent. "
                    "Your job is to retrieve information requested "
                    "by the summary agent. "
                    "If more information is required, call your search tool. "
                    "If you already have enough information, return the result."
                )
            ),

            *state.get("search_agent_state_memory", []),

            HumanMessage(
                content=(
                    f"Original query:\n"
                    f"{state.get('query', '')}\n\n"

                    f"Request from summary agent:\n"
                    f"Tool name: {summary_tool_call['name']}\n"
                    f"Arguments: "
                    f"{json.dumps(summary_tool_call['args'], ensure_ascii=False)}"
                )
            ),
        ]

    

    response = search_agent.invoke(messages)

#  case 1
    if response.tool_calls:
        return {
            "search_agent_state_memory": [
                *state.get("search_agent_state_memory", []),
                response,  # AIMessage(tool_calls=[...])
            ],
        }
    
# case 2
    tool_message = ToolMessage(
        content=response.content,

        tool_call_id=summary_tool_call["id"],
        name=summary_tool_call["name"],
        artifact=response.content,
    )

    return {
        "search_agent_state_memory": [
            *state.get("search_agent_state_memory", []),
            response,
        ],

        "retrieved_context": [
            *state.get("retrieved_context", []),
            response.content,
        ],

        "summary_agent_state_memory": [
            *state.get("summary_agent_state_memory", []),
            tool_message,
        ],
    }


if __name__ == "__main__":
    #  python -m src.agents.data_retriever
    test_state = {
        "query": "What are the benefits of using LangGraph for RAG workflows?",
        "retrieved_context": [],
        "search_attempts": 0,
        "max_search_attempts": 2,
    }
    result = data_retriever(test_state)
    print(json.dumps(result, indent=4, ensure_ascii=False))
