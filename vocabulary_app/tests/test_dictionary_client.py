"""Tests for the DictionaryClient with mocked requests."""

from unittest.mock import patch, Mock

import json
import pytest
import requests

from vocabulary_app.services.dictionary_client import DictionaryClient
from vocabulary_app.storage.json_storage import JSONStorage
from vocabulary_app.models.word import Word


@pytest.fixture
def mock_storage():
    return Mock(spec=JSONStorage)


@pytest.fixture
def client(mock_storage):
    return DictionaryClient(storage=mock_storage)


def test_get_word_success(client):
    """Test successful word lookup."""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = [
        {
            "word": "test",
            "phonetics": [{"text": "/tɛst/"}],
            "meanings": [
                {
                    "partOfSpeech": "noun",
                    "definitions": [{"definition": "A means of testing"}],
                    "synonyms": ["trial", "exam"],
                    "antonyms": ["proof"],
                }
            ],
        }
    ]

    with patch("vocabulary_app.services.dictionary_client.requests.get", return_value=mock_response) as mock_get:
        word = client.get_word("test")
        mock_get.assert_called_once_with(
            "https://api.dictionaryapi.dev/api/v2/entries/en/test", timeout=10
        )

        assert word is not None
        assert word.term == "test"
        assert word.pronunciation == "/tɛst/"
        assert word.definition == "A means of testing"
        assert "trial" in word.synonyms
        assert "proof" in word.antonyms


def test_get_word_not_found(client):
    """Test word not found (API returns empty list)."""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = []

    with patch("vocabulary_app.services.dictionary_client.requests.get", return_value=mock_response):
        word = client.get_word("nonexistent")
        assert word is None


def test_get_word_network_error(client):
    """Test network error handling."""
    with patch(
        "vocabulary_app.services.dictionary_client.requests.get",
        side_effect=requests.RequestException("Network error"),
    ):
        word = client.get_word("test")
        assert word is None


def test_get_word_invalid_json(client):
    """Test invalid JSON response handling."""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

    with patch("vocabulary_app.services.dictionary_client.requests.get", return_value=mock_response):
        word = client.get_word("test")
        assert word is None


def test_clean_query():
    """Test input cleaning with regex."""
    client = DictionaryClient()
    assert client._clean_query("  Hello!  ") == "hello"
    assert client._clean_query("A-B") == "ab"
    assert client._clean_query("123abc") == "abc"
    assert client._clean_query("") == ""
    assert client._clean_query("   ") == ""


def test_clean_query_invalid_after_cleaning():
    """Test that cleaning empty string raises ValueError in get_word."""
    client = DictionaryClient()
    with pytest.raises(ValueError, match="Word input cannot be empty"):
        client.get_word("")
    with pytest.raises(ValueError, match="Word input cannot be empty"):
        client.get_word("   ")
    with pytest.raises(ValueError, match="Word input is invalid after cleaning"):
        client.get_word("123!@#")
