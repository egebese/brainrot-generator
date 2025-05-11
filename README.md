https://github.com/gavink97/reddit-shorts-generator/assets/78187175/d244555b-235b-4897-8c70-7009c6ba45ea

<h1 align="center">Reddit Shorts Generator</h1>
<p align="center" style="font-size: large;">Generate Short-form media from UGC
content from the worst website on the internet</p> <br>

## Table of contents
- [Why](#why-this-project)
- [Features](#features)
- [Installation](#installation)
    - [Optional](#optional)
- [Quick Start](#getting-started)
- [Customization](#making-it-your-own)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [Star History](#star-history)


## Why this project
I started this project after being inspired by this
[video](https://youtu.be/_BsgckzDeRI?si=p18GIlR5urz-Pues).

It was mid December and I had just gotten absolutely crushed
in my first technical interview, so I wanted to build
something simple to regain confidence.


## Features
- Create Short-form media from UGC content from the worst website on the
  internet.
- Upload videos directly to YouTube via the [YouTube
  API](https://developers.google.com/youtube/v3).
- Automatically generate captions for your videos using Open AI
  [Whisper](https://github.com/openai/whisper).
- Videos are highly customizable and render blazingly fast with FFMPEG.
- Utilizes SQLite to avoid creating duplicate content.


## Installation
Reddit Shorts can run independently but if you want to upload shorts
automatically to YouTube or TikTok you must install the [TikTok
Uploader](https://github.com/wkaisertexas/tiktok-uploader) and set up the
[YouTube Data API](https://developers.google.com/youtube/v3) respectively.

Additionally, install the reddit shorts repo in the root directory of the
project as shown in the file tree.

### File tree

```
├── client_secrets.json
├── cookies.txt
├── [reddit-shorts]
├── resources
│   ├── footage
│   └── music
├── tiktok-uploader
├── tiktok_tts.txt
└── youtube_tts.txt
```

### Optional
- [TikTok Uploader](https://github.com/wkaisertexas/tiktok-uploader) is required to upload shorts to TikTok.
- [YouTube Data API](https://developers.google.com/youtube/v3) is required to upload shorts to YouTube.

### Build source
Because OpenAi's [Whisper](https://github.com/openai/whisper) is only compatible
with Python 3.8 - 3.11 only use those versions of python.

```
mkdir reddit-shorts
gh repo clone gavink97/reddit-shorts-generator reddit-shorts
pip install -e reddit-shorts
```

### Install dependencies
This package requires `ffmpeg fonts-liberation` to be installed.

*This repository utilizes pillow to create reddit images, so make sure to
uninstall PIL if you have it installed*

### Config
If your music / footage directory is different from the file tree configure the
path inside `config.py`.

If you are creating videos for TikTok or YouTube and wish to have some custom
tts at the end of the video, make sure you
create `tiktok_tts.txt` or `youtube_tts.txt`.


## Getting Started
`shorts` is the command line interface for the project. 

Simply run `shorts -p platform` to generate a youtube short and automatically
upload it.

`shorts -p youtube`

*it should be noted that the only supported platform is youtube at
the moment*


## Making it your own
Customize your shorts with FFMPG inside `create_short.py`.


## Contributing
All contributions are welcome!

## Roadmap

- [ ] Standalone video exports
- [ ] TikTok Support

## Star History
<a href="https://star-history.com/#gavink97/reddit-shorts-generator&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=gavink97/reddit-shorts-generator&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=gavink97/reddit-shorts-generator&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=gavink97/reddit-shorts-generator&type=Date" />
 </picture>
</a>

# TikTok Brainrot Generator

This project generates engaging short videos from locally provided text stories. It combines these stories with background videos, music, TikTok-style Text-to-Speech (TTS) narration, and a customizable title image overlay. The final videos are saved directly to your local machine.

Created by [egebese](https://x.com/egebese).

**Acknowledgements:** This project is a significantly modified version of the original [reddit-shorts-generator by gavink97](https://github.com/gavink97/reddit-shorts-generator.git). While the core functionality has been adapted for local use with different TTS and story input methods, much of the foundational video processing logic and project structure is derived from this original work.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=egebese/tiktok-brainrot-generator&type=Date)](https://star-history.com/#egebese/tiktok-brainrot-generator&Date)

## Key Features

*   **Local Story Input:** Reads stories directly from a `stories.txt` file in the project root.
*   **Local Video Output:** Saves generated videos to the `generated_shorts/` directory.
*   **TikTok TTS Narration:** Utilizes the [mark-rez/TikTok-Voice-TTS](https://github.com/mark-rez/TikTok-Voice-TTS) library for dynamic and natural-sounding text-to-speech. This library leverages public APIs and does not require direct user management of TikTok session IDs.
*   **Customizable Aesthetics:**
    *   **Fonts:** Uses "Montserrat ExtraBold" for the title image text and video subtitles by default.
    *   **Background Video Looping:** Background videos will loop if their duration is shorter than the narration.
    *   **Custom Title Image:** Allows for a user-provided template (`resources/images/reddit_submission_template.png`) where the story title is overlaid.
*   **Platform Independent:** Core functionality does not rely on direct integration with external platforms like Reddit or YouTube APIs for content fetching or uploading.

## Setup and Installation

### Prerequisites

1.  **Python:** Python 3.11+ is recommended. You can use tools like `pyenv` to manage Python versions.
    ```bash
    # Example using pyenv (if you have it installed)
    # pyenv install 3.11.9
    # pyenv local 3.11.9 
    ```
2.  **FFmpeg:** Essential for video processing. It must be installed on your system and accessible via your system's PATH.
    *   **macOS (using Homebrew):** `brew install ffmpeg`
    *   **Linux (using apt):** `sudo apt update && sudo apt install ffmpeg`
    *   **Windows:** Download from the [FFmpeg website](https://ffmpeg.org/download.html) and add the `bin` directory to your PATH.
3.  **Fonts:**
    *   **Montserrat ExtraBold:** Used for title images and subtitles. Ensure this font is installed on your system. You can typically find and install `.ttf` or `.otf` files. If the font is not found by its name, you may need to modify the font paths/names directly in `reddit_shorts/make_submission_image.py` and `reddit_shorts/create_short.py`.
    *   **Liberation Fonts (Optional):** If you adapt old templates or resources that might have used them, having these might be useful. They can be found on [GitHub](https://github.com/liberationfonts/liberation-fonts).

### Installation Steps

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/egebese/tiktok-brainrot-generator.git
    cd tiktok-brainrot-generator
    ```

2.  **Create and Activate a Python Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -e .
    ```
    The `-e .` makes an editable install, good for development.

## Project Structure & Required Assets

Before running, ensure the following files and directories are set up:

*   **`stories.txt`**: (Create this file in the project root)
    *   This file contains the stories to be converted into videos.
    *   **Format:** Each story should have a title and the story body, formatted as follows:
        ```
        Title: [Your Story Title Here]
        Story:
        [First paragraph of your story]
        [Second paragraph of your story]
        ...
        ```
        Separate multiple stories with at least one blank line.

*   **`resources/footage/`**:
    *   Place your background MP4 video files in this directory. The script will randomly select one for each short.

*   **`resources/music/`**:
    *   Place your background music files (MP3, WAV, OGG) here. Music is chosen based on keywords ("creepy", "storytime", or "general") inferred from the story title/content, or a general track is used.

*   **`resources/images/reddit_submission_template.png`**:
    *   This is your custom background image for the title screen overlay. The story title will be drawn onto this image.
    *   The current title placement is configured in `reddit_shorts/make_submission_image.py` for specific coordinates. You may need to adjust these if you change the template significantly.

*   **`generated_shorts/`**:
    *   This directory will be created automatically if it doesn't exist. All generated videos will be saved here.

*   **`reddit_shorts/`**: Main Python package containing the application logic.
    *   `config.py`: Contains paths to resources, bad words list, and other configurations.
    *   `main.py`: The main script to execute for video generation.
    *   `make_tts.py`: Handles Text-to-Speech using the integrated TikTok TTS library.
    *   `create_short.py`: Manages the FFmpeg video assembly process.
    *   `make_submission_image.py`: Generates the title image overlay.
    *   `get_reddit_stories.py`: Modified to parse stories from `stories.txt`.
    *   `tiktok_voice/`: The integrated [mark-rez/TikTok-Voice-TTS](https://github.com/mark-rez/TikTok-Voice-TTS) library.

## Usage

1.  **Prepare Stories:** Populate `stories.txt` with the content you want to turn into videos, following the format described above.
2.  **Add Assets:**
    *   Add your MP4 background videos to the `resources/footage/` directory.
    *   Add your MP3/WAV/OGG music files to the `resources/music/` directory.
    *   Ensure your `resources/images/reddit_submission_template.png` is in place.
3.  **Run the Video Generator:**
    Open your terminal, navigate to the project's root directory, ensure your virtual environment is activated, and run:
    ```bash
    brainrot-gen 
    ```
    (This uses the new console script name defined in `setup.cfg`). Alternatively, you can still use:
    ```bash
    python -m reddit_shorts.main
    ```
4.  **Optional Arguments:**
    *   `--filter`: Enables a basic profanity filter for story text (bad words are defined in `reddit_shorts/config.py`).
        ```bash
        brainrot-gen --filter
        # or
        # python -m reddit_shorts.main --filter
        ```

Generated videos will appear in the `generated_shorts/` directory.

## Customization

*   **Paths & Filters:** Modify `reddit_shorts/config.py` to change resource paths or update the `bad_words_list`.
*   **Fonts & Styles:**
    *   **Title Image Font:** The font and size for the title drawn on `reddit_submission_template.png` can be changed in `reddit_shorts/make_submission_image.py` (look for `font_name` and `title_font_size`).
    *   **Subtitle Style:** The appearance of video subtitles (font, size, color, shadow, etc.) is controlled by an FFmpeg filter style string within `reddit_shorts/create_short.py`. Search for `force_style=` in the `ffmpeg.filter('subtitles', ...)` section.
*   **Title Image Layout:** If you use a different `reddit_submission_template.png`, you'll likely need to adjust the title drawing coordinates (e.g., `offset_left`, `offset_top`, etc.) in `reddit_shorts/make_submission_image.py`.
*   **Default TTS Voice:** The default TikTok voice is set in `reddit_shorts/make_tts.py` via `DEFAULT_TIKTOK_VOICE_ENUM`. You can change this by selecting a different voice from `reddit_shorts/tiktok_voice/src/voice.py`.

## Troubleshooting

*   **Font Not Found Errors:**
    *   Ensure the specified fonts (e.g., "Montserrat ExtraBold") are correctly installed on your system and accessible by name.
    *   If Pillow (the imaging library) cannot find the font by name, you may need to provide an absolute path to the `.ttf` or `.otf` font file in the code (`make_submission_image.py` for title, `create_short.py` for subtitles if using a system font there, though subtitles use FFmpeg's font finding).
*   **FFmpeg Errors / "FFmpeg not found":**
    *   Verify that FFmpeg is installed correctly.
    *   Confirm that the directory containing the `ffmpeg` executable is in your system's PATH environment variable.
*   **TTS Failures:**
    *   The integrated TikTok TTS library relies on publicly accessible API endpoints. If these services are temporarily down or change, TTS generation might fail. Check your internet connection.
    *   The library attempts to fall back to alternative endpoints if one fails.
*   **`playsound` Warning on macOS:**
    *   You might see: `playsound is relying on a python 2 subprocess...`
    *   Installing `PyObjC` can sometimes resolve this or make it more efficient: `pip3 install PyObjC`. (This is generally for when `playsound` is used directly for playback, which isn't part of the main video generation flow but might be used in test scripts).
*   **ModuleNotFoundError for `reddit_shorts.tiktok_voice...`:**
    *   Ensure the `tiktok_voice` directory was correctly copied into the `reddit_shorts` directory and that your Python environment can see it (which `pip install -e .` should handle).

## License

This project is publicly available and free to use, modify, and distribute under the terms of the MIT License. See the `LICENSE` file for more details.

---

*This project builds upon the foundational structure and concepts from the [Reddit Shorts Generator by gavink97](https://github.com/gavink97/reddit-shorts-generator.git).*
