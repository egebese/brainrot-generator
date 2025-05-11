from reddit_shorts.make_submission_image import generate_reddit_story_image


def test_generate_reddit_story_image():
    submission_data = {
        'subreddit': 'askreddit',
        'author': 'gavink',
        'title': 'What are some early signs of male pattern baldness?',
        'timestamp': 1703679574,
        'score': 100,
        'num_comments': 50
    }

    kwargs = {
        'platform': 'youtube',
        'filter': True
    }

    generate_reddit_story_image(**{**submission_data, **kwargs})
