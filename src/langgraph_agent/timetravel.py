from langchain.chat_models import init_chat_model
from typing import Annotated
from langchain_tavily import TavilySearch
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# Initialize LLM
llm = init_chat_model(
    "llama-3.1-8b-instant",
    model_provider="groq",
    temperature=0
)

# Define State
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Initialize graph builder
graph_builder = StateGraph(State)

# Initialize tools
tool = TavilySearch(max_results=2)
tools = [tool]
llm_with_tools = llm.bind_tools(tools)

# Define chatbot node
def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# Add nodes to graph
graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=[tool])
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
    # Configuration for thread
    config = {"configurable": {"thread_id": "1"}}
    
    # First interaction - research request
    print("\nFirst interaction:")
    events = graph.stream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "I'm learning LangGraph. Could you do some research on it for me?",
                },
            ],
        },
        config,
        stream_mode="values",
    )
    for event in events:
        if "messages" in event:
            event["messages"][-1].pretty_print()
    
    # Second interaction - follow up
    print("\nSecond interaction:")
    events = graph.stream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Ya that's helpful. Maybe I'll build an autonomous agent with it!",
                },
            ],
        },
        config,
        stream_mode="values",
    )
    for event in events:
        if "messages" in event:
            event["messages"][-1].pretty_print()
    
    # State history inspection
    print("\nState history inspection:")
    to_replay = None
    for state in graph.get_state_history(config):
        print("Num Messages:", len(state.values["messages"]), "Next:", state.next)
        print("-" * 80)
        if len(state.values["messages"]) == 6:
            # Select a specific state based on message count
            to_replay = state
    
    if to_replay:
        print("\nSelected state to replay:")
        print("Next:", to_replay.next)
        print("Config:", to_replay.config)
        
        # Replay from selected state
        print("\nReplaying from selected state:")
        for event in graph.stream(None, to_replay.config, stream_mode="values"):
            if "messages" in event:
                event["messages"][-1].pretty_print()