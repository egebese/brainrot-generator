import argparse
import os
import ssl

from reddit_shorts.config import (
    project_path,
    stories_file_path, 
    output_video_path,
    # TIKTOK_SESSION_ID_TTS # No longer needed by the new library
)
from reddit_shorts.get_reddit_stories import get_story_from_file
from reddit_shorts.make_submission_image import generate_reddit_story_image
from reddit_shorts.make_tts import generate_tiktok_tts_for_story # Uses the new library
from reddit_shorts.create_short import create_short_video

ssl._create_default_https_context = ssl._create_unverified_context

def run_local_video_generation(**kwargs) -> str | None:
    """Generates a video locally from a story file."""
    print("Starting local video generation process...")
    submission_data = get_story_from_file(**kwargs)

    if not submission_data:
        print("No story data received. Aborting video generation.")
        return None

    story_id = submission_data.get('id', "default_story_id")
    story_title = submission_data.get('title', "")
    story_selftext = submission_data.get('selftext', "")
    print(f"Processing story ID: {story_id}, Title: {story_title}")

    current_story_temp_dir = os.path.join(project_path, "temp", story_id)
    os.makedirs(current_story_temp_dir, exist_ok=True)

    print("Generating TTS audio for story...")
    tts_paths = generate_tiktok_tts_for_story(
        title=story_title,
        text_content=story_selftext,
        story_id=story_id,
        temp_dir=current_story_temp_dir,
        **kwargs # Pass through kwargs which should include the 'voice' parameter
    )

    video_tts_path = tts_paths.get('video_tts_path')

    if not video_tts_path:
        print("TTS generation failed for video. Video might lack narration.")

    try:
        print("Generating story image...")
        image_generation_data = {**submission_data, 'subreddit': submission_data.get('music_type', 'local_story')}
        generate_reddit_story_image(**{**image_generation_data, **kwargs})
        print("Story image generated.")
    except Exception as e:
        print(f"Error generating story image: {e}. Continuing without image specific to story text, or this step might need review.")

    print("Creating short video...")
    try:
        short_file_path = create_short_video(
            **tts_paths, 
            **submission_data, 
            **kwargs, 
            output_dir=output_video_path
        )
        if short_file_path and os.path.exists(short_file_path):
            print(f"Successfully created video: {short_file_path}")
            return short_file_path
        else:
            print(f"Video creation failed or file not found. Path returned: {short_file_path}")
            return None
    except Exception as e:
        print(f"Error during video creation: {e}")
        import traceback
        traceback.print_exc()
        return None

def main(**kwargs) -> None:
    # Simplified main function to only generate video locally
    print(f"Received arguments for main: {kwargs}")
    
    # db_path = f'{project_path}/reddit-shorts/shorts.db' # DB not used
    # if not os.path.isfile(db_path):
    #     create_tables()

    # No platform switching, just run the local generation
    video_file = run_local_video_generation(**kwargs)

    if video_file:
        print(f"Video generation complete. File saved at: {video_file}")
    else:
        print("Video generation failed.")
    
    # No uploading, no deleting of the local file


def parse_my_args() -> dict:
    parser = argparse.ArgumentParser(description="Generate a short video from a local story file.")
    # Removed platform argument
    # parser.add_argument("-p", "--platform", choices=VALID_PLATFORM_CHOICES, default=VALID_PLATFORM_CHOICES[3], help="Choose what platform to upload to:")
    # parser.add_argument("-i", "--input", type=str.lower, action='store', default=False, help="Input your own text")
    # parser.add_argument("-v", "--video", type=str.lower, action='store', default=False, help="Input your own video path")
    # parser.add_argument("-m", "--music", type=str.lower, action='store', default=False, help="Input your own music") 
    parser.add_argument("-pf", "--filter", action="store_true", default=False, help="Enable profanity filter for stories.")

    args = parser.parse_args()

    # platform = args.platform # No longer used
    profanity_filter = args.filter

    return {
        # 'platform': platform, # No longer used
        'filter': profanity_filter,
        # Add other relevant args if create_short_video or other functions need them explicitly
    }


def run() -> None:
    args = parse_my_args()
    main(**args)


if __name__ == '__main__':
    run()
