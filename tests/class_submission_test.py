from reddit_shorts.class_submission import identify_post_type, qualify_submission, Submission
import pytest
from reddit_shorts.config import subreddits
from testing.reddit_submission_example import get_submission_from_reddit
import random


@pytest.fixture
def kwargs():
    kwargs = {
        'platform': 'tiktok',
        'filter': True
    }

    return kwargs


@pytest.fixture
def submission_sample(kwargs):
    data = get_submission_from_reddit(**kwargs)
    return data


def test_identify_post_type(submission_sample):
    result = identify_post_type(submission_sample)
    assert result is not None


def test_process_submission(submission_sample, kwargs):
    subreddit = random.choice(subreddits)
    result = Submission.process_submission(subreddit, submission_sample, **kwargs)
    assert result is not None


def test_qualify_submission(submission_sample, kwargs):
    qualify_submission(submission_sample, **kwargs)
