from datetime import datetime
from enum import auto, Enum, unique, IntEnum
from typing import NamedTuple, Optional, FrozenSet


@unique
class Rating(IntEnum):
    LEFT = 1
    LEAN_LEFT = 2
    CENTER = 3
    LEAN_RIGHT = 4
    RIGHT = 5
    MIXED = 6


class NewsSource(NamedTuple):
    name: str
    rating: Rating
    url: str


class Story(NamedTuple):
    news_source: NewsSource
    url: str
    publish_date: Optional[datetime]
    title: str
    authors: FrozenSet[str]
    text: str
    summary: str
    keywords: FrozenSet[str]
