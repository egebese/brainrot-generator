import os
from flask import Blueprint, request, jsonify, send_file, send_from_directory
from reddit_shorts.tiktok_voice.src.voice import Voice
from reddit_shorts.main import run_local_video_generation
from reddit_shorts.config import footage, music

# Set the static folder when creating the blueprint
# It should be relative to the blueprint's root path.
# Since routes.py is in web_ui/, and static is also in web_ui/,
# the path will be 'static'.
main_bp = Blueprint('main', __name__, static_folder='static')

# Voice name mapping based on user's provided table
VOICE_NAME_MAP = {
    'en_male_jomboy': 'Game On',
    'en_us_002': 'Jessie',
    'es_mx_002': 'Warm',  # Note: Non-English, will be filtered by current logic unless changed
    'en_male_funny': 'Wacky',
    'en_us_ghostface': 'Scream', # Also 'Ghost Face' in user list, using 'Scream' as it's first
    'en_female_samc': 'Empathetic',
    'en_male_cody': 'Serious',
    'en_female_makeup': 'Beauty Guru',
    'en_female_richgirl': 'Bestie',
    'en_male_grinch': 'Trickster',
    'en_us_006': 'Joey',
    'en_male_narration': 'Story Teller',
    'en_male_deadpool': 'Mr. GoodGuy',
    'en_uk_001': 'Narrator',
    'en_uk_003': 'Male English UK',
    'en_au_001': 'Metro',
    'en_male_jarvis': 'Alfred',
    'en_male_ashmagic': 'ashmagic',
    'en_male_olantekkers': 'olantekkers',
    'en_male_ukneighbor': 'Lord Cringe',
    'en_male_ukbutler': 'Mr. Meticulous',
    'en_female_shenna': 'Debutante',
    'en_female_pansino': 'Varsity',
    'en_male_trevor': 'Marty',
    'en_female_f08_twinkle': 'Pop Lullaby',
    'en_male_m03_classical': 'Classic Electric',
    'en_female_betty': 'Bae',
    'en_male_cupid': 'Cupid',
    'en_female_grandma': 'Granny',
    'en_male_m2_xhxs_m03_christmas': 'Cozy',
    'en_male_santa_narration': 'Author',
    'en_male_sing_deep_jingle': 'Caroler',
    'en_male_santa_effect': 'Santa',
    'en_female_ht_f08_newyear': 'NYE 2023',
    'en_male_wizard': 'Magician',
    'en_female_ht_f08_halloween': 'Opera',
    'en_female_ht_f08_glorious': 'Euphoric',
    'en_male_sing_funny_it_goes_up': 'Hypetrain',
    'en_female_ht_f08_wonderful_world': 'Melodrama',
    'en_male_m2_xhxs_m03_silly': 'Quirky Time',
    'en_female_emotional': 'Peaceful',
    'en_male_m03_sunshine_soon': 'Toon Beat',
    'en_female_f08_warmy_breeze': 'Open Mic',
    'en_male_sing_funny_thanksgiving': 'Thanksgiving',
    'en_female_f08_salut_damour': 'Cottagecore',
    'en_us_007': 'Professor',
    'en_us_009': 'Scientist',
    'en_us_010': 'Confidence',
    'en_au_002': 'Smooth',
    # Duplicates from user table already covered: en_us_ghostface, en_us_chewbacca, etc.
    # Assuming codes from Voice enum like 'en_us_chewbacca' are preferred if not in mapping.
    'fr_001': 'French - Male 1' # Added from user's list
}

# Prioritized voice codes from user
PRIORITIZED_VOICE_CODES = [
    'en_male_jomboy',
    'en_us_002',
    'es_mx_002', 
    'en_male_funny',
    'en_us_ghostface',
    'en_female_samc',
    'en_male_cody',
    'en_female_makeup',
    'en_female_richgirl',
    'en_male_grinch',
    'en_us_006',
    'en_male_narration',
    'en_male_deadpool'
]

@main_bp.route('/')
def index():
    # Serves the index.html file from the 'static' directory
    # The directory is relative to the blueprint's static folder, 
    # or app's static_folder if blueprint has no static_folder.
    # For our setup, Flask should find it in web_ui/static/
    return send_from_directory(main_bp.static_folder, 'index.html')

