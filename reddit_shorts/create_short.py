import os
import whisper
import math
import random
import ffmpeg
import shutil # For cleaning up temp directories

from whisper.utils import get_writer

# project_path is derived in config.py and used for temp paths if not overridden
from reddit_shorts.config import project_path as default_project_path, footage, music, output_video_path as global_output_video_path
from reddit_shorts.utils import random_choice_music


def get_audio_duration(track: str) -> float: # Changed to accept path directly
    if not track or not os.path.exists(track):
        # print(f"Warning: Audio track {track} not found or is None. Returning 0 duration.")
        return 0.0
    try:
        probe = ffmpeg.probe(track)
        audio_info = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
        duration = float(audio_info['duration'])
        return duration
    except Exception as e:
        print(f"Error probing audio duration for {track}: {e}")
        return 0.0


def get_video_duration(track: str) -> float: # Changed to accept path directly
    if not track or not os.path.exists(track):
        print(f"Warning: Video track {track} not found. Returning 0 duration.")
        return 0.0
    try:
        probe = ffmpeg.probe(track)
        video_info = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
        duration = float(video_info['duration'])
        return duration
    except Exception as e:
        print(f"Error probing video duration for {track}: {e}")
        return 0.0


def create_short_video(**kwargs) -> str | None:
    story_id = kwargs.get('id')
    story_title = kwargs.get('title') # Expecting title from submission_data
    # submission_text = kwargs.get('selftext') # Now passed as narrator_content_track audio
    subreddit_music_type = kwargs.get('music_type', 'general') # Default to general
    
    # TTS tracks for title and content - provided by a preceding step (e.g. modified make_tts.py)
    narrator_title_track_path = kwargs.get('video_tts_path') # Path to title TTS audio file
    narrator_content_track_path = kwargs.get('content_tts_path') # Path to content (selftext) TTS audio file

    # Commentor and platform TTS are removed as per our simplification
    # commentor_track_path = kwargs.get('commentor_track')
    # platform_tts_track_path = kwargs.get('platform_track')

    output_dir = kwargs.get('output_dir', global_output_video_path) # Get from kwargs or global config
    os.makedirs(output_dir, exist_ok=True)

    # Define a temporary directory for this specific video's processing files
    # This helps in organization and cleanup.
    # Use default_project_path (imported from config) for the root of temp, or make it relative to output_dir
    temp_processing_dir = os.path.join(default_project_path, "temp", story_id if story_id else "temp_video")
    os.makedirs(temp_processing_dir, exist_ok=True)
    
    # submission_image path needs to use story_id (or title if id is not reliable yet from image gen)
    # Assuming make_submission_image.py saves based on ID now.
    submission_image_filename = f"{story_id}.png" if story_id else "story_image.png"
    submission_image_path = os.path.join(default_project_path, "temp", "images", submission_image_filename)
    
    short_file_path = os.path.join(output_dir, f"{story_id if story_id else 'short'}.mp4")
    tts_combined_path = os.path.join(temp_processing_dir, "combined.mp3")
    music_looped_path = os.path.join(temp_processing_dir, "music_looped.mp3")
    processed_music_path = os.path.join(temp_processing_dir, "music_processed.mp3")
    mixed_audio_file_path = os.path.join(temp_processing_dir, 'mixed_audio.mp3')
    # srt_filename = f"{story_id if story_id else 'combined'}.srt"
    # tts_combined_srt_path = os.path.join(temp_processing_dir, srt_filename)
    # Using a fixed name for SRT within its temp dir for Whisper, will be specific to this run.
    tts_combined_srt_path = os.path.join(temp_processing_dir, "subtitles.srt") 

    if not footage:
        print("Error: No background footage available. Please check config and resources directory.")
        return None
    random_video_path = random.choice(footage)

    if not music:
        print("Warning: No music available. Video will be created without music.")
        resource_music_link = None
        resource_music_volume = 0.0
    else:
        resource_music_link, resource_music_volume = random_choice_music(music, subreddit_music_type)

    # --- Start Audio Processing ---
    audio_segments = []
    space_between_tts = 0.5  # seconds
    current_total_duration = 0.0

    if narrator_title_track_path and os.path.exists(narrator_title_track_path):
        audio_segments.append(ffmpeg.input(narrator_title_track_path))
        current_total_duration += get_audio_duration(narrator_title_track_path)
        # Add silence after title if content follows
        if narrator_content_track_path and os.path.exists(narrator_content_track_path):
            audio_segments.append(ffmpeg.input(f'aevalsrc=0:d={space_between_tts}', f='lavfi'))
            current_total_duration += space_between_tts
    else:
        print("Warning: Narrator title track not found or not provided.")

    if narrator_content_track_path and os.path.exists(narrator_content_track_path):
        audio_segments.append(ffmpeg.input(narrator_content_track_path))
        current_total_duration += get_audio_duration(narrator_content_track_path)
    else:
        print("Warning: Narrator content track not found or not provided.")

    if not audio_segments:
        print("Error: No valid TTS audio tracks provided for title or content. Cannot create video.")
        shutil.rmtree(temp_processing_dir, ignore_errors=True) # Clean up temp dir
        return None

    # Concatenate available TTS audio segments
    try:
        concat_filter = ffmpeg.concat(*audio_segments, v=0, a=1).node
        (ffmpeg
            .output(concat_filter[0], tts_combined_path)
            .run(overwrite_output=True, quiet=True)
        )
    except Exception as e:
        print(f"Error concatenating TTS audio: {e}")
        shutil.rmtree(temp_processing_dir, ignore_errors=True)
        return None
    # --- End Audio Processing ---

    soundduration = get_audio_duration(tts_combined_path) # This is the duration of combined narration
    if soundduration == 0.0:
        print("Error: Combined TTS audio has zero duration. Cannot proceed.")
        shutil.rmtree(temp_processing_dir, ignore_errors=True)
        return None

    # Whisper transcription for subtitles
    try:
        print("Starting Whisper transcription for subtitles...")
        writer_options = {"max_line_count": 1, "max_words_per_line": 1}
        whisper_model = whisper.load_model("tiny.en", device="cpu") # Consider base or small for better accuracy if tiny is too basic
        tts_combined_transcribed = whisper_model.transcribe(tts_combined_path, language="en", fp16=False, word_timestamps=True, task="transcribe")
        srt_writer = get_writer("srt", os.path.dirname(tts_combined_srt_path)) # Pass directory to writer
        srt_writer(tts_combined_transcribed, os.path.basename(tts_combined_srt_path), writer_options)
        print(f"Subtitles generated: {tts_combined_srt_path}")
        if not os.path.exists(tts_combined_srt_path):
            print("Warning: SRT file was not created by Whisper.")
            # Fallback: create an empty SRT file to prevent ffmpeg error if subtitles are mandatory in filter graph
            with open(tts_combined_srt_path, 'w') as f:
                f.write("") 
    except Exception as e:
        print(f"Error during Whisper transcription: {e}. Subtitles might be missing.")
        # Fallback: create an empty SRT file
        with open(tts_combined_srt_path, 'w') as f:
            f.write("") 

    # Background Music Processing
    if resource_music_link and os.path.exists(resource_music_link):
        music_track_input = ffmpeg.input(resource_music_link)
        music_duration = get_audio_duration(resource_music_link)

        if music_duration > 0 and soundduration > 0:
            if music_duration < soundduration:
                loops = int(soundduration / music_duration) + 1
                # crossfade_duration = min(10, music_duration / 2) # Ensure crossfade is not too long for short music
                crossfade_duration = 5 

                looped_inputs = [ffmpeg.input(resource_music_link) for _ in range(loops)]
                try:
                    (ffmpeg
                        .filter(looped_inputs, 'acrossfade', d=str(crossfade_duration), c1='tri', c2='tri')
                        .output(music_looped_path)
                        .run(overwrite_output=True, quiet=True)
                    )
                    music_source_for_processing = music_looped_path
                except Exception as e:
                    print(f"Error looping music with acrossfade: {e}. Using original music track.")
                    music_source_for_processing = resource_music_link # Fallback to original if looping fails
            else:
                music_source_for_processing = resource_music_link
            
            try:
                (ffmpeg
                    .input(music_source_for_processing)
                    .filter('atrim', start=0, end=soundduration)
                    .filter('volume', resource_music_volume)
                    .filter('afade', t='out', st=max(0, soundduration-5), d=5)
                    .output(processed_music_path)
                    .run(overwrite_output=True, quiet=True)
                )
            except Exception as e:
                print(f"Error processing music: {e}. Continuing without music.")
                processed_music_path = None # No music if processing fails
        else:
            print("Music duration or sound duration is zero. Skipping music processing.")
            processed_music_path = None
    else:
        print("No music link provided or file does not exist. Skipping music processing.")
        processed_music_path = None

    # Mixing TTS with Background Music (if music exists)
    narration_audio_stream = ffmpeg.input(tts_combined_path)
    if processed_music_path and os.path.exists(processed_music_path):
        background_music_stream = ffmpeg.input(processed_music_path)
        try:
            (ffmpeg
                .filter([narration_audio_stream, background_music_stream], 'amix', inputs=2, duration='first', dropout_transition=str(soundduration))
                .output(mixed_audio_file_path)
                .run(overwrite_output=True, quiet=True)
            )
            final_audio_stream_for_video = ffmpeg.input(mixed_audio_file_path)
        except Exception as e:
            print(f"Error mixing narration and music: {e}. Using narration only.")
            final_audio_stream_for_video = narration_audio_stream # Fallback to narration only
    else:
        print("Processed music path not available. Using narration audio only for video.")
        # shutil.copy(tts_combined_path, mixed_audio_file_path) # If mixed_audio_file_path is expected later
        final_audio_stream_for_video = narration_audio_stream

    # Video Processing
    if not os.path.exists(random_video_path):
        print(f"Error: Selected background video {random_video_path} not found.")
        shutil.rmtree(temp_processing_dir, ignore_errors=True)
        return None
        
    video_duration = get_video_duration(random_video_path)
    video_input_options = {}

    if video_duration == 0.0:
        print(f"Error: Background video {random_video_path} has zero duration. Cannot use this video.")
        shutil.rmtree(temp_processing_dir, ignore_errors=True)
        return None

    if soundduration > video_duration:
        print(f"Narration duration ({soundduration:.2f}s) is longer than background video ({video_duration:.2f}s). Looping video.")
        # Pick a random start point within the original video's duration for the first segment
        start_ss = random.uniform(0, video_duration) if video_duration > 0 else 0
        video_input_options['ss'] = f"{start_ss:.4f}" # Format to string with precision
        video_input_options['stream_loop'] = -1  # Loop indefinitely
        video_input_options['t'] = f"{soundduration:.4f}" # Trim the looped stream to soundduration
    else:
        # Narration is shorter or equal to video duration, pick a random segment
        max_start_point = video_duration - soundduration
        start_ss = random.uniform(0, max_start_point) if max_start_point > 0 else 0
        video_input_options['ss'] = f"{start_ss:.4f}"
        video_input_options['t'] = f"{soundduration:.4f}"

    resource_video_clipped = (
        ffmpeg
        .input(random_video_path, **video_input_options)
        .filter('crop', 'ih*9/16', 'ih', '(iw-ih*9/16)/2', '0') # Centered crop to 9:16
        .filter('scale', '1080', '1920')
        .filter('setpts', 'PTS-STARTPTS') # Reset timestamps after trimming/looping
        )

    # Image Overlay
    # Determine title display duration - should be duration of title TTS if available
    title_tts_duration = get_audio_duration(narrator_title_track_path) if narrator_title_track_path else 0
    # If no title TTS, maybe show for a fixed short duration, or not at all.
    # For now, if title_tts_duration is 0, overlay won't show based on 'between(t,0,{title_tts_duration})'
    # which is fine. Or set a minimum (e.g. 2-3s) if title_track_path is None but image exists.
    if not os.path.exists(submission_image_path):
        print(f"Warning: Submission image {submission_image_path} not found. Video will not have image overlay.")
        overlay_stream = None
    else:
        overlay_stream = (
            ffmpeg
            .input(submission_image_path)
            .filter('scale', w='min(1000,iw)', h='-1') # Scale image, limit width to 1000px
        )

    # Main video and audio assembly
    output_options = {
        'c:v': 'libx264',
        'preset': 'medium', # Slower for better compression/quality, or 'fast'/'ultrafast' for speed
        'crf': '23', # Constant Rate Factor (18-28 is typical, lower is better quality)
        'c:a': 'aac',
        'b:a': '192k',
        'movflags': '+faststart' # Good for web video
    }
    
    # Filter graph construction
    video_with_audio = ffmpeg.concat(resource_video_clipped, final_audio_stream_for_video, v=1, a=1).node
    main_stream = video_with_audio[0]
    audio_stream_node = video_with_audio[1]

    # Apply fade out to video and audio if possible
    main_stream = ffmpeg.filter(main_stream, 'fade', type='out', start_time=max(0, soundduration-3), duration=3)
    # audio_stream_node = ffmpeg.filter(audio_stream_node, 'afade', type='out', start_time=max(0, soundduration-3), duration=3)
    # Note: Fading audio here might be redundant if already faded in music processing and narration ends cleanly.
    # If final_audio_stream_for_video is directly from narration_audio_stream (no music), an afade here would be good.
    if not (processed_music_path and os.path.exists(processed_music_path)):
         audio_stream_node = ffmpeg.filter(audio_stream_node, 'afade', type='out', start_time=max(0, soundduration-3), duration=3)

    if overlay_stream and title_tts_duration > 0:
        main_stream = ffmpeg.overlay(main_stream, overlay_stream, x='(W-w)/2', y='(H-h)/3', enable=f'between(t,0,{title_tts_duration})')
    elif overlay_stream: # If title TTS is 0 but image exists, maybe show for a fixed short time? For now, it won't show.
        print("Title TTS duration is 0 or title track not found, image overlay based on title duration might not show.")
        # Example: Show for first 3 seconds if no title TTS: enable='between(t,0,3)'
        # main_stream = ffmpeg.overlay(main_stream, overlay_stream, x='(W-w)/2', y='(H-h)/3', enable='between(t,0,3)')

    if os.path.exists(tts_combined_srt_path) and os.path.getsize(tts_combined_srt_path) > 0:
        main_stream = ffmpeg.filter(
            main_stream,
            'subtitles',
            filename=tts_combined_srt_path,
            force_style=f'''MarginV=60,Bold=-1,Fontname=Montserrat ExtraBold,Fontsize=36,OutlineColour=&HFF000000,BorderStyle=1,Outline=2,Shadow=2,ShadowColour=&HAA000000'''
        )
    else:
        print("SRT file is missing or empty. Skipping subtitles filter.")

    try:
        (ffmpeg
            .output(main_stream, audio_stream_node, short_file_path, **output_options)
            .run(overwrite_output=True, quiet=False) # Set quiet=False for more ffmpeg output if debugging
        )
        print(f"Video processing complete. Output: {short_file_path}")
    except ffmpeg.Error as e:
        print(f"FFmpeg Error during final video assembly: {e.stderr.decode('utf8') if e.stderr else 'Unknown FFmpeg error'}")
        shutil.rmtree(temp_processing_dir, ignore_errors=True) # Clean up
        return None
    except Exception as e:
        print(f"Generic error during final video assembly: {e}")
        shutil.rmtree(temp_processing_dir, ignore_errors=True) # Clean up
        return None
    finally:
        # Clean up temporary processing directory
        shutil.rmtree(temp_processing_dir, ignore_errors=True)
        print(f"Temporary processing directory {temp_processing_dir} cleaned up.")

    return short_file_path


