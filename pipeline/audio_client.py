import asyncio
import edge_tts

async def generate_coaching_audio(text_script: str, output_filename: str):
    print(f"Generating audio for: {output_filename}...")
    
    # We are using "Christopher", a solid, clear voice for coaching.
    # Other free options include "en-US-GuyNeural" or "en-US-AriaNeural"
    voice = "en-US-ChristopherNeural" 
    
    try:
        # Initialize the TTS engine
        communicate = edge_tts.Communicate(text_script, voice)
        
        # Save directly to an MP3 file
        await communicate.save(output_filename)
        print(f"Success! Saved as {output_filename}")
        
    except Exception as e:
        print(f"Failed to generate audio: {str(e)}")

# This allows us to test the file directly from the terminal
if __name__ == "__main__":
    test_script = "Keep your back flat, elbows close to your torso, and pull the weight to your ribcage to maximize lat engagement."
    
    # Run the async function for our standalone test
    asyncio.run(generate_coaching_audio(test_script, "test_rowing_tip.mp3"))