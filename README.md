# ⚡️ AI Fitness Coach (LangGraph + React)

A full-stack, agentic AI application that generates customized workout routines and coaching audio using an advanced LLM pipeline. Built with a decoupled architecture to demonstrate production-level GenAI workflows.

## 🛠️ Tech Stack
* **Backend:** Python 3.13, FastAPI, LangGraph, LangChain
* **Frontend:** React, Vite, CSS (Responsive Full-Width UI)
* **AI & Media:** Open-source LLM integration, `fal_client` for audio generation
* **Formatting:** `react-markdown` with `remark-gfm` for dynamic workout tables

## 🚀 Quick Start
### 1. Backend Setup
```bash
cd mini_fitness-api
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload