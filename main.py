import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

from pipeline.audio_client import generate_coaching_audio

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI(title="Mini AI Fitness API")

@app.get("/")
async def serve_homepage():
    return FileResponse("index.html")

# --- ENSURE THIS ENDPOINT IS PRESENT ---
@app.get("/audio")
async def serve_audio():
    audio_path = "workout_coach_tip.mp3"
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio file not generated yet")
    return FileResponse(audio_path, media_type="audio/mpeg")
# ---------------------------------------

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

@app.post("/generate-workout", response_model=WorkoutPlan)
async def generate_workout(request: UserRequest):
    try:
        json_schema_prompt = """
        You are an expert AI personal trainer. 
        Output strictly in JSON matching this exact structure: 
        {"title": "string", "estimated_minutes": integer, "exercises": [{"name": "string", "reps_or_time": "string", "tips": "string"}]}
        """
        
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": json_schema_prompt},
                {"role": "user", "content": request.prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result_dict = json.loads(completion.choices[0].message.content)
        
        if result_dict.get("exercises"):
            first_exercise = result_dict["exercises"][0]
            tip_script = f"First exercise: {first_exercise['name']}. {first_exercise['tips']}"
            await generate_coaching_audio(tip_script, "workout_coach_tip.mp3")
            
        return result_dict
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))