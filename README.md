# 🎬 Multi-Agent YouTube Shorts Video Generator

This project is an end-to-end, multi-agent framework for automatically generating YouTube Shorts using [Microsoft AutoGen](https://github.com/microsoft/autogen). The system orchestrates multiple specialized AI agents—**Script Writer**, **Voice Actor**, **Graphic Designer**, and **Director**—to collaboratively create engaging short-form videos from a single user prompt.

---

## 🚀 Features

- **Script Writer Agent**: Generates a compelling script and 5 short captions for the video.
- **Voice Actor Agent**: Produces voiceovers for each caption using [ElevenLabs API](https://www.elevenlabs.io/) or local stubs (to save API credits).
- **Graphic Designer Agent**: Generates or selects images using [Stability AI](https://stability.ai/) or stubbed local images.
- **Director Agent**: Assembles voiceovers, images, and captions into a final video using [MoviePy](https://zulko.github.io/moviepy/).
- **Stub Mode**: Supports development without making real API calls (local files for audio and images).
- **Fully Automated Pipeline**: Enter a topic and receive a ready-to-upload YouTube Shorts video.

---

## 🛠 Tech Stack

- Python
- [Microsoft AutoGen](https://github.com/microsoft/autogen)
- [MoviePy](https://zulko.github.io/moviepy/)
- [ElevenLabs API](https://www.elevenlabs.io/)
- [Stability AI API](https://platform.stability.ai/)

---

## ⚙️ How It Works

1. **User Input**: Provide a topic or idea for the short video.
2. **Script Generation**: Script writer agent creates a narrative and captions.
3. **Voiceover Generation**: Voice actor agent generates or stubs audio files.
4. **Image Generation**: Graphic designer agent fetches or generates relevant images.
5. **Video Assembly**: Director agent stitches everything into a complete video using MoviePy.
6. **Output**: Final video is saved as `final_output.mp4`.

---

## 🧪 Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Josmin123/Mutli-agent-system.git
cd Mutli-agent-system
