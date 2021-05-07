from enum import auto, Enum, unique
from typing import NamedTuple


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
    title: str
    authors: frozenset[str]
    text: str
    summary: str
    keywords: frozenset[str]
