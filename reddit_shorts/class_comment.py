from typing import Any
import re

from reddit_shorts.utils import contains_bad_words


class Comment():
    def __init__(self,
                 author: str,
                 body: str,
                 id: int):
        self.author = author
        self.body = body
        self.id = id

    @classmethod
    def process_comment(cls, comment: Any, submission_author: str, **kwargs) -> 'Comment':
        author = str(comment.author)
        body = str(comment.body)
        filter = kwargs.get('filter')

        url_pattern = re.compile(r'http', flags=re.IGNORECASE)

        author = author.replace("-", "")

        if author == "AutoModerator":
            # print("Skipping bot comment")
            pass

        if author == submission_author:
            # print("Skipping Submission Authors comment")
            pass

        if url_pattern.search(body.lower()):
            # print("Skipping comment that contains a link")
            pass

        if filter is True:
            if contains_bad_words(body):
                pass

        return cls(
            author=author,
            body=body,
            id=comment.id
        )
