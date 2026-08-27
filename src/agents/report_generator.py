import os
from typing import List
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.messages import SystemMessage, HumanMessage

from src.state import GraphState

load_dotenv()

def helper_search_data(query: str) -> str:
    """what you want to Search data tell it in very detail string and be board or specific."""
    return f"Search result for: {query}"

def setup_report_generator_agent():
    """Setup the report generator model with available tools."""

    # llm = ChatOpenAI(
    #     model=os.getenv("MAIN_MODEL"),
    #     api_key=os.getenv("OPENAI_API_KEY"),
    # )
    llm = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0,
        api_key = os.getenv("GROQ_API_KEY")
        )

    return llm.bind_tools([helper_search_data])

def report_generator(state: GraphState) -> dict:
    """Generate a report or request additional retrieval."""

    report_agent = setup_report_generator_agent()

    messages = [
        SystemMessage(
            content=(
                "You are a report generator agent. "
                "Use the provided context to answer the user's query. "
                "If the context is insufficient, call search_data."
            )
        ),
        HumanMessage(
            content=(
                f"User query:\n{state.get('query', '')}\n\n"
                f"state memory : {state.get('summary_agent_state_memory', [])}"
            )
        ),
    ]

    response = report_agent.invoke(messages)
    content = response.content.strip()
    print("Response:", response)
    print("Content:", response.content)
    print("Tool calls:", response.tool_calls)

    if response.tool_calls:
        return {
            "summary_agent_state_memory": [
                *state.get("summary_agent_state_memory", []),
                response,
            ],
            "final_report": "",
        }

    return {
        "final_report": response.content,
    }
