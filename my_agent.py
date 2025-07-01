from elevenlab_test import generate_video_tool

stub_captions = [
    "Emerald waters, sun-kissed sands.",
    "Adventure awaits on this tropical isle.",
    "Relax, rejuvenate, reconnect.",
    "Discover hidden beaches, vibrant life.",
    "Your island escape is now."
]

result = generate_video_tool(stub_captions)
print(result)