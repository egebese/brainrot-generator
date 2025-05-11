import datetime
import os
import random # For placeholder data

from PIL import Image, ImageFont, ImageDraw, ImageOps # ImageOps for potential padding

from reddit_shorts.config import project_path # This should be default_project_path now or ensure it resolves correctly
# Removed unused utils: split_string_at_space, abbreviate_number, format_relative_time
# as we will simplify the image to mostly title, or use the template's existing elements.

# Helper function for text wrapping (can be improved)
def wrap_text(text, font, max_width):
    lines = []
    if not text:
        return lines
    
    words = text.split()
    current_line = ''
    for word in words:
        # Test if adding word exceeds max_width
        # For multiline_textbbox, we'd need a draw object, but font.getlength is for single line
        # A simple approximation: test bbox of current_line + word
        # More accurately, build line by line and measure with draw.multiline_textbbox
        if current_line: # if line is not empty
            test_line = f'{current_line} {word}'
        else:
            test_line = word
        
        # Use textbbox for more accurate width, considering font specifics
        # Requires a ImageDraw object, so we pass it or create a dummy one if needed for helper
        # For simplicity here, let's assume a draw object would be available or use getlength as an approximation
        # Note: getlength is for single line. For multiline, textbbox is better.
        # Pillow versions differ: older getsize, newer getlength, textbbox, multiline_textbbox
        try:
            # Try to get width using textlength if available (newer Pillow)
            line_width = font.getlength(test_line)
        except AttributeError:
            # Fallback for older Pillow or if no draw object for textbbox
            # This is a rough estimate based on average char width, not ideal.
            # A better fallback for older Pillow is draw.textsize(test_line, font=font)[0]
            # but this helper doesn't have `draw` yet.
            # For a robust solution, this helper would need `draw` or be part of a class.
            # For now, we keep it simple and expect it might need refinement.
            # A very basic character count based splitting if font metrics fail badly:
            # if len(test_line) * (font.size * 0.6) > max_width: # Rough estimate
            # For now, let's stick to what original code implies (word splitting by count)
            # The original code had `characters_to_linebreak` which is what we are trying to replace
            # with a width-based approach.
            pass # Placeholder for more robust width check if font.getlength fails

        if font.getlength(test_line) <= max_width:
            current_line = test_line
        else:
            if current_line: # Avoid adding empty lines if a single word is too long
                lines.append(current_line)
            current_line = word
            # Handle case where a single word is longer than max_width (optional: break word)
            if font.getlength(current_line) > max_width:
                # For now, just add it if it's the only word, it will overflow.
                # Proper handling would be char-level splitting.
                lines.append(current_line)
                current_line = '' # Reset if word itself was added
    
    if current_line: # Add the last line
        lines.append(current_line)
    return lines

