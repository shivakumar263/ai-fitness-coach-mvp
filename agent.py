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

# Import custom pipeline components
from pipeline.audio_client import generate_coaching_audio
from vector_store import get_past_workouts, save_workout_to_db

load_dotenv()

@tool
def generate_audio_tool(text_script: str) -> str:
    """Generates an audio voiceover payload for workout coaching cues."""
    filename = "latest_audio.mp3"
    asyncio.run(generate_coaching_audio(text_script, filename))
    return f"Audio successfully generated and saved at {filename}."

tools = [generate_audio_tool]

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Initialize language model and bind external tools
llm = ChatGroq(model="openai/gpt-oss-20b", api_key=os.getenv("GROQ_API_KEY"))
llm_with_tools = llm.bind_tools(tools)

def agent_node(state: State):
    """
    Processes the conversation state, injects RAG context on the first iteration,
    and invokes the LLM to generate the next response or tool call.
    """
    messages = state["messages"]
    
    # Inject RAG memory context only on the initial user prompt
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
        messages = [SystemMessage(content=system_prompt)] + messages

    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# Construct the state machine graph for the AI agent
builder = StateGraph(State)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
builder.add_edge("tools", "agent")

graph = builder.compile()

def fitness_agent(user_prompt: str) -> str:
    """
    Entry point for the application. Executes the LangGraph workflow
    and persists the generated session to ChromaDB memory.
    """
    result = graph.invoke({"messages": [HumanMessage(content=user_prompt)]})
    generated_workout = result['messages'][-1].content
    
    save_workout_to_db(user_prompt, generated_workout)
    
    return generated_workout

if __name__ == "__main__":
    # CLI execution for pipeline verification
    user_input = "Give me a 15 minute shoulder workout and generate an audio coaching tip."
    print(f"User: {user_input}\n")
    response = fitness_agent(user_input)
    print(f"Agent: {response}")