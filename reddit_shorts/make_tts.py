import os
# import ssl # No longer needed if not using tiktok_tts which might have its own ssl context needs

# from dotenv import load_dotenv # Not needed for gTTS
from gtts import gTTS
import shutil # For ensuring temp directories exist

# from reddit_shorts.config import project_path # We'll use a passed-in temp_dir
# from reddit_shorts.tiktok_tts import tts # Replacing this
# from reddit_shorts.utils import tts_for_platform # Replacing this logic

# ssl._create_default_https_context = ssl._create_unverified_context # Likely not needed for gTTS

# load_dotenv() # Not needed
# tiktok_session_id = os.environ['TIKTOK_SESSION_ID_TTS'] # Not needed

# Import the tts function from the existing tiktok_tts module
# from reddit_shorts.tiktok_tts import tts as tiktok_tts_api

# Import from the new library copied into reddit_shorts/tiktok_voice
# The actual tts function and Voice enum are in tiktok_voice.src
from reddit_shorts.tiktok_voice.src.text_to_speech import tts as tiktok_library_tts
from reddit_shorts.tiktok_voice.src.voice import Voice

# Default voice mapping to the new library's enum
# Voice.US_FEMALE_2 maps to 'en_us_002'
DEFAULT_TIKTOK_VOICE_ENUM = Voice.US_FEMALE_2

def generate_gtts_for_story(title: str, text_content: str, story_id: str, temp_dir: str) -> dict:
    """
    Generates TTS audio for title and content using gTTS and saves them to the specified temp_dir.
    Returns a dictionary with paths to the generated TTS files.
    """
    if not title and not text_content:
        print("Error: Both title and text content are empty. Cannot generate TTS.")
        return {'title_tts_path': None, 'content_tts_path': None}

    # Ensure the specific temporary directory for this story's TTS exists
    # temp_dir is expected to be something like /path/to/project/temp/<story_id>/
    os.makedirs(temp_dir, exist_ok=True)

    title_tts_path = None
    content_tts_path = None
    lang = 'en' # Language for TTS

    try:
        # TTS for Title
        if title:
            title_tts_filename = f"title_{story_id}.mp3"
            title_tts_path = os.path.join(temp_dir, title_tts_filename)
            tts_obj = gTTS(text=title, lang=lang, slow=False)
            tts_obj.save(title_tts_path)
            print(f"Title TTS generated: {title_tts_path}")
        else:
            print("Title is empty, skipping title TTS generation.")

        # TTS for Content
        if text_content:
            # gTTS might have issues with very long texts in one go.
            # It's better to split if necessary, but for now, let's try direct.
            # Max length for gTTS is not strictly defined but practically, very long texts can fail or be slow.
            # Consider splitting text_content into chunks if issues arise.
            if len(text_content) > 4000: # Arbitrary limit, gTTS docs don't specify hard limit
                 print(f"Warning: Content text is very long ({len(text_content)} chars). TTS might be slow or fail.")
            
            content_tts_filename = f"content_{story_id}.mp3"
            content_tts_path = os.path.join(temp_dir, content_tts_filename)
            tts_obj = gTTS(text=text_content, lang=lang, slow=False)
            tts_obj.save(content_tts_path)
            print(f"Content TTS generated: {content_tts_path}")
        else:
            print("Content text is empty, skipping content TTS generation.")
            
    except Exception as e:
        print(f"Error during gTTS generation: {e}")
        # Return None for paths if an error occurs to prevent downstream issues
        # It's possible one succeeded and the other failed.
        if title_tts_path and not os.path.exists(title_tts_path):
             title_tts_path = None
        if content_tts_path and not os.path.exists(content_tts_path):
             content_tts_path = None
        # No need to return partial success, create_short can handle missing files by skipping them.

    return {
        'video_tts_path': title_tts_path,    # Matching key expected by create_short_video (originally narrator_title_track)
        'content_tts_path': content_tts_path # Matching key expected by create_short_video (originally narrator_content_track)
    }

