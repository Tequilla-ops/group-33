"""Tests for SpacedRepetitionManager."""

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from vocabulary_app.services.spaced_repetition import SpacedRepetitionManager
from vocabulary_app.storage.json_storage import JSONStorage


@pytest.fixture
def mock_storage():
    return Mock(spec=JSONStorage)


@pytest.fixture
def sr_manager(mock_storage):
    return SpacedRepetitionManager(storage=mock_storage)


def test_review_card_missing(sr_manager, mock_storage):
    """Reviewing a non-existent card returns False."""
    mock_storage.load.return_value = {}
    result = sr_manager.review_card("missing", "good")
    assert result is False


def test_review_card_easy(sr_manager, mock_storage):
    """Reviewing card as 'easy' schedules it further out and resets difficulty to 0."""
    mock_storage.load.return_value = {
        "hello": {
            "word": {
                "term": "hello",
                "pronunciation": "/hɛloʊ/",
                "definition": "greeting",
                "synonyms": [],
                "antonyms": [],
            },
            "definition": "greeting",
            "difficulty": 1,
            "review_count": 0,
            "next_review_date": datetime.now().isoformat(),
            "last_reviewed": datetime.now().isoformat(),
        }
    }
    mock_storage.save.return_value = True

    result = sr_manager.review_card("hello", "easy")
    assert result is True
    mock_storage.save.assert_called_once()
    
    args, _ = mock_storage.save.call_args
    saved_data = args[1]
    card = saved_data["hello"]
    assert card["review_count"] == 1
    assert card["difficulty"] == 0
    
    # next_review_date should be approximately now + 4 days
    next_review = datetime.fromisoformat(card["next_review_date"])
    expected_future = datetime.now() + timedelta(days=4)
    # Allow small difference due to processing time
    assert abs((next_review - expected_future).total_seconds()) < 10


def test_review_card_good(sr_manager, mock_storage):
    """Reviewing card as 'good' schedules it medium out and sets difficulty to 1."""
    mock_storage.load.return_value = {
        "hello": {
            "word": {
                "term": "hello",
                "pronunciation": "/hɛloʊ/",
                "definition": "greeting",
                "synonyms": [],
                "antonyms": [],
            },
            "definition": "greeting",
            "difficulty": 1,
            "review_count": 1,
            "next_review_date": datetime.now().isoformat(),
            "last_reviewed": datetime.now().isoformat(),
        }
    }
    mock_storage.save.return_value = True

    result = sr_manager.review_card("hello", "good")
    assert result is True
    
    args, _ = mock_storage.save.call_args
    saved_data = args[1]
    card = saved_data["hello"]
    assert card["review_count"] == 2
    assert card["difficulty"] == 1
    
    # next_review_date should be approximately now + 4 days (2 * review_count = 2 * 2 = 4 days)
    next_review = datetime.fromisoformat(card["next_review_date"])
    expected_future = datetime.now() + timedelta(days=4)
    assert abs((next_review - expected_future).total_seconds()) < 10


def test_review_card_hard(sr_manager, mock_storage):
    """Reviewing card as 'hard' schedules it 1 day out and sets difficulty to 2."""
    mock_storage.load.return_value = {
        "hello": {
            "word": {
                "term": "hello",
                "pronunciation": "/hɛloʊ/",
                "definition": "greeting",
                "synonyms": [],
                "antonyms": [],
            },
            "definition": "greeting",
            "difficulty": 1,
            "review_count": 5,
            "next_review_date": datetime.now().isoformat(),
            "last_reviewed": datetime.now().isoformat(),
        }
    }
    mock_storage.save.return_value = True

    result = sr_manager.review_card("hello", "hard")
    assert result is True
    
    args, _ = mock_storage.save.call_args
    saved_data = args[1]
    card = saved_data["hello"]
    assert card["review_count"] == 6
    assert card["difficulty"] == 2
    
    # next_review_date should be approximately now + 1 day
    next_review = datetime.fromisoformat(card["next_review_date"])
    expected_future = datetime.now() + timedelta(days=1)
    assert abs((next_review - expected_future).total_seconds()) < 10
