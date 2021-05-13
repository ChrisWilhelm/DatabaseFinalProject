from datetime import datetime
from enum import auto, Enum, unique
from typing import NamedTuple, Optional, FrozenSet


@unique
class Rating(Enum):
    LEFT = auto()
    LEAN_LEFT = auto()
    CENTER = auto()
    LEAN_RIGHT = auto()
    RIGHT = auto()
    MIXED = auto()


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
