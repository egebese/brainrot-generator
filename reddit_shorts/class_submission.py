from datetime import datetime
from typing import Any, Optional
import re
import os
from praw.models import MoreComments
from praw.models.comment_forest import CommentForest
from reddit_shorts.config import project_path
from reddit_shorts.query_db import check_if_video_exists, write_to_db, check_for_admin_posts
from reddit_shorts.class_comment import Comment
from reddit_shorts.utils import tts_for_platform, contains_bad_words


class Submission:
    def __init__(self,
                 subreddit: str,
                 author: str,
                 title: str,
                 is_self: bool,
                 text: str,
                 url: str,
                 score: int,
                 num_comments: int,
                 timestamp: datetime,
                 id: int,
                 comments: CommentForest,
                 music_type: Optional[str],
                 top_comment_body: Optional[str],
                 top_comment_author: Optional[str],
                 kind: str = None):
        self.subreddit = subreddit
        self.author = author
        self.title = title
        self.is_self = is_self
        self.text = text
        self.url = url
        self.score = score
        self.num_comments = num_comments
        self.timestamp = timestamp
        self.id = id
        self.comments = comments
        self.music_type = music_type
        self.top_comment_body = top_comment_body
        self.top_comment_author = top_comment_author
        self.kind = kind

    def as_dict(self):
        return {
            "subreddit": self.subreddit,
            "author": self.author,
            "title": self.title,
            "is_self": self.is_self,
            "text": self.text,
            "url": self.url,
            "score": self.score,
            "num_comments": self.num_comments,
            "timestamp": self.timestamp,
            "id": self.id,
            "comments": self.comments,
            "music_type": self.music_type,
            "top_comment_body": self.top_comment_body,
            "top_comment_author": self.top_comment_author,
            "kind": self.kind
        }

    @classmethod
    def process_submission(cls, subreddit: list, submission: Any, **kwargs) -> 'Submission':
        platform = kwargs.get('platform')
        (platform_tts_path, platform_tts) = tts_for_platform(**kwargs)

        subreddit_name = subreddit[0]
        subreddit_music_type = subreddit[1]

        tts_character_limit = 200
        min_character_len = 300

        if platform == 'youtube':
            max_character_len = 830

        elif platform == 'tiktok':
            max_character_len = 2400

        submission_author = str(submission.author)
        submission_title = str(submission.title)
        submission_text = str(submission.selftext)
        submission_id = str(submission.id)
        submission_kind = identify_post_type(submission)

        submission_author = submission_author.replace("-", "")

        qualify_submission(submission, **kwargs)

        suitable_submission = False
        comments = submission.comments

        for index, comment in enumerate(comments):
            if isinstance(comment, MoreComments):
                continue

            comment_data = Comment.process_comment(comment, submission_author)
            top_comment_body = comment_data.body
            top_comment_author = comment_data.author
            top_comment_id = comment_data.id

            total_length = len(submission_title) + len(submission_text) + len(top_comment_body) + len(platform_tts)
            print(f"{subreddit_name}:{submission_title} Total:{total_length}")

            if total_length < min_character_len:
                continue

            if total_length <= max_character_len:
                video_exists = check_if_video_exists(submission_id, top_comment_id)
                if video_exists is False:
                    suitable_submission = True
                    break

                else:
                    continue

            if index == len(comments) - 1:
                print('reached the end of the comments')
                return None

        if suitable_submission is True:
            print("Found a suitable submission!")
            print(f"Suitable Submission:{subreddit}:{submission_title} Total:{total_length}")

            if not os.path.exists(f"{project_path}/temp/ttsoutput/texts/"):
                os.makedirs(f"{project_path}/temp/ttsoutput/texts/")

            if len(submission_title) >= tts_character_limit:
                with open(f'{project_path}/temp/ttsoutput/texts/{submission_author}_title.txt', 'w', encoding='utf-8') as file:
                    file.write(submission_title)

            if len(submission_text) >= tts_character_limit:
                with open(f'{project_path}/temp/ttsoutput/texts/{submission_author}_content.txt', 'w', encoding='utf-8') as file:
                    file.write(submission_text)

            if len(top_comment_body) >= tts_character_limit:
                with open(f'{project_path}/temp/ttsoutput/texts/{top_comment_author}.txt', 'w', encoding='utf-8') as file:
                    file.write(top_comment_body)

            write_to_db(submission_id, top_comment_id)

            return cls(
                subreddit=subreddit_name,
                author=submission_author,
                title=submission_title,
                is_self=submission.is_self,
                text=submission_text,
                url=submission.url,
                score=submission.score,
                num_comments=submission.num_comments,
                timestamp=submission.created_utc,
                id=submission_id,
                comments=submission.comments,
                music_type=subreddit_music_type,
                top_comment_body=top_comment_body,
                top_comment_author=top_comment_author,
                kind=submission_kind
            )


class Title(Submission):
    kind = "title"


class Text(Submission):
    kind = "text"


class Link(Submission):
    kind = "link"


class Image(Submission):
    kind = "image"


class Video(Submission):
    kind = "video"


def identify_post_type(submission: Any) -> str:
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    video_extensions = ['.mp4', '.avi', '.mov']
    reddit_image_extensions = [
        'https://www.reddit.com/gallery/',
        'https://i.redd.it/'
    ]
    reddit_video_extensions = [
        'https://v.redd.it/',
        'https://youtube.com',
        'https://youtu.be'
    ]

    if submission.is_self is True:

        if submission.selftext == "":
            return Title.kind

        else:
            return Text.kind

    if submission.is_self is False:
        url = submission.url

        if any(url.endswith(ext) for ext in image_extensions):
            return Image.kind

        elif any(url.startswith(ext) for ext in reddit_image_extensions):
            return Image.kind

        elif any(url.endswith(ext) for ext in video_extensions):
            return Video.kind

        elif any(url.startswith(ext) for ext in reddit_video_extensions):
            return Video.kind

        else:
            return Link.kind


def qualify_submission(submission: Any, **kwargs) -> None:
    filter = kwargs.get('filter')
    url_pattern = re.compile(r'http', flags=re.IGNORECASE)

    submission_title = str(submission.title)
    submission_text = str(submission.selftext)
    submission_id = str(submission.id)
    submission_kind = identify_post_type(submission)

    if submission_kind == "image" or submission_kind == "video":
        # print(f"This submission is not in text {submission_title}")
        pass

    if url_pattern.search(submission_text.lower()):
        # print("Skipping post that contains a link")
        pass

    admin_post = check_for_admin_posts(submission_id)
    if admin_post is True:
        pass

    if filter is True:
        if contains_bad_words(submission_title):
            pass

        if contains_bad_words(submission_text):
            pass
