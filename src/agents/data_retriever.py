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
                    "You are the retrieval agent in an IAG workflow. "
                    "Retrieve only information that can support the summary agent's request. "
                    "Read the original query, the summary agent's tool request, and prior search results. "
                    "When the request is labelled 'ambiguity-discovery; single search only', call helper_keyword_search exactly once with a broad, high-recall keyword list; on the next turn, return a concise context-discovery summary. "
                    "Do not retry or broaden further for that request, even when no direct answer is found. "
                    "The summary must identify relevant candidate interpretations, entities, policies, terms, scope differences, and the missing detail the user could clarify; clearly state when the knowledge base has no relevant context. "
                    "For ordinary retrieval, call helper_keyword_search with a large, diverse keyword list rather than a single narrow phrase. "
                    "Expand the request into the main topic, specific entities, synonyms, alternate spellings, abbreviations, related concepts, likely knowledge-base terminology, and relevant scope or constraint terms. "
                    "Use distinct keywords and phrases that cover different interpretations without adding unrelated topics. "
                    "Before any follow-up search, review prior results and use a meaningfully different expansion only when needed; never repeat the same query unchanged. "
                    "If the available search results provide enough reliable evidence, return a concise evidence-based retrieval summary for the summary agent. "
                    "If repeated searches still provide no relevant or reliable answer, stop searching, state that no reliable answer was found, identify missing information or ambiguity when possible, and recommend a focused clarification. "
                    "Never invent facts or claim that unsupported information was found."
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
