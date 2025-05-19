from langchain.chat_models import init_chat_model
from typing import Annotated
from langchain_tavily import TavilySearch
from langchain_core.tools import tool, InjectedToolCallId
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, interrupt
from langchain_core.messages import ToolMessage  # Added import for ToolMessage

# Initialize LLM
llm = init_chat_model(
    "llama-3.1-8b-instant",
    model_provider="groq",
    temperature=0
)

# Define State with both messages and user profile information
class State(TypedDict):
    messages: Annotated[list, add_messages]
    name: str
    birthday: str

# Initialize graph builder
graph_builder = StateGraph(State)

# Define human assistance tool with state updating capability
@tool
def human_assistance(
    name: str, 
    birthday: str, 
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> str:
    """Request assistance from a human to verify information."""
    human_response = interrupt(
        {
            "question": "Is this correct?",
            "name": name,
            "birthday": birthday,
        },
    )
    
    # If the information is correct, update the state as-is
    if human_response.get("correct", "").lower().startswith("y"):
        verified_name = name
        verified_birthday = birthday
        response = "Correct"
    # Otherwise, receive corrected information from the human reviewer
    else:
        verified_name = human_response.get("name", name)
        verified_birthday = human_response.get("birthday", birthday)
        response = f"Made a correction: {human_response}"

    # Return a Command object to update our state
    return Command(update={
        "name": verified_name,
        "birthday": verified_birthday,
        "messages": [ToolMessage(content=response, tool_call_id=tool_call_id)],
    })

# Initialize tools
tool = TavilySearch(max_results=2)
tools = [tool, human_assistance]
llm_with_tools = llm.bind_tools(tools)

# Define chatbot node
def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    return {"messages": [message]}

# Add nodes to graph
graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

# Add edges to graph
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

# Initialize memory checkpoint
memory = MemorySaver()

# Compile graph
graph = graph_builder.compile(checkpointer=memory)

# Main execution
if __name__ == "__main__":
    # Initial configuration
    config = {"configurable": {"thread_id": "1"}}
    
    # First interaction - request information and human review
    user_input = (
        "Can you look up when LangGraph was released? "
        "When you have the answer, use the human_assistance tool for review."
    )
    
    print(f"User: {user_input}")
    print("\nAssistant responses:")
    
    # Stream initial interaction
    events = graph.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config,
        stream_mode="values",
    )
    
    for event in events:
        if "messages" in event:
            event["messages"][-1].pretty_print()
    
    # Simulate human response
    human_command = Command(
        resume={
            "name": "LangGraph",
            "birthday": "Jan 17, 2024",
        },
    )
    
    print("\nHuman review completed. Resuming conversation...")
    
    # Stream response after human input
    events = graph.stream(human_command, config, stream_mode="values")
    for event in events:
        if "messages" in event:
            event["messages"][-1].pretty_print()
    
    # Manually update state with additional information
    graph.update_state(config, {"name": "LangGraph (library)"})
    
    # Get and display final state
    snapshot = graph.get_state(config)
    print("\nFinal state:")
    print({k: v for k, v in snapshot.values.items() if k in ("name", "birthday")})