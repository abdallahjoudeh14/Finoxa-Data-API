# Google News topic IDs
_TOPIC_IDS = {
    "world": "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB",
    "business": "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB",
    "technology": "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB",
    "entertainment": "CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtVnVHZ0pWVXlnQVAB",
    "sports": "CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FtVnVHZ0pWVXlnQVAB",
    "science": "CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp0Y1RjU0FtVnVHZ0pWVXlnQVAB",
    "health": "CAAqIQgKIhtDQkFTRGdvSUwyMHZNR3QwTlRFU0FtVnVLQUFQAQ",
}


def get_topic_id(topic: str) -> str:
    """Get the Google News topic ID for a given topic.

    Args:
        topic (str): Topic name to look up

    Returns:
        str: Topic ID for Google News

    Raises:
        ValueError: If the topic is not supported
    """
    if topic not in _TOPIC_IDS:
        raise ValueError(f"Invalid topic: {topic}")

    return _TOPIC_IDS[topic]


def topic_url(topic_id: str, lang: str = "en", country: str = "US") -> str:
    """Build the Google News URL for a given topic, language, and country.

    Args:
        topic_id (str): Google News topic ID
        language (str): Language code
        country (str): Country code

    Returns:
        str: Full Google News URL
    """

    return f"https://news.google.com/topics/{topic_id}?hl={lang}-{country}&gl={country}&ceid={country}:{lang}"
