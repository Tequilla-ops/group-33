"""Flashcard model used for spaced-repetition reviews."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from .word import Word

@dataclass
class Flashcard:
    """A flashcard containing a word and review metadata."""
    word: Word
    definition: str
    difficulty: int  # 0 = easy, 1 = medium, 2 = hard
    review_count: int = 0
    next_review_date: Optional[datetime] = None
    last_reviewed: Optional[datetime] = None

    def __post_init__(self) -> None:
        if self.difficulty not in (0, 1, 2):
            raise ValueError("Difficulty must be 0, 1, or 2")
        if self.next_review_date is None:
            self.next_review_date = datetime.now()
        if self.last_reviewed is None:
            self.last_reviewed = datetime.now()
