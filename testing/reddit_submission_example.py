import praw
import random
import time
from reddit_shorts.config import subreddits
from reddit_shorts.get_reddit_stories import connect_to_reddit
from praw.models import Submission
import os
import re
from praw.models import MoreComments
from dotenv import load_dotenv
from reddit_shorts.utils import tts_for_platform
from reddit_shorts.class_submission import qualify_submission

load_dotenv()
reddit_client_id = os.environ['REDDIT_CLIENT_ID']
reddit_client_secret = os.environ['REDDIT_CLIENT_SECRET']


def get_submission_from_reddit(reddit: praw.Reddit or None= None, **kwargs) -> Submission:
    print("Getting a story from Reddit...")
    min_character_len = 300
    max_character_len = 830
    (platform_tts_path, platform_tts) = tts_for_platform(**kwargs)
    url_pattern = re.compile(r'http', flags=re.IGNORECASE)

    while True:
        subreddit = random.choice(subreddits)
        subreddit_name = subreddit[0]

        try:
            if reddit is None:
                print("Connection failed. Attempting to reconnect...")
                reddit = connect_to_reddit(reddit_client_id, reddit_client_secret)
                time.sleep(5)

        except praw.exceptions.APIException as api_exception:
            print(f"PRAW API Exception: {api_exception}")
            reddit = None

        except Exception as e:
            print(f"Error: {e}")

        for submission in reddit.subreddit(f"{subreddit_name}").hot(limit=20):
            submission_author = submission.author
            submission_title = submission.title
            submission_text = submission.selftext

            submission_author = str(submission_author)
            submission_author = submission_author.replace("-", "")

            qualify_submission(submission, **kwargs)

            suitable_submission = False

            for top_level_comment in submission.comments:
                if isinstance(top_level_comment, MoreComments):
                    continue

                top_comment_author = top_level_comment.author
                top_comment_body = top_level_comment.body

                top_comment_author = str(top_comment_author)
                top_comment_author = top_comment_author.replace("-", "")

                if top_comment_author == "AutoModerator":
                    continue

                if top_comment_author == submission_author:
                    continue

                if url_pattern.search(top_comment_body.lower()):
                    continue

                total_length = len(submission_title) + len(submission_text) + len(top_comment_body) + len(platform_tts)
                print(f"{subreddit_name}:{submission_title} Total:{total_length}")

                if total_length < min_character_len:
                    continue

                if total_length <= max_character_len:
                    suitable_submission = True
                    break

            if suitable_submission is True:
                return submission