def generate_reddit_story_image(**kwargs) -> None:
    story_id = str(kwargs.get('id', 'unknown_story')) # Use ID for filename, provide fallback
    # subreddit will be music_type or 'local_story' passed from main.py
    subreddit = str(kwargs.get('subreddit', 'local_story')) 
    submission_title = str(kwargs.get('title', 'Untitled Story'))

    # Provide placeholders for Reddit-specific data not available from local files
    submission_author = str(kwargs.get('author', story_id[:20])) # Use truncated story_id or a generic name
    submission_timestamp = kwargs.get('timestamp', datetime.datetime.now().timestamp())
    submission_score = int(kwargs.get('score', random.randint(20, 300)))
    submission_comments_int = int(kwargs.get('num_comments', random.randint(5, 50)))

    subreddit_lowercase = subreddit.lower()

    # Ensure temp/images directory exists
    temp_images_dir = os.path.join(project_path, "temp", "images")
    os.makedirs(temp_images_dir, exist_ok=True)

    story_template_path = os.path.join(project_path, "resources", "images", "reddit_submission_template.png")
    if not os.path.exists(story_template_path):
        print(f"Error: Story template not found at {story_template_path}")
        return
    story_template = Image.open(story_template_path).convert("RGBA") # Ensure RGBA for transparency handling
    template_width, template_height = story_template.size

    # Define offsets for the title box based on user specification
    offset_left = 148
    offset_top = 198
    offset_right = 148
    offset_bottom = 134

    # Calculate title box coordinates
    title_box_left = offset_left
    title_box_top = offset_top
    title_box_right = template_width - offset_right
    title_box_bottom = template_height - offset_bottom
    title_box_width = title_box_right - title_box_left
    title_box_height = title_box_bottom - title_box_top # Calculated for completeness

    if title_box_width <= 0 or title_box_height <= 0:
        print(f"Error: Calculated title box dimensions are invalid (width: {title_box_width}, height: {title_box_height}). Check template size and offsets.")
        return
    
    # Output filename uses story_id
    submission_image_path = os.path.join(temp_images_dir, f"{story_id}.png")
    
    community_logo_path = os.path.join(project_path, "resources", "images", "subreddits", f"{subreddit_lowercase}.png")
    default_community_logo_path = os.path.join(project_path, "resources", "images", "subreddits", "default.png")

    if len(submission_author) > 22:
        submission_author_formatted = submission_author[:22]
        # return submission_author_formatted # This was an early return, should not be here
    else:
        submission_author_formatted = submission_author

    font_name = "Montserrat-ExtraBold" # Changed from LiberationSans-Bold
    # Start with a reasonable font size; this might need to be dynamic later.
    # For dynamic font sizing, you would loop, check fit, and adjust size.
    title_font_size = 60 
    try:
        title_font = ImageFont.truetype(font_name, title_font_size)
    except IOError:
        print(f"Error: Font '{font_name}' at size {title_font_size} not found. Please ensure Montserrat ExtraBold is installed and accessible.")
        # Attempt a very basic fallback if the specified font isn't found
        try:
            title_font = ImageFont.load_default() # Very basic, might not look good
            print("Warning: Using default Pillow font due to error with Montserrat-ExtraBold.")
        except Exception as e_font_fallback:
            print(f"Error loading default font: {e_font_fallback}. Cannot draw title.")
            return

    draw = ImageDraw.Draw(story_template)

    if os.path.exists(community_logo_path):
        community_logo_img = Image.open(community_logo_path)
    elif os.path.exists(default_community_logo_path):
        community_logo_img = Image.open(default_community_logo_path)
    else:
        print(f"Warning: Default community logo not found at {default_community_logo_path}. Skipping logo.")
        community_logo_img = None

    if community_logo_img:
        community_logo_img = community_logo_img.resize((244, 244))
        story_template.paste(community_logo_img, (222, 368), mask=community_logo_img if community_logo_img.mode == 'RGBA' else None)

    # --- Text Wrapping and Drawing for Title ---
    # Using a simpler wrap_text logic for now. Pillow's TextWrapper is not in older versions.
    # For complex cases, a more sophisticated text engine or manual line breaking based on draw.textbbox is better.
    
    # Simple line wrapper (based on character count per line, then join - from original code)
    # This is less accurate than width-based wrapping. We'll try to improve.
    # characters_to_linebreak = int(title_box_width / (title_font_size * 0.45)) # Rough estimate of chars per line
    # if characters_to_linebreak == 0: characters_to_linebreak = 10 # Avoid zero div / too small
    # chunks = []
    # current_line_start = 0
    # while current_line_start < len(submission_title):
    #     line_end = current_line_start + characters_to_linebreak
    #     if line_end < len(submission_title):
    #         # Try to break at a space
    #         actual_line_end = submission_title.rfind(' ', current_line_start, line_end + 1)
    #         if actual_line_end == -1 or actual_line_end < current_line_start: # No space found, or space is before start
    #             actual_line_end = line_end # Break mid-word if no space
    #     else:
    #         actual_line_end = len(submission_title)
    #     chunks.append(submission_title[current_line_start:actual_line_end].strip())
    #     current_line_start = actual_line_end + 1 # Skip the space if broken at space
    # wrapped_title_text = '\n'.join(chunks)

    # Improved wrapping using the helper (still basic, assumes `font.getlength` works)
    wrapped_lines = wrap_text(submission_title, title_font, title_box_width)
    wrapped_title_text = '\n'.join(wrapped_lines)

    # If you have Pillow 9.2.0+ you can use multiline_textbbox for better vertical centering and fit checking.
    # For now, we draw at top of box and rely on fixed line spacing.
    # Anchor 'lt' means top-left for the text block.
    # To center within the box, more calculations are needed (get text block height, then offset top).
    
    # Get the bounding box of the wrapped text to help with centering (optional, but good for alignment)
    try:
        # text_bbox for Pillow 9.2.0+
        # For older versions, this specific call might not exist or behave differently.
        # draw.multiline_textbbox((0,0), wrapped_title_text, font=title_font, spacing=4) # spacing is line spacing
        # If using an older Pillow, one might have to render to a dummy image to get size or sum line heights.
        # For now, let's use a default spacing and align top-left in the box.
        text_x = title_box_left
        text_y = title_box_top
        line_spacing = 10 # Adjust as needed for the chosen font size

        # Vertical centering: (needs text block height)
        #_, _, _, text_block_bottom = draw.multiline_textbbox((text_x, text_y), wrapped_title_text, font=title_font, spacing=line_spacing)
        #text_block_height = text_block_bottom - text_y # This is not quite right, text_y is not 0 for bbox calc relative to (0,0)
        # A better way: sum heights or use bbox with (0,0) as origin
        # For simplicity, let's just draw from the top of the box for now and adjust line spacing.
        # True vertical centering within the box title_box_height would involve:
        # 1. Get total height of wrapped_title_text with chosen font and spacing.
        # 2. text_y = title_box_top + (title_box_height - total_text_height) / 2

        draw.multiline_text(
            (text_x, text_y),
            wrapped_title_text,
            fill=(35, 31, 32, 255), # Black, fully opaque
            font=title_font,
            spacing=line_spacing, # Line spacing
            align='left' # 'left', 'center', or 'right' (horizontal alignment of lines)
        )
        print(f"Title drawn in box ({title_box_left},{title_box_top})-({title_box_right},{title_box_bottom}) with font size {title_font_size}.")

    except Exception as e_draw:
        print(f"Error drawing multiline text for title: {e_draw}")

    # Since the template now provides all other UI elements (r/AITA, scores, etc.),
    # we remove the script's logic for drawing those.
    # The original code for drawing author, timestamp, scores, community logo is now removed.

    try:
        story_template.save(submission_image_path)
        print(f"Submission image saved to: {submission_image_path}")
    except Exception as e:
        print(f"Error saving submission image: {e}")

    # story_template.show() # Keep commented out unless debugging