def generate_tiktok_tts_for_story(title: str, text_content: str, story_id: str, temp_dir: str, **kwargs) -> dict:
    """
    Generates TTS audio for title and content using the mark-rez/TikTok-Voice-TTS library
    and saves them to the specified temp_dir.
    Accepts an optional 'voice' kwarg for the voice code (e.g., 'en_us_002').
    Returns a dictionary with paths to the generated TTS files.
    """
    generated_paths = {'video_tts_path': None, 'content_tts_path': None}
    selected_voice_code = kwargs.get('voice', None)
    
    active_voice_enum = DEFAULT_TIKTOK_VOICE_ENUM
    if selected_voice_code:
        try:
            # Attempt to get the Voice enum member by its value (the voice code string)
            active_voice_enum = Voice(selected_voice_code)
            print(f"Using selected voice: {selected_voice_code} ({active_voice_enum.name})")
        except ValueError:
            print(f"Warning: Invalid voice code '{selected_voice_code}' provided. Falling back to default voice {DEFAULT_TIKTOK_VOICE_ENUM.value}.")
            # active_voice_enum remains DEFAULT_TIKTOK_VOICE_ENUM

    if not title and not text_content:
        print("Error: Both title and text content are empty. Cannot generate TTS.")
        return generated_paths

    # Ensure the temporary directory for this story exists
    os.makedirs(temp_dir, exist_ok=True)
    
    # --- Generate TTS for Title ---
    if title:
        title_tts_filename = f"title_{story_id}.mp3"
        title_tts_path = os.path.join(temp_dir, title_tts_filename)
        print(f"Generating TikTok TTS for title using new library: {title[:50]}...")
        try:
            tiktok_library_tts(
                text=title,
                voice=active_voice_enum,
                output_file_path=title_tts_path,
                play_sound=False
            )
            if os.path.exists(title_tts_path) and os.path.getsize(title_tts_path) > 0:
                generated_paths['video_tts_path'] = title_tts_path
                print(f"Title TTS successfully generated: {title_tts_path}")
            else:
                print(f"Error: Title TTS file not generated or empty by new library. Path: {title_tts_path}")
        except Exception as e:
            print(f"Error during title TTS generation with new library: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Title is empty, skipping title TTS generation.")

    # --- Generate TTS for Content ---
    if text_content:
        content_tts_filename = f"content_{story_id}.mp3"
        content_tts_path = os.path.join(temp_dir, content_tts_filename)
        print(f"Generating TikTok TTS for content using new library (first 50 chars): {text_content[:50]}...")
        try:
            # For content, the library handles splitting long text internally
            tiktok_library_tts(
                text=text_content,
                voice=active_voice_enum,
                output_file_path=content_tts_path,
                play_sound=False
            )
            if os.path.exists(content_tts_path) and os.path.getsize(content_tts_path) > 0:
                generated_paths['content_tts_path'] = content_tts_path
                print(f"Content TTS successfully generated: {content_tts_path}")
            else:
                print(f"Error: Content TTS file not generated or empty by new library. Path: {content_tts_path}")
        except Exception as e:
            print(f"Error during content TTS generation with new library: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Text content is empty, skipping content TTS generation.")

    return generated_paths

