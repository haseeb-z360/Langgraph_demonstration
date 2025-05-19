from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages

import os
from langchain.chat_models import init_chat_model
from IPython.display import Image, display


# Define the conversation state
class State(TypedDict):
    messages: Annotated[list, add_messages]


# Initialize stateful graph
graph_builder = StateGraph(State)

# Initialize the LLM from Groq (make sure GROQ_API_KEY is set in env vars)
llm = init_chat_model(
    "llama-3.1-8b-instant",  # or any other model available via Groq
    model_provider="groq",
    temperature=0
)

# Define chatbot logic node
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

# Add node and connect edges
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")

# Compile the graph
graph = graph_builder.compile()

# Optional visualization
try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    pass


# Function to stream the graph output
def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)


# Chat loop
if __name__ == "__main__":
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            stream_graph_updates(user_input)
        except Exception as e:
            print("Error:", e)
            user_input = "What do you know about LangGraph?"
            print("User: " + user_input)
            stream_graph_updates(user_input)
            break
