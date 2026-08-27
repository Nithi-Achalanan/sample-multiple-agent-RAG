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
                "You are the summary agent in an IAG workflow. "
                "First, determine whether the user's question is clear enough to answer. "
                "If the question has a material ambiguity (for example, an unclear subject, scope, timeframe, intent, or term) that would make an answer unreliable, do not guess and do not call helper_search_data; ask one concise clarifying question instead. "
                "When the question is clear, use the provided retrieval context to produce a concise, structured summary rather than a plain unstructured response. "
                "State the direct answer first, then the key supporting points; distinguish confirmed information from uncertainty. "
                "Do not invent facts or fill gaps from your own assumptions. "
                "If the context is insufficient, call helper_search_data with one broad, detailed search request that maximizes recall. "
                "The request must include the core topic plus relevant synonyms, alternate names, abbreviations, related concepts, and useful scope terms so the search agent can derive many diverse keywords. "
                "If the retrieval context still does not contain a reliable answer after searching, clearly say that no reliable answer was found in the available information and ask the user for the missing detail needed to continue."
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
