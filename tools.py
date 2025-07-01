# tools.py
import asyncio
from autogen_core.tools import FunctionTool
from typing_extensions import Annotated
from elevenlabs import ElevenLabs
from autogen_core import CancellationToken
from moviepy.editor import (
    ImageClip, TextClip, AudioFileClip,
    CompositeVideoClip, concatenate_videoclips
)
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.video.fx.resize import resize
import os
import requests
from dotenv import load_dotenv
load_dotenv()


print("API Key loaded:", os.getenv("ELEVENLABS_API_KEY"))

# Setup
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
voice_id = "2qfp6zPuviqeCOZIE9RZ"
elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)


print("API Key loaded", os.getenv("STABILITY_API_KEY"))

stability_api_key = os.getenv("STABILITY_API_KEY")


#VIOCECOVER FUNCTION
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



# IMAGE GENERATION

def generate_images(prompts: list[str]) -> list[str]:
    """
    Generate images based on text prompts using Stability AI API.

    Args:
        prompts: List of text prompts to generate images from

    Returns:
        List of file paths to the generated images
    """
    seed = 42
    output_dir = "images"
    os.makedirs(output_dir, exist_ok=True)

    stability_api_key = os.getenv("STABILITY_API_KEY")
    stability_api_url = "https://api.stability.ai/v2beta/stable-image/generate/core"
    headers = {
        "Authorization": f"Bearer {stability_api_key}",
        "Accept": "image/*"
    }

    image_paths = []
    for i, prompt in enumerate(prompts, 1):
        print(f"Generating image {i}/{len(prompts)} for prompt: {prompt}")

        # Skip if image already exists
        image_path = os.path.join(output_dir, f"image_{i}.webp")
        if not os.path.exists(image_path):
            # Prepare request payload
            payload = {
                "prompt": (None, prompt),
                "output_format": (None, "webp"),
                "height": (None, "1920"),
                "width": (None, "1080"),
                "seed": (None, str(seed))
            }

            try:
                response = requests.post(stability_api_url, headers=headers, files=payload)
                if response.status_code == 200:
                    with open(image_path, "wb") as image_file:
                        image_file.write(response.content)
                    print(f"Image saved to {image_path}")
                else:
                    print(f"Error generating image {i}: {response.json()}")
            except Exception as e:
                print(f"Error generating image {i}: {e}")
        else:
            print(f"Image already exists: {image_path}")

        image_paths.append(image_path)
    return image_paths


#VIDEO CREATION

IMAGE_DURATION = 5  # seconds
WIDTH, HEIGHT = 1080, 1920
FONT = "./arialbd.ttf"  # Make sure this path is correct
BACKGROUND_MUSIC = "music/grey-sky-810121-PREVIEW.mp3"

def generate_video(captions):
    print("Video generation agent reached here")
    images = sorted(f"images/{f}" for f in os.listdir("images") if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".jfif")))
    voices = sorted(f"voiceovers/{f}" for f in os.listdir("voiceovers") if f.lower().endswith(".mp3"))

    assert len(images) == len(voices) == len(captions), \
        f"Counts mismatch: images={len(images)}, voices={len(voices)}, captions={len(captions)}"

    clips = []

    for img_path, voice_path, cap in zip(images, voices, captions):
        print(f"🖼️ Processing: {img_path} | 🎙️ {voice_path} | 📝 '{cap}'")

        img = ImageClip(img_path).fx(resize, height=HEIGHT)
        voice = AudioFileClip(voice_path)
        img_duration = min(IMAGE_DURATION, voice.duration)
        img = img.set_duration(img_duration).set_pos("center")

        txt = TextClip(cap, font=FONT, fontsize=64, color="white", method="caption", size=(WIDTH-100, None))
        txt = txt.set_duration(img_duration).set_pos(("center", HEIGHT - 200))

        voice = voice.set_duration(img_duration)

        comp = CompositeVideoClip([img, txt], size=(WIDTH, HEIGHT))
        comp = comp.set_audio(voice)
        clips.append(comp)

    final = concatenate_videoclips(clips, method="compose")

    # 🎵 Add background music
    if os.path.exists(BACKGROUND_MUSIC):
        bg_music = AudioFileClip(BACKGROUND_MUSIC).volumex(0.1)  # Lower volume
        bg_music = bg_music.set_duration(final.duration)
        mixed_audio = CompositeAudioClip([final.audio, bg_music])
        final = final.set_audio(mixed_audio)
    else:
        print("⚠️ No background music found. Skipping...")

    final.write_videofile("final_output.mp4", fps=24)
    print("✅ Done: final_output.mp4")



