"""Tests for the Flashcard dataclass and its validation."""

import pytest
from datetime import datetime, timedelta

from vocabulary_app.models.flashcard import Flashcard
from vocabulary_app.models.word import Word


def make_word():
    return Word(
        term="test",
        pronunciation="/tɛst/",
        definition="A test definition",
        synonyms=[],
        antonyms=[],
        ai_explanation=None,
        memory_trick=None,
    )


def test_flashcard_defaults():
    w = make_word()
    fc = Flashcard(word=w, definition=w.definition, difficulty=1)
    assert isinstance(fc.next_review_date, datetime)
    assert isinstance(fc.last_reviewed, datetime)
    assert fc.review_count == 0


def test_flashcard_invalid_difficulty():
    w = make_word()
    with pytest.raises(ValueError, match="Difficulty must be 0, 1, or 2"):
        Flashcard(word=w, definition=w.definition, difficulty=3)
