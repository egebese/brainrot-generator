# TikTok Brainrot Generator

This project generates engaging short videos from text stories. It features a web-based UI for easy video creation, allowing users to input stories, select background videos, choose background music, and pick from a variety of TikTok-style Text-to-Speech (TTS) voices. The final videos are saved directly to your local machine.

Created by [egebese](https://x.com/egebese).

**Acknowledgements:** This project is a significantly modified version of the original [reddit-shorts-generator by gavink97](https://github.com/gavink97/reddit-shorts-generator.git). While the core functionality has been adapted for local use with different TTS and story input methods, and now includes a Web UI, much of the foundational video processing logic and project structure is derived from this original work.

## Key Features

*   **Web-Based User Interface:** Easily create videos through a user-friendly web page.
*   **Flexible Input:**
    *   Enter story titles and content directly in the UI.
    *   Select background videos from your `resources/footage/` directory, with thumbnail previews.
    *   Choose background music from your `resources/music/` directory, with audio previews.
    *   Select from a wide range of TikTok TTS voices.
*   **Local Video Output:** Saves generated videos to the `generated_shorts/` directory.
*   **TikTok TTS Narration:** Utilizes the [mark-rez/TikTok-Voice-TTS](https://github.com/mark-rez/TikTok-Voice-TTS) library for dynamic and natural-sounding text-to-speech.
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

### Installation Steps

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/egebese/tiktok-brainrot-generator.git # Or your fork
    cd tiktok-brainrot-generator
    ```

2.  **Create and Activate a Python Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    If you intend to modify the core `reddit_shorts` package itself and want those changes reflected immediately (developer install):
    ```bash
    pip install -e .
    ```

## Project Structure & Required Assets

Before running, ensure the following files and directories are set up:

*   **`resources/footage/`**:
    *   Place your background MP4 video files in this directory. These will be available for selection in the Web UI. Thumbnails will be automatically generated and cached in `web_ui/static/thumbnails/`.
*   **`resources/music/`**:
    *   Place your background music files (MP3, WAV, OGG) here. These will be available for selection in the Web UI. For preview functionality, ensure assets are accessible (e.g., copied to `web_ui/static/music_assets/` by the application or during setup).
*   **`resources/images/reddit_submission_template.png`**:
    *   This is your custom background image for the title screen overlay. The story title will be drawn onto this image.
    *   The current title placement is configured in `reddit_shorts/make_submission_image.py`. You may need to adjust these if you change the template significantly.
*   **`generated_shorts/`**:
    *   This directory will be created automatically if it doesn't exist. All videos generated via the Web UI will be saved here.
*   **`web_ui/`**: Contains the Flask web application.
    *   `static/`: Holds static assets for the UI (HTML, CSS, JS, and initially empty `thumbnails` and `music_assets` folders).
    *   `routes.py`: Defines the API endpoints and serves the UI.
    *   `__init__.py`: Initializes the Flask app.
*   **`run_web.py`**: Script to start the Flask development server for the Web UI.
*   **`reddit_shorts/`**: Main Python package containing the video generation logic.
    *   `config.py`: Contains paths to resources, bad words list, and other configurations.
    *   `main.py`: Core logic for video generation, called by the Web UI.
    *   `make_tts.py`: Handles Text-to-Speech using the integrated TikTok TTS library.
    *   `create_short.py`: Manages the FFmpeg video assembly process.
    *   `make_submission_image.py`: Generates the title image overlay.
    *   `tiktok_voice/`: The integrated [mark-rez/TikTok-Voice-TTS](https://github.com/mark-rez/TikTok-Voice-TTS) library.
*   **`requirements.txt`**: Lists Python dependencies for the project, including Flask for the Web UI.

## Usage

### Running the Web UI

1.  **Prepare Assets:**
    *   Add your MP4 background videos to the `resources/footage/` directory.
    *   Add your MP3/WAV/OGG music files to the `resources/music/` directory. (The UI will copy `music.mp3` to `web_ui/static/music_assets/` for preview if it exists at the expected location).
    *   Ensure your `resources/images/reddit_submission_template.png` is in place.
2.  **Start the Flask Server:**
    Open your terminal, navigate to the project's root directory, ensure your virtual environment is activated, and run:
    ```bash
    python run_web.py
    ```
3.  **Access the UI:**
    Open your web browser and go to `http://127.0.0.1:5001` (or the port specified in the terminal output).
4.  **Generate Videos:**
    *   Fill in the "Title" and "Story" fields.
    *   Select a background video from the displayed thumbnails.
    *   Select background music and preview it.
    *   Choose a TTS voice from the paginated table.
    *   Click "Generate Video". The video will be processed and then downloaded by your browser. It will also be saved in the `generated_shorts/` directory.

### (Alternative) Original CLI Usage (Limited Functionality)

The project previously supported a CLI-based generation using `stories.txt`. While the Web UI is now the primary method, the underlying CLI entry point `brainrot-gen` (or `python -m reddit_shorts.main`) might still work for basic generation if `stories.txt` is populated, but it will not use the UI's selection features for voice, specific background video, or music.

For CLI usage with `stories.txt`:
1.  **Prepare `stories.txt`**: (Create this file in the project root if using CLI)
    *   Format: Each story should have a title and the story body:
        ```
        Title: [Your Story Title Here]
        Story:
        [First paragraph of your story]
        ...
        ```
        Separate multiple stories with at least one blank line.
2.  **Run:**
    ```bash
    brainrot-gen
    # or
    # python -m reddit_shorts.main
    ```
    *   `--filter`: Enables a basic profanity filter.

## Customization

*   **Video Editing Logic:** Modify `reddit_shorts/create_short.py` to change FFmpeg parameters, subtitle styles, or video composition.
*   **Title Image Generation:** Adjust title placement, font, or text wrapping in `reddit_shorts/make_submission_image.py`.
*   **TTS Voice Management:** Voices are sourced from the `tiktok_voice` library and managed in `web_ui/routes.py` for the UI.
*   **Configuration:** Edit `reddit_shorts/config.py` for resource paths, etc.
*   **Web UI Frontend:** Modify `web_ui/static/index.html` for UI layout, styling (Tailwind CSS), and Vue.js app logic.
*   **Web UI Backend:** Modify `web_ui/routes.py` for API endpoint behavior.

## Troubleshooting

*   **`ModuleNotFoundError: No module named 'flask'` (or other dependencies):** Ensure you've installed dependencies using `pip install -r requirements.txt`.
*   **`Address already in use` for port 5001:** Another application is using the port. You can change the port in `run_web.py`.
*   **404 Errors in UI / API calls not working:** Check terminal logs from `python run_web.py` for errors. Ensure Flask routes are correctly defined.
*   **`ffmpeg: command not found`**: Ensure FFmpeg is installed and in your system's PATH.
*   **Font errors (e.g., "Font not found")**: Make sure "Montserrat ExtraBold" (or your chosen font) is installed correctly.
*   **TTS Issues**:
    *   Check your internet connection.
    *   The underlying API used by the TTS library can sometimes be unreliable.
    *   Look for error messages in the console output from `python run_web.py`.
*   **No videos generated / Video generation fails**:
    *   Check `resources/footage/` has at least one `.mp4` file.
    *   Check `resources/music/` has music files.
    *   Ensure `resources/images/reddit_submission_template.png` exists.
    *   Examine console output from `python run_web.py` for detailed FFmpeg or Python errors during generation.

## Acknowledgements

*   This project is a heavily modified fork of [gavink97/reddit-shorts-generator](https://github.com/gavink97/reddit-shorts-generator).
*   Uses the [mark-rez/TikTok-Voice-TTS](https://github.com/mark-rez/TikTok-Voice-TTS) library.
*   Web UI uses Vue.js and Tailwind CSS.

## License

This project is currently unlicensed, inheriting the original [MIT License](https://github.com/gavink97/reddit-shorts-generator/blob/main/LICENSE) from the upstream repository where applicable to original code sections. New modifications by egebese are also effectively under MIT-style permissions unless otherwise specified.

---

*This project builds upon the foundational structure and concepts from the [Reddit Shorts Generator by gavink97](https://github.com/gavink97/reddit-shorts-generator.git).*

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=egebese/brainrot-generator&type=Date)](https://www.star-history.com/#egebese/brainrot-generator&Date)