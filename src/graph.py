"""LangGraph wiring for the mock retrieval and reporting workflow."""

from langgraph.graph import END, START, StateGraph

from src.agents.data_retriever import data_retriever
from src.agents.report_generator import report_generator
from src.state import GraphState
from src.tools.multiple_keyword_search import search_tool

def should_continue(state: GraphState, memory_key: str) -> str:
    """Continue only when the current agent requests one or more tools."""
    messages = state.get(memory_key, [])
    if not messages:
        return END
    last_message = messages[-1]
    if getattr(last_message, "tool_calls", None):
        return "route_to_tool_node"
    return END


def route_to_tool_node(Any) :
    """helper function to route to the tool node in the graph( in purpose to reuse "should_continue" function)"""
    """since we have 1 tool node in the graph, we can route to it directly"""
    return 



def build_retrieval_graph():
    builder = StateGraph(GraphState)
    builder.add_node("data_retriever", data_retriever)
    builder.add_node("search_tool", search_tool)
    builder.add_node("route_to_tool_node", route_to_tool_node)

    builder.add_edge(START, "data_retriever")
    builder.add_conditional_edges("data_retriever",
                                  lambda state: should_continue(
                                      state, "search_agent_state_memory"
                                  ),
                                  ["route_to_tool_node", END]
                                   )
    builder.add_edge("route_to_tool_node", "search_tool")
    builder.add_edge("search_tool", "data_retriever")
    return builder.compile()

def build_main_graph():
    builder = StateGraph(GraphState)
    builder.add_node("report_generator", report_generator)
    builder.add_node("data_retrieval", build_retrieval_graph())
    builder.add_node("route_to_tool_node", route_to_tool_node)


    builder.add_edge(START, "report_generator")
    builder.add_conditional_edges("report_generator",
                                  lambda state: should_continue(
                                      state, "summary_agent_state_memory"
                                  ),
                                  ["route_to_tool_node", END]
                                  )
    builder.add_edge("route_to_tool_node", "data_retrieval")
    builder.add_edge("data_retrieval", "report_generator")
    return builder.compile()

graph = build_main_graph()
