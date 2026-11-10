import os
import asyncio
from dotenv import load_dotenv
from typing import Annotated, TypedDict
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# Import your custom modules
from pipeline.audio_client import generate_coaching_audio
from vector_store import get_past_workouts, save_workout_to_db

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

# Initialize LLM and bind tools (Updated to a standard Groq model)
llm = ChatGroq(model="openai/gpt-oss-20b", api_key=os.getenv("GROQ_API_KEY"))
llm_with_tools = llm.bind_tools(tools)

# Define the Agent Node with Vector Memory Injection
def agent_node(state: State):
    messages = state["messages"]
    
    # If this is the first iteration (no system message present), inject the RAG context
    if not any(isinstance(m, SystemMessage) for m in messages):
        user_prompt = messages[0].content
        past_context = get_past_workouts(user_prompt)
        
        system_prompt = f"""You are an elite, highly professional AI Fitness Coach. 
        
        Here is the user's recent workout history based on semantic similarity:
        {past_context}
        
        Instructions:
        - Analyze the past history to ensure progressive overload and avoid overtraining.
        - Format your workout schedule cleanly using a Markdown table.
        - Use the generate_audio_tool to create voiceovers.
        """
        # Prepend the system message to guide the LLM
        messages = [SystemMessage(content=system_prompt)] + messages

    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# 3. Build and Compile the Graph
builder = StateGraph(State)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
builder.add_edge("tools", "agent")

graph = builder.compile()

# 4. Main Exported Function for FastAPI
def fitness_agent(user_prompt: str) -> str:
    """Executes the graph, handles tools, and saves the final output to memory."""
    
    # Run the LangGraph workflow
    result = graph.invoke({"messages": [HumanMessage(content=user_prompt)]})
    generated_workout = result['messages'][-1].content
    
    # Save the new routine to ChromaDB for future reference
    save_workout_to_db(user_prompt, generated_workout)
    
    return generated_workout

# 5. Local Testing
if __name__ == "__main__":
    user_input = "Give me a 15 minute shoulder workout and generate an audio coaching tip."
    print(f"User: {user_input}\n")
    response = fitness_agent(user_input)
    print(f"Agent: {response}")