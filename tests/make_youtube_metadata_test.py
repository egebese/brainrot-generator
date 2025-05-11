from reddit_shorts.make_youtube_metadata import create_video_title, create_video_keywords
import pytest


@pytest.fixture
def metadata():
    submission_title = "askreddit Craziest Coincidences: Redditors, what's the most mind-blowing coincidence you've ever experienced?"
    subreddit = "askreddit"

    return submission_title, subreddit


def test_create_video_title(metadata):
    submission_title, subreddit = metadata

    kwargs = {
        'platform': 'youtube',
        'title': submission_title,
        'subreddit': subreddit
    }

    assert create_video_title(**kwargs) == "askreddit Craziest Coincidences: Redditors, what's the most mind-blowing coinc... #reddit #minecraft"


def test_create_video_keywords(metadata):
    submission_title, subreddit = metadata
    additional_keywords = "minecraft,mindblowing,askreddit"

    assert create_video_keywords(submission_title, subreddit, additional_keywords) == ['askreddit', 'craziest', 'coincidences', 'redditors', 'whats', 'the', 'most', 'mindblowing', 'coincidence', 'youve', 'ever', 'experienced', 'minecraft']
