"""Unit tests for Word model and basic validation."""

import pytest
from vocabulary_app.models.word import Word

def test_word_creation_valid():
    w = Word(
        term="ephemeral",
        pronunciation="/?'fem?r?l/",
        definition="Lasting for a very short time.",
        synonyms=["transient", "fleeting"],
        antonyms=["permanent"],
        ai_explanation="Short lived.",
        memory_trick="Eph is ephemeral."
    )
    assert w.term == "ephemeral"
    assert w.definition == "Lasting for a very short time."

def test_word_creation_invalid_empty():
    with pytest.raises(ValueError, match="Word term cannot be empty"):
        Word(
            term="",
            pronunciation=None,
            definition="test",
            synonyms=[],
            antonyms=[]
        )

def test_word_creation_invalid_too_short():
    with pytest.raises(ValueError, match="Word term must be at least 2 characters"):
        Word(
            term="a",
            pronunciation=None,
            definition="test",
            synonyms=[],
            antonyms=[]
        )
