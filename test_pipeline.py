import asyncio
from tools import generate_voiceovers, generate_images, generate_video

stub_captions = [
    "Emerald shores, turquoise sea.",
    "Sun-drenched days, endless views.",
    "Tranquil sunsets, whispered secrets.",
    "Adventure awaits, nature's embrace.",
    "Island bliss. Your next escape."
]

# Generate voiceovers (will use existing files if present)
voiceover_paths = asyncio.run(generate_voiceovers(stub_captions))
print("Voiceovers:", voiceover_paths)

# Generate images (will use local images)
image_paths = generate_images(stub_captions)
print("Images:", image_paths)

# Generate video
generate_video(stub_captions)
print("Video generated as final_output.mp4")