import os

# Determine the project root based on the location of this config file.
# Assumes config.py is in 'reddit_shorts' and 'resources' is in the parent directory.
launcher_path = os.path.abspath(os.path.dirname(__file__))
project_path = os.path.abspath(os.path.join(launcher_path, os.pardir))

# Path for the input stories text file
stories_file_path = os.path.join(project_path, "stories.txt")

# Path for saving output videos
output_video_path = os.path.join(project_path, "generated_shorts")
os.makedirs(output_video_path, exist_ok=True) # Ensure the directory exists

video_resources_path = os.path.join(project_path, "resources", "footage")
if not os.path.exists(video_resources_path):
    # Fallback for when installed as a package and resources are alongside modules
    video_resources_path = os.path.join(launcher_path, "resources", "footage")
    if not os.path.exists(video_resources_path):
        print(f"Warning: Footage directory not found at {os.path.join(project_path, 'resources', 'footage')} or {video_resources_path}")
        video_resources = []
    else:
        video_resources = os.listdir(video_resources_path)
else:
    video_resources = os.listdir(video_resources_path)


music_resources_path = os.path.join(project_path, "resources", "music")
if not os.path.exists(music_resources_path):
    # Fallback for when installed as a package and resources are alongside modules
    music_resources_path = os.path.join(launcher_path, "resources", "music")
    if not os.path.exists(music_resources_path):
        print(f"Warning: Music directory not found at {os.path.join(project_path, 'resources', 'music')} or {music_resources_path}")
        music_resources = []
    else:
        music_resources = os.listdir(music_resources_path)
else:
    music_resources = os.listdir(music_resources_path)

footage = []
for file_name in video_resources: # Renamed 'file' to 'file_name' to avoid conflict
    file_path = os.path.join(video_resources_path, file_name)
    if not file_name.startswith('.DS_Store') and os.path.isfile(file_path): # Added check for file
        footage.append(file_path)

# CHECK MUSIC FOR COPYRIGHT BEFORE USING
# music_path str, volumex float float, music_type str
music = []
for file_name in music_resources: # Renamed 'file' to 'file_name'
    music_file_path = os.path.join(music_resources_path, file_name)
    if not file_name.startswith('.DS_Store') and os.path.isfile(music_file_path): # Added check for file
        # Defaulting music type to general and volume, adjust as needed
        if file_name.endswith((".mp3", ".wav", ".ogg")): # Basic check for audio files
            # Assigning a default music_type and volume.
            # You might want to develop a more sophisticated way to categorize music if needed.
            music_type = "general"
            if "storytime" in file_name.lower():
                music_type = "storytime"
            elif "creepy" in file_name.lower():
                music_type = "creepy"
            
            # Example: Assign different volumes based on type or filename, or just a default
            volume = 0.2
            if music_type == "storytime":
                volume = 0.35
            elif music_type == "creepy":
                volume = 0.4

            music.append((music_file_path, volume, music_type))

if not footage:
    print("Warning: No footage files found. Please check 'resources/footage' directory.")
if not music:
    print("Warning: No music files found. Please check 'resources/music' directory and ensure they have .mp3, .wav, or .ogg extensions.")
    # Add at least one default placeholder if empty, otherwise parts of the code might fail
    # music.append(("placeholder.mp3", 0.2, "general")) # This would require a placeholder file

# This list is no longer needed as we are reading from a local file.
# subreddits = [
#         # Asking Questions
#         ("askreddit", "general", True),
# ... (rest of the subreddits list was here) ...
#         ("thetruthishere", "creepy", False)
#         ]

bad_words_list = [
    "porn",
    "fuck",
    "fucking"
]

# TikTok Session ID for TTS (No longer used by the new library)
# TIKTOK_SESSION_ID_TTS = os.environ.get('TIKTOK_SESSION_ID_TTS', 'YOUR_SESSION_ID_HERE_OR_THE_ACTUAL_ONE')

# List of words to check for in stories (optional)