@main_bp.route('/api/voices', methods=['GET'])
def get_voices():
    """Return list of available TikTok voices, with prioritized voices first."""
    prioritized_list = []
    other_voices_list = []
    
    # Ensure all prioritized codes are valid and map them to their display info
    valid_prioritized_voice_objects = []
    for code in PRIORITIZED_VOICE_CODES:
        voice_enum_member = Voice((code)) # Get enum member by value (code)
        if voice_enum_member:
             # Apply filter (e.g. English only, or specific other languages)
            if voice_enum_member.value.startswith('en_') or voice_enum_member.value in ['fr_001', 'es_mx_002']:
                voice_name = VOICE_NAME_MAP.get(code, voice_enum_member.name.replace('_', ' ').title())
                prioritized_list.append({
                    "id": code,
                    "name": voice_name,
                    "category": "TikTok"
                })
                valid_prioritized_voice_objects.append(voice_enum_member)

    # Process the rest of the voices from the Enum
    for voice_enum_member in Voice:
        if voice_enum_member not in valid_prioritized_voice_objects: # Avoid duplicates
            # Apply filter (e.g. English only, or specific other languages)
            if voice_enum_member.value.startswith('en_') or voice_enum_member.value in ['fr_001', 'es_mx_002']:
                voice_id = voice_enum_member.value
                voice_name = VOICE_NAME_MAP.get(voice_id, voice_enum_member.name.replace('_', ' ').title())
                other_voices_list.append({
                    "id": voice_id,
                    "name": voice_name,
                    "category": "TikTok"
                })
                
    return jsonify(prioritized_list + other_voices_list)

@main_bp.route('/api/backgrounds', methods=['GET'])
def get_backgrounds():
    """Return list of available background videos"""
    if not footage:
        return jsonify([])
    
    backgrounds = []
    for video_path in footage:
        base_name = os.path.basename(video_path)
        video_name_without_ext = os.path.splitext(base_name)[0]
        thumbnail_url = f"/static/thumbnails/{video_name_without_ext}.jpg"
        backgrounds.append({
            "id": base_name,
            "name": video_name_without_ext,
            "path": video_path,
            "thumbnail": thumbnail_url  # Add the thumbnail URL
        })
    return jsonify(backgrounds)

@main_bp.route('/api/music', methods=['GET'])
def get_music():
    """Return list of available music tracks"""
    if not music:
        return jsonify([])
    
    tracks = []
    for music_file_path, volume, music_type_from_config in music:
        base_name = os.path.basename(music_file_path)
        track_name = os.path.splitext(base_name)[0]
        # Construct a URL that the frontend can use to fetch the music for preview
        # Assumes music files are copied to 'web_ui/static/music_assets/'
        servable_url = f"/static/music_assets/{base_name}"
        
        tracks.append({
            "id": base_name, # Keep original ID for selection consistency if needed
            "name": track_name,
            "path": servable_url, # Send the servable URL
            "type": music_type_from_config # Use the type from config
        })
    return jsonify(tracks)

@main_bp.route('/api/generate', methods=['POST'])
def generate_video():
    """Generate a video from the provided script and settings"""
    data = request.json
    
    # Create a story entry in stories.txt format
    story_content = f"""Title: {data['title']}
Story:
{data['story']}
"""
    
    # Temporarily save the story
    with open('stories.txt', 'w', encoding='utf-8') as f:
        f.write(story_content)
    
    # Set up generation parameters
    params = {
        'filter': data.get('filter', False),
        'voice': data.get('voice', 'en_us_002'),  # Default TikTok voice
        'background_video': data.get('background_video', None),
        'background_music': data.get('background_music', None)
    }
    
    try:
        # Generate the video
        video_path = run_local_video_generation(**params)
        
        if video_path and os.path.exists(video_path):
            # Return the video file
            return send_file(
                video_path,
                mimetype='video/mp4',
                as_attachment=True,
                download_name=os.path.basename(video_path)
            )
        else:
            return jsonify({"error": "Video generation failed"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500 