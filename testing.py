import os
import asyncio
from autogen_core.tools import FunctionTool
from typing_extensions import Annotated
from elevenlabs import ElevenLabs
from autogen_core import CancellationToken
from dotenv import load_dotenv

load_dotenv()

import os
print("API Key loaded:", os.getenv("ELEVENLABS_API_KEY"))

# Setup
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
voice_id = "2qfp6zPuviqeCOZIE9RZ"
elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)

async def generate_voiceovers(messages: list[str]) -> list[str]:
    print("Agent reached here----")
    """
    Generate voiceovers for a list of messages using ElevenLabs API.
    
    Args:
        messages: List of messages to convert to speech
        
    Returns:
        List of file paths to the generated audio files
    """
    os.makedirs("voiceovers", exist_ok=True)
    
    # Check for existing files first
    audio_file_paths = []
    for i in range(1, len(messages) + 1):
        file_path = f"voiceovers/voiceover_{i}.mp3"
        if os.path.exists(file_path):
            audio_file_paths.append(file_path)
            
    # If all files exist, return them
    if len(audio_file_paths) == len(messages):
        print("All voiceover files already exist. Skipping generation.")
        return audio_file_paths
        
    # Generate missing files one by one
    audio_file_paths = []
    for i, message in enumerate(messages, 1):
        try:
            save_file_path = f"voiceovers/voiceover_{i}.mp3"
            if os.path.exists(save_file_path):
                print(f"File {save_file_path} already exists, skipping generation.")
                audio_file_paths.append(save_file_path)
                continue

            print(f"Generating voiceover {i}/{len(messages)}...")
            
            # Generate audio with ElevenLabs
            response = elevenlabs_client.text_to_speech.convert(
                text=message,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                output_format="mp3_22050_32",
            )
            
            # Collect audio chunks
            audio_chunks = []
            for chunk in response:
                if chunk:
                    audio_chunks.append(chunk)
            
            # Save to file
            with open(save_file_path, "wb") as f:
                for chunk in audio_chunks:
                    f.write(chunk)
                        
            print(f"Voiceover {i} generated successfully")
            audio_file_paths.append(save_file_path)
        
        except Exception as e:
            print(f"Error generating voiceover for message: {message}. Error: {e}")
            continue
            
    return audio_file_paths



# ✅ Tool wrapper (AutoGen format)
async def generate_voiceovers_tool(
    captions: Annotated[list[str], "List of captions to convert to voice"]
) -> dict:
    audio_paths = await generate_voiceovers(captions)
    return {"voiceover_paths": audio_paths}

# FunctionTool for Autogen agents
voiceover_tool = FunctionTool(
    generate_voiceovers_tool,
    name="generate_voiceovers_tool",
    description="Generate voiceovers from captions using ElevenLabs and save them locally."
)


async def test_voiceover_tool():
    result = await voiceover_tool.run_json({
        "captions": [
            "Unlock the mystery.",
            "The clock is ticking.",
            "Every clue matters.",
            "Truth is stranger than fiction.",
            "It all comes down to this."
        ]
    }, CancellationToken())
    print(result)

if __name__ == "__main__":
    asyncio.run(test_voiceover_tool())
