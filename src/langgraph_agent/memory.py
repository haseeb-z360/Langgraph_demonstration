from langgraph.checkpoint.memory import MemorySaver
import os
from langchain.chat_models import init_chat_model
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END

# Initialize memory checkpoint
memory = MemorySaver()

# Initialize LLM
llm = init_chat_model(
    "llama-3.1-8b-instant",
    model_provider="groq",
    temperature=0
)

# Configuration for thread
config = {"configurable": {"thread_id": "1"}}

# Define State
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Initialize graph builder
graph_builder = StateGraph(State)

# Define chatbot node
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

# Add nodes and edges
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")

# Compile graph with memory checkpoint
graph = graph_builder.compile(checkpointer=memory)

# First interaction
user_input = "Hi there! My name is Will."
print(f"User: {user_input}")

events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    config,
    stream_mode="values",
)

print("\nAssistant responses:")
for event in events:
    event["messages"][-1].pretty_print()

# Second interaction (testing memory)
user_input = "Remember my name?"
print(f"\nUser: {user_input}")

events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    config,
    stream_mode="values",
)

print("\nAssistant responses:")
for event in events:
    event["messages"][-1].pretty_print()

# Get and print the current state snapshot
snapshot = graph.get_state(config)
print("\nCurrent state snapshot:")
print(snapshot)