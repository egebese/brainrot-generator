import re


def create_video_title(**kwargs) -> str:
    submission_title = kwargs.get('title')
    platform = kwargs.get('platform')

    if platform == "youtube":
        title_character_limit = 100

    else:
        title_character_limit = 2200

    title_hashtags = "#reddit #minecraft"

    truncated_character_limit = title_character_limit - len(title_hashtags) - 4

    if len(submission_title) >= truncated_character_limit:
        truncated_title = submission_title[:truncated_character_limit]
        if truncated_title.endswith(' '):
            truncated_title = truncated_title[:-1]

        short_video_title = f"{truncated_title}... {title_hashtags}"
    else:
        short_video_title = f"{submission_title} {title_hashtags}"

    print(short_video_title)
    return short_video_title


def create_video_keywords(submission_title: str, subreddit: str, additional_keywords: str = None) -> list:
    # character limit is 500
    cleaned_sentence = re.sub(r'[^\w\s]', '', submission_title.lower())
    keywords = cleaned_sentence.split()
    unique_keywords = []
    keywords.append(subreddit)
    if additional_keywords is not None:
        additional_keys = additional_keywords.split(',')
        keywords.extend(additional_keys)

    for word in keywords:
        if word not in unique_keywords:
            unique_keywords.append(word)

    return unique_keywords
