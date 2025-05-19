LangGraph Agent with Human-in-the-Loop Verification
Overview
This project implements a conversational AI agent using LangGraph that can:

Conduct web searches using Tavily

Request human verification for important information

Maintain conversation state and user profile data

Support interruption and resumption of conversations

Persist conversation history using checkpoints

The agent demonstrates advanced features like human-in-the-loop workflows and state management in AI applications.

Features
Conversational Agent: Powered by Groq's Llama 3.1 8B instant model

Web Search: Integrated Tavily search for real-time information retrieval

Human Verification: Ability to pause execution for human review of critical information

State Management: Tracks conversation history and user profile data

Checkpointing: Saves conversation state for resumption and replay

Tool Integration: Supports custom tools with state update capabilities

Requirements
Python 3.8+

Groq API key (for LLM access)

Tavily API key (for web search)

Required Python packages (see Installation)

Installation
Clone the repository:

bash
git clone https://github.com/yourusername/langgraph-agent.git
cd langgraph-agent
Install dependencies:

bash
pip install -r requirements.txt
Or install manually:

bash
pip install langgraph langchain-core langchain-tavily groq

Set up environment variables:
Create a .env file with your API keys:

GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
Code Structure
The main components are:

State Definition (State class):

Tracks conversation messages

Stores user profile information (name, birthday)

Tools:

TavilySearch: For web research

human_assistance: For human verification workflow

Graph Construction:

Chatbot node for LLM interactions

Tools node for executing actions

Conditional edges for routing

Execution Flow:

Initialization with memory checkpointing

Conversation streaming

State inspection and replay

Usage

Run the agent:
python agent.py

Example Interaction Flow:
User asks for information about LangGraph's release date

Agent performs web search

Agent requests human verification of found information

Human provides confirmation/correction

Agent updates state and continues conversation

Key Methods:
human_assistance(): Tool for human verification

chatbot(): Main LLM interaction node

graph.stream(): Processes user input and generates responses

graph.get_state(): Inspects current conversation state

Configuration
Modify these parameters in the code:

llm initialization: Change model or temperature

State class: Add/remove tracked fields

config: Adjust thread ID for conversation tracking

State Management
The agent maintains:

Full conversation history

Verified user profile data

Checkpoints for each significant state change

Access state with:

python
snapshot = graph.get_state(config)
print(snapshot.values)
Extending the Agent
To add new capabilities:

Add Tools:

Create new @tool functions

Bind them to the LLM

Modify State:

Update the State TypedDict

Adjust state updates in tools

Change Workflow:

Add new nodes to the graph

Modify edge conditions

Troubleshooting
Common issues:

Missing API Keys:

Ensure .env file is properly set up

Verify keys have correct permissions

Tool Errors:

Check tool definitions and parameters

Verify tool schemas match LLM expectations

State Issues:

Validate state updates in tools

Check checkpoint storage
