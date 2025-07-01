import asyncio
import os
import json
from dotenv import load_dotenv
from typing_extensions import Annotated
from autogen_core.tools import FunctionTool
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import GraphFlow, DiGraphBuilder
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from tools import generate_voiceovers, generate_images, generate_video

# Load environment variables
load_dotenv()

# === TOOL WRAPPERS ===
async def generate_voiceovers_tool(
    captions: Annotated[list[str], "List of captions to convert to voice"]
) -> dict:
    audio_paths = await generate_voiceovers(captions)
    return {"voiceover_paths": audio_paths}

voiceover_tool = FunctionTool(
    generate_voiceovers_tool,
    name="generate_voiceovers_tool",
    description="Generate voiceovers from captions using ElevenLabs and save them locally."
)

def generate_images_tool(
    captions: Annotated[list[str], "List of short captions to convert into images"]
) -> dict:
    prompts = [f"{caption} in Abstract Art Style / Ultra High Quality." for caption in captions]
    image_paths = generate_images(prompts)
    print("[TOOL] generate_images_tool returned:", image_paths)
    if image_paths is None:
        image_paths = []
    # Pass captions along with image_paths for the director agent
    return {"image_paths": image_paths, "captions": captions}

image_generation_tool = FunctionTool(
    generate_images_tool,
    name="generate_images_tool",
    description="Generate images from a list of captions using Stability AI."
)

def generate_video_tool(
    captions: Annotated[list[str], "List of cleaned captions for video creation"]
) -> dict:
    print("[TOOL] generate_video_tool called with captions:", captions)
    generate_video(captions)
    return {"video_path": "final_output.mp4"}

video_generation_tool = FunctionTool(
    generate_video_tool,
    name="generate_video_tool",
    description="Create a video using pre-generated voiceovers, images, and provided captions."
)

# === CAPTIONS GLOBAL VARIABLE ===
captions_global = []

def extract_captions(text):
    try:
        if text.strip().startswith("```json"):
            text = text.strip().strip("```json").strip("```")
        data = json.loads(text)
        return data.get("captions", [])
    except Exception as e:
        print("❌ Failed to extract captions:", e)
        return []

# === MAIN FUNCTION ===
async def main():
    model_client = OpenAIChatCompletionClient(model="gemini-1.5-flash-8b") 
    
    script_writer = AssistantAgent(
        name="script_writer",
        model_client=model_client,
        system_message='''
            You are a creative assistant tasked with writing a script for a short video.
            The script should contain exactly 5 captions (max 8 words each) in a compelling narrative.
            Return response in JSON format:
            {
                "topic": "topic",
                "takeaway": "takeaway",
                "captions": ["caption1", ..., "caption5"]
            }
        '''
    )

    voice_actor = AssistantAgent(
        name="voice_actor",
        model_client=model_client,
        tools=[voiceover_tool],
        system_message=(
            "You are only allowed to use the tool generate_voiceovers_tool. "
            "Do not attempt to generate voiceovers yourself. "
            "Always call the tool when asked to generate voiceovers. "
            "Respond with 'TERMINATE' when done."
        )
    )

    graphic_designer = AssistantAgent(
        name="graphic_designer",
        model_client=model_client,
        tools=[image_generation_tool],
        system_message=(
            "You are only allowed to use the tool generate_images_tool. "
            "Never output JSON, summaries, or text directly. Only call the tool. "
            "If you do not call the tool, images will not be generated. "
            "Example: To generate images, call generate_images_tool with the captions list. "
            "Respond with 'TERMINATE' when done."
        )
    )

    director = AssistantAgent(
        name="director",
        model_client=model_client,
        tools=[video_generation_tool],
        system_message=(
        """"
          You are only allowed to use the tool generate_video_tool.
          Do not attempt to generate videos yourself. 
          Always call the tool when asked to generate a video.
          Respond with 'TERMINATE' when done."""
     )
    )

    # Sequential execution setup
    builder = DiGraphBuilder()
    builder.add_node(script_writer)
    builder.add_node(voice_actor)
    builder.add_node(graphic_designer)
    builder.add_node(director)
    builder.add_edge(script_writer, voice_actor)
    builder.add_edge(voice_actor, graphic_designer)
    builder.add_edge(graphic_designer, director)
    graph = builder.build()

    team = GraphFlow(
        participants=[script_writer, voice_actor, graphic_designer, director],
        graph=graph,
        termination_condition=TextMentionTermination("TERMINATE"),
        max_turns=4
    )

    while True:
        user_input = input("Enter a message (type 'exit' to leave): ")
        if user_input.strip().lower() == "exit":
            break

        stream = team.run_stream(task=user_input)
        await Console(stream)

if __name__ == "__main__":
    asyncio.run(main())
