import os
import random
import uuid # For generating unique IDs for stories

# Removed praw, dotenv, and time imports as they are no longer needed for local file processing.
# from dotenv import load_dotenv
# from reddit_shorts.class_submission import Submission # We will create a simpler structure for now
from reddit_shorts.config import stories_file_path, bad_words_list # music list might be used for type later

# load_dotenv() # Not needed
# reddit_client_id = os.environ['REDDIT_CLIENT_ID'] # Not needed
# reddit_client_secret = os.environ['REDDIT_CLIENT_SECRET'] # Not needed


# The Submission class might be too complex for local files initially.
# We'll aim for a dictionary structure that create_short.py can use.
# The original Submission class might have methods for cleaning, word checking, etc.
# which we might need to replicate or simplify.

def parse_stories_from_file(file_path: str) -> list[dict]:
    """Parses stories from the local text file."""
    stories = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            current_story = {}
            lines = f.readlines()
            idx = 0
            while idx < len(lines):
                line = lines[idx].strip()
                if line.startswith("Title:"):
                    if current_story: # Save previous story before starting a new one
                        # Basic validation: ensure story has title and body
                        if current_story.get("title") and current_story.get("selftext"):
                            stories.append(current_story)
                        current_story = {} # Reset for next story
                    current_story["title"] = line.replace("Title:", "", 1).strip()
                    current_story["id"] = str(uuid.uuid4()) # Generate a unique ID
                    current_story["subreddit"] = "local_story" # Placeholder
                    current_story["url"] = f"local_story_url_{current_story['id']}" # Placeholder
                    current_story["music_type"] = "general" # Default, can be refined
                    # Try to infer music_type from title or story content if desired
                    # For example:
                    if "creepy" in current_story["title"].lower() or \
                       (current_story.get("selftext") and "creepy" in current_story.get("selftext", "").lower()):
                        current_story["music_type"] = "creepy"
                    elif "story" in current_story["title"].lower() or \
                         (current_story.get("selftext") and "story" in current_story.get("selftext", "").lower()):
                        current_story["music_type"] = "storytime"

                elif line == "Story:" and "title" in current_story:
                    idx += 1
                    story_body_lines = []
                    while idx < len(lines) and not lines[idx].strip().startswith("Title:"):
                        story_body_lines.append(lines[idx].strip())
                        idx += 1
                    current_story["selftext"] = "\n".join(story_body_lines).strip()
                    continue # Already incremented idx in the inner loop

                idx += 1
            
            if current_story and current_story.get("title") and current_story.get("selftext"): # Add the last story
                stories.append(current_story)

    except FileNotFoundError:
        print(f"Error: Stories file not found at {file_path}")
        return []
    except Exception as e:
        print(f"Error reading or parsing stories file: {e}")
        return []
    return stories

def check_bad_words(text: str) -> bool:
    """Checks if the text contains any bad words from the configured list."""
    if not text:
        return False
    return any(bad_word in text.lower() for bad_word in bad_words_list)

# Keep track of stories that have been processed in this session to avoid immediate reuse.
# For persistent tracking, a database or file would be needed.
_processed_story_ids_session = set()

def get_story_from_file(**kwargs) -> dict | None:
    """Gets a single, unprocessed story from the local file."""
    # print("Getting a story from local file...") # Optional: for debugging
    
    all_stories = parse_stories_from_file(stories_file_path)
    if not all_stories:
        print("No stories found in the file or an error occurred.")
        return None

    available_stories = [s for s in all_stories if s["id"] not in _processed_story_ids_session]

    if not available_stories:
        print("All stories from the file have been processed in this session.")
        # Optionally, reset if all are processed and we want to loop:
        # _processed_story_ids_session.clear()
        # available_stories = all_stories
        # if not available_stories: return None
        return None # Or handle re-processing if desired

    selected_story = random.choice(available_stories)

    # Perform bad word check (simplified from original Submission class)
    if check_bad_words(selected_story.get("title", "")) or \
       check_bad_words(selected_story.get("selftext", "")):
        print(f"Story with title '{selected_story.get('title', '')}' contains bad words. Skipping.")
        _processed_story_ids_session.add(selected_story["id"]) # Mark as processed to avoid re-checking immediately
        return get_story_from_file(**kwargs) # Try to get another story

    _processed_story_ids_session.add(selected_story["id"])
    
    # The original Submission class had more processing, e.g. character limits,
    # database interaction. We are simplifying this for now.
    # The dictionary returned should be compatible with what create_short.py expects.
    # Essential fields based on original Submission.as_dict() and create_short.py:
    # - title (str)
    # - selftext (str)
    # - id (str)
    # - subreddit (str) -> we use "music_type" derived from story, or a placeholder
    # - url (str) - placeholder
    # - music_type (str) - derived or default "general"
    
    print(f"Selected story: '{selected_story.get('title', 'Untitled')}'")
    return selected_story

# Removed connect_to_reddit and get_story_from_reddit functions.
# The main script will now call get_story_from_file.

if __name__ == '__main__':
    # For testing purposes
    story = get_story_from_file()
    if story:
        print("\nSelected story for testing:")
        print(f"  ID: {story.get('id')}")
        print(f"  Title: {story.get('title')}")
        print(f"  Music Type: {story.get('music_type')}")
        print(f"  Story: {story.get('selftext')[:100]}...") # Print first 100 chars of story
    else:
        print("No story selected for testing.")

    # Test processing all stories
    print("\n--- All Parsed Stories ---")
    all_s = parse_stories_from_file(stories_file_path)
    for s in all_s:
        print(f"Title: {s.get('title')}, ID: {s.get('id')}, Music: {s.get('music_type')}")
    print(f"Total stories parsed: {len(all_s)}")
    if not all_s and os.path.exists(stories_file_path):
        print(f"Make sure '{stories_file_path}' is not empty and stories are formatted correctly.")