# Example usage (for testing this file directly)
if __name__ == '__main__':
    print("Testing gTTS generation...")
    # Create a dummy temp directory for testing
    test_story_id = "test_gtts_001"
    # project_root_for_test = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    # test_temp_dir = os.path.join(project_root_for_test, "temp", test_story_id, "tts")
    
    # Simpler temp dir for direct script test relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_temp_root = os.path.join(script_dir, "..", "temp") # e.g., project_root/temp/
    test_temp_story_dir = os.path.join(test_temp_root, test_story_id) # e.g., project_root/temp/test_gtts_001/
    
    # Ensure base temp directory exists (temp/)
    # os.makedirs(os.path.dirname(test_temp_dir), exist_ok=True)
    # os.makedirs(test_temp_dir, exist_ok=True)
    # This generate_gtts_for_story will create the final subdir if needed

    print(f"TTS files will be saved in a subdirectory of: {test_temp_story_dir}")

    sample_title = "Hello World from gTTS"
    sample_content = "This is a test of the Google Text-to-Speech library. It should generate an MP3 file with this text spoken."
    
    tts_paths = generate_gtts_for_story(sample_title, sample_content, test_story_id, test_temp_story_dir)
    
    if tts_paths.get('video_tts_path') and os.path.exists(tts_paths['video_tts_path']):
        print(f"Title TTS successfully created at: {tts_paths['video_tts_path']}")
    else:
        print("Title TTS creation failed or file not found.")

    if tts_paths.get('content_tts_path') and os.path.exists(tts_paths['content_tts_path']):
        print(f"Content TTS successfully created at: {tts_paths['content_tts_path']}")
    else:
        print("Content TTS creation failed or file not found.")

    # Clean up dummy test directory if you want
    # if os.path.exists(test_temp_dir):
    #     shutil.rmtree(test_temp_dir)
    #     print(f"Cleaned up test directory: {test_temp_dir}")
    # if os.path.exists(os.path.dirname(test_temp_dir)) and not os.listdir(os.path.dirname(test_temp_dir)):
    #     os.rmdir(os.path.dirname(test_temp_dir))
    # if os.path.exists(os.path.dirname(os.path.dirname(test_temp_dir))) and not os.listdir(os.path.dirname(os.path.dirname(test_temp_dir))):
    #     os.rmdir(os.path.dirname(os.path.dirname(test_temp_dir))) # clean up temp/ if empty
    print(f"If successful, check the subdirectory within {test_temp_story_dir} for MP3 files.")

    print("Testing new generate_tiktok_tts_for_story function...")
    
    # Create a dummy temp directory for testing
    test_story_id = "test_story_001"
    test_temp_dir_base = "temp" # Assuming script is run from project root where 'temp' would be
    test_temp_dir_story = os.path.join(test_temp_dir_base, test_story_id, "tts_test_output") # More specific path
    
    # Ensure the base temp directory exists for the test
    if not os.path.exists(test_temp_dir_base):
        os.makedirs(test_temp_dir_base)
    if not os.path.exists(os.path.join(test_temp_dir_base, test_story_id)):
         os.makedirs(os.path.join(test_temp_dir_base, test_story_id))


    print(f"Test temporary directory will be: {test_temp_dir_story}")
    # Clean up previous test directory if it exists
    if os.path.exists(test_temp_dir_story):
        shutil.rmtree(test_temp_dir_story)
    os.makedirs(test_temp_dir_story, exist_ok=True)

    sample_title = "Hello World from New Library"
    sample_content = "This is a test of the newly integrated TikTok TTS library. It should handle this text and save it as an MP3 audio file."

    results = generate_tiktok_tts_for_story(
        title=sample_title,
        text_content=sample_content,
        story_id=test_story_id,
        temp_dir=test_temp_dir_story
    )

    print("\n--- Test Results ---")
    if results.get('video_tts_path') and os.path.exists(results['video_tts_path']):
        print(f"Title TTS Path: {results['video_tts_path']} (Exists: True, Size: {os.path.getsize(results['video_tts_path'])})")
    else:
        print(f"Title TTS generation FAILED. Path: {results.get('video_tts_path')}")

    if results.get('content_tts_path') and os.path.exists(results['content_tts_path']):
        print(f"Content TTS Path: {results['content_tts_path']} (Exists: True, Size: {os.path.getsize(results['content_tts_path'])})")
    else:
        print(f"Content TTS generation FAILED. Path: {results.get('content_tts_path')}")

    # Suggest cleanup
    print(f"\nTest files were saved in: {test_temp_dir_story}")
    print("You may want to manually delete this directory after inspection.")
    # For automated cleanup, you could add:
    # if os.path.exists(test_temp_dir_story):
    #     shutil.rmtree(test_temp_dir_story)
    #     print(f"Cleaned up test directory: {test_temp_dir_story}")