# Example of how it might be called if you had TTS paths:
# if __name__ == '__main__':
#     # Create dummy TTS files for testing
#     os.makedirs("temp_tts", exist_ok=True)
#     dummy_title_tts = "temp_tts/title.mp3"
#     dummy_content_tts = "temp_tts/content.mp3"
#     # You'd use a real TTS engine to create these from text
#     # For now, just creating silent placeholders if you run this directly
#     try:
#         ffmpeg.input('aevalsrc=0:d=2', f='lavfi').output(dummy_title_tts).run(overwrite_output=True, quiet=True)
#         ffmpeg.input('aevalsrc=0:d=10', f='lavfi').output(dummy_content_tts).run(overwrite_output=True, quiet=True)
#     except Exception as e:
#        print(f"Could not create dummy tts files: {e}")

#     test_kwargs = {
#         'id': 'test_story_001',
#         'title': 'My Test Story Title',
#         'music_type': 'general',
#         'video_tts_path': dummy_title_tts,    # Corresponds to narrator_title_track in original
#         'content_tts_path': dummy_content_tts, # Corresponds to narrator_content_track in original
#         'output_dir': 'generated_videos_test' # Test output directory
#         # 'selftext' is not directly used if content_tts_path is provided
#     }
#     print(f"Running test with kwargs: {test_kwargs}")
#     # Need to ensure make_submission_image.py has run and created temp/images/test_story_001.png
#     # os.makedirs("temp/images", exist_ok=True)
#     # with open("temp/images/test_story_001.png", "w") as f: f.write("dummy png") # DUMMY, use real image

#     video_path = create_short_video(**test_kwargs)
#     if video_path:
#         print(f"Test video created: {video_path}")
#     else:
#         print("Test video creation failed.")
#     # Cleanup dummy files
#     if os.path.exists(dummy_title_tts): os.remove(dummy_title_tts)
#     if os.path.exists(dummy_content_tts): os.remove(dummy_content_tts)
#     if os.path.exists("temp/images/test_story_001.png"): os.remove("temp/images/test_story_001.png")
