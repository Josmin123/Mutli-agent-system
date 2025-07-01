from dotenv import load_dotenv
import asyncio
import os
import requests
from autogen_core.tools import FunctionTool
from typing_extensions import Annotated
import asyncio
from autogen_core import CancellationToken

load_dotenv()

print("API Key loaded:", os.getenv("STABILITY_API_KEY"))

stability_api_key = os.getenv("STABILITY_API_KEY")

def generate_images(prompts: list[str]):
    """
    Generate images based on text prompts using Stability AI API.
    
    Args:
        prompts: List of text prompts to generate images from
    """
    seed = 42
    output_dir = "images"
    os.makedirs(output_dir, exist_ok=True)

    # API config
    stability_api_url = "https://api.stability.ai/v2beta/stable-image/generate/core"
    headers = {
        "Authorization": f"Bearer {stability_api_key}",
        "Accept": "image/*"
    }

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



def generate_images_tool(
    captions: Annotated[list[str], "List of short captions to convert into images"]
) -> dict:
    prompts = [f"{caption} in Abstract Art Style / Ultra High Quality." for caption in captions]
    generate_images(prompts)
    return {"image_paths": [f"images/image_{i+1}.webp" for i in range(len(prompts))]}

image_generation_tool = FunctionTool(
    generate_images_tool,
    name="generate_images_tool",
    description="Generate images from a list of captions using Stability AI."
)                

async def test_image_generation():
    result = await image_generation_tool.run_json({
        "captions": [
            "Unlock the mystery",
            "The clock is ticking",
            "Every clue matters",
            "Truth is stranger than fiction",
            "It all comes down to this"
        ]
    }, CancellationToken())
    
    print("Generated image paths:", result)

if __name__ == "__main__":
    asyncio.run(test_image_generation())