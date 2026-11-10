import os
import json
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from agent import fitness_agent
from fastapi.responses import FileResponse
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI(title="Mini AI Fitness API")

# Configure CORS for decoupled frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Updated to allow deployment URLs (Render/Vercel)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def serve_homepage():
    return FileResponse("index.html")

@app.get("/audio")
async def get_audio():
    """Serves the most recently generated AI voiceover payload."""
    return FileResponse(
        "latest_audio.mp3", 
        media_type="audio/mpeg", 
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"}
    )

class Exercise(BaseModel):
    name: str
    reps_or_time: str
    tips: str

class WorkoutPlan(BaseModel):
    title: str
    estimated_minutes: int
    exercises: list[Exercise]

class UserRequest(BaseModel):
    prompt: str

async def generate_ai_video_task(exercise_name: str, output_filename: str):
    """Background task simulator for future video generation capabilities."""
    print(f"🎥 [START] Initiating AI video render for: {exercise_name}...")
    await asyncio.sleep(10) 
    print(f"✅ [DONE] Video render complete! Saved to static/videos/{output_filename}")

@app.post("/generate-workout")
async def generate_workout(request: UserRequest):
    try:
        # Enforce agentic tool-use for audio generation via prompt engineering
        enhanced_prompt = f"{request.prompt}. You MUST use your audio tool to generate a short, motivating audio introduction or coaching tip specifically for this requested workout."
        
        # Execute the LangGraph workflow augmented with ChromaDB memory
        agent_response = fitness_agent(enhanced_prompt)
        
        return {
            "title": "Agentic Workout Plan", 
            "agent_response": agent_response,
            "audio_url": "/audio"
        }
        
    except Exception as e:
        print(f"FastAPI Backend Exception: {e}") 
        raise HTTPException(status_code=500, detail=str(e))