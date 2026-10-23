# Autonomous AI Fitness Coach API

A multimodal, agentic backend built with FastAPI and LangGraph that dynamically generates personalized workout routines and synthesizes on-the-fly audio coaching using a ReAct architecture. 

## 🏗 System Architecture
This project abandons rigid, hardcoded LLM pipelines in favor of an **Autonomous Agent Workflow**. 
* **Core Logic:** Uses LangGraph to orchestrate a ReAct (Reasoning and Acting) state graph.
* **Tool Calling:** The LLM evaluates user prompts and autonomously decides when to trigger the local text-to-speech audio tool.
* **Zero-Cost Scalability:** Leverages Groq's high-speed API for LLM inference and `edge-tts` for local audio generation, ensuring $0 operational costs.

## 🚀 Tech Stack
* **Backend:** FastAPI, Uvicorn, Python 3.13
* **AI Orchestration:** LangGraph, LangChain
* **LLM Engine:** Groq API 
* **Audio Synthesis:** Edge-TTS (Local, Async)
* **Frontend:** React (In Development)

## ⚙️ Local Setup & Installation

1. **Clone the repository and navigate to the directory:**
   ```bash
   git clone [https://github.com/yourusername/ai-fitness-agent.git](https://github.com/yourusername/ai-fitness-agent.git)
   cd ai-fitness-agent