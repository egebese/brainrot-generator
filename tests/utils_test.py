import datetime
from reddit_shorts.utils import split_string_at_space, abbreviate_number, format_relative_time, tts_for_platform, random_choice_music, contains_bad_words
from reddit_shorts.config import music, project_path


def test_split_string_at_space():
    text = "You've been kidnapped. The last person you saw on a tv series is coming to save you. Who is it?"
    index = 37
    assert split_string_at_space(text, index) == 31


def test_abbreviate_number():
    number = "9100"
    assert abbreviate_number(number) == "9.1k"


def test_format_relative_time():
    time = 1707595200.0
    formatted_time = datetime.datetime.fromtimestamp(time)
    format_relative_time(formatted_time)


def test_tts_for_platform():
    kwargs = {
        'platform': 'youtube'
    }
    platform_tts_path = f'{project_path}/youtube_tts.txt'
    try:
        with open(platform_tts_path, 'r') as file:
            platform_tts = file.read()

    except FileNotFoundError:
        print(f"File {platform_tts_path} not found.")

    assert tts_for_platform(**kwargs) == (platform_tts_path, platform_tts)


def test_random_choice_music():
    subreddit_music_type = 'general'
    random_choice_music(music, subreddit_music_type)


def test_contains_bad_words():
    text = 'fuck'
    text2 = 'what do we have here?'
    assert contains_bad_words(text) is True
    assert contains_bad_words(text2) is False
