import os
import asyncio
import fal_client
from dotenv import load_dotenv
from typing import Annotated, TypedDict
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition


# Import your existing audio pipeline
from pipeline.audio_client import generate_coaching_audio

load_dotenv()

# 1. Define the Tools
@tool
def generate_audio_tool(text_script: str) -> str:
    """Use this tool to generate an audio voiceover when the user requests audio coaching."""
    filename = "latest_audio.mp3"
    asyncio.run(generate_coaching_audio(text_script, filename))
    return f"Audio successfully generated and saved at {filename}."

tools = [generate_audio_tool]

# 2. Define the State Graph
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Initialize LLM and bind tools
llm = ChatGroq(model="openai/gpt-oss-20b", api_key=os.getenv("GROQ_API_KEY"))
llm_with_tools = llm.bind_tools(tools)

# Define the Agent Node
def agent_node(state: State):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# 3. Build and Compile the Graph
builder = StateGraph(State)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
builder.add_edge("tools", "agent")

fitness_agent = builder.compile()

# 4. Test the Agent
if __name__ == "__main__":
    user_input = "Give me a 15 minute shoulder workout and generate an audio coaching tip for the first exercise."
    print(f"User: {user_input}\n")
    
    result = fitness_agent.invoke({"messages": [HumanMessage(content=user_input)]})
    print(f"Agent: {result['messages'][-1].content}")