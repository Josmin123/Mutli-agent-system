Multi-Agent YouTube Shorts Video Generator
This project is an end-to-end, multi-agent framework for automatically generating YouTube Shorts videos using Microsoft AutoGen. The system orchestrates multiple specialized AI agents—script writer, voice actor, graphic designer, and director—to collaboratively create engaging short-form videos from a single user prompt.

Features
Script Writer Agent: Generates a compelling short script and captions for the video.
Voice Actor Agent: Produces voiceovers for each caption using ElevenLabs (with local file stubbing to save API credits).
Graphic Designer Agent: Creates or selects images for each caption using Stability AI or local stubs.
Director Agent: Assembles images, voiceovers, and captions into a final video using MoviePy.
Stub Mode: Supports local-only operation for both images and audio to avoid API usage during development/testing.
Fully Automated Pipeline: Just provide a topic or prompt—everything else is handled by the agents.
Tech Stack
Python
Microsoft AutoGen
MoviePy
ElevenLabs API
Stability AI API
How It Works
User Input: Enter a topic or idea for a video short.
Script Generation: The script writer agent creates a narrative and 5 short captions.
Voiceover Generation: The voice actor agent generates or retrieves voiceover audio for each caption.
Image Generation: The graphic designer agent generates or selects images for each caption.
Video Assembly: The director agent combines images, voiceovers, and captions into a final video.
Output: The system saves a ready-to-upload YouTube Shorts video (final_output.mp4).
Setup
Clone the repository:

**git clone https://github.com/Josmin123/Mutli-agent-system.git
cd Mutli-agent-system**

Create and activate a virtual environment:

**python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate**

Install dependencies:

**pip install -r requirements.txt**

Set up your .env file:

ELEVENLABS_API_KEY=your_elevenlabs_api_key
STABILITY_API_KEY=your_stability_api_key

Add images and music:

Place your images in the images folder.
Place your background music in the music folder.
Usage
Run the main agent pipeline:

Follow the prompts to enter a topic and watch the agents generate your video.

Notes
The system supports both real API and stubbed (local) modes for development.
The generated video will be saved as final_output.mp4 in the project directory.
Make sure to keep your API keys private and never commit them to the repository.
License
MIT License
