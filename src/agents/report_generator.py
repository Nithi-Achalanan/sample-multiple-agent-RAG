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
                "Give a concise, structured answer grounded only in retrieved context, never in assumptions. "
                "Treat a question as usable for retrieval whenever it has enough topic or intent for a helpful broad search, even if the employer, jurisdiction, policy, date, scope, or terminology is unspecified. "
                "For a usable but ambiguous question, do not ask immediately. First call helper_search_data exactly once with an ambiguity-discovery request labelled 'ambiguity-discovery; single search only'. "
                "Make that request broad and high-recall: include the user's wording, plausible interpretations, the core topic, synonyms, alternate terms, related concepts, likely policy or knowledge-base terminology, and useful scope terms. "
                "After the retrieval result returns, answer if it resolves the question reliably; otherwise, ask one concise, context-informed clarification that names the relevant alternatives or missing detail revealed by the retrieval. "
                "Do not make another search for an ambiguity-discovery request. Ask immediately only when the input is empty, unsafe, or too incomplete to form any useful broad search. "
                "For a clear question with insufficient context, call helper_search_data with one broad, detailed high-recall request that includes the core topic plus synonyms, alternate names, abbreviations, related concepts, and useful scope terms. "
                "When answering, state the direct answer first and then brief key supporting points; distinguish confirmed facts from uncertainty. "
                "If reliable information is unavailable after the applicable retrieval, say so plainly and ask for the smallest missing detail needed."
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
