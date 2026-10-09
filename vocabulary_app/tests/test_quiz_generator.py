"""Tests for the QuizGenerator class."""

import random
from unittest.mock import Mock, patch

import pytest

from vocabulary_app.services.quiz_generator import QuizGenerator
from vocabulary_app.storage.json_storage import JSONStorage
from vocabulary_app.models.word import Word


@pytest.fixture
def mock_storage():
    return Mock(spec=JSONStorage)


@pytest.fixture
def quiz_gen(mock_storage):
    return QuizGenerator(storage=mock_storage)


def test_get_words_for_quiz_empty(quiz_gen, mock_storage):
    """Test getting words when no words are saved."""
    mock_storage.load.return_value = {}
    words = quiz_gen.get_words_for_quiz(count=5)
    assert words == []


def test_get_words_for_quiz_with_data(quiz_gen, mock_storage):
    """Test getting words when words are saved."""
    mock_storage.load.return_value = {
        "hello": {"term": "hello", "definition": "greeting", "pronunciation": "/hɛloʊ/", "synonyms": [], "antonyms": []},
        "world": {"term": "world", "definition": "planet", "pronunciation": "/wɔrld/", "synonyms": [], "antonyms": []},
        "test": {"term": "test", "definition": "exam", "pronunciation": "/tɛst/", "synonyms": [], "antonyms": []},
    }
    
    words = quiz_gen.get_words_for_quiz(count=2)
    assert len(words) == 2
    assert all(isinstance(w, Word) for w in words)
    terms = [w.term for w in words]
    assert "hello" in terms or "world" in terms or "test" in terms


def test_generate_question(quiz_gen):
    """Test generating a question from a word."""
    word = Word(
        term="ephemeral",
        pronunciation="/ɪˈfɛmərəl/",
        definition="Lasting for a markedly brief time",
        synonyms=["transient", "fleeting"],
        antonyms=["permanent", "lasting"],
        ai_explanation=None,
        memory_trick=None,
    )
    
    # Mock get_words_for_quiz to return a pool including this word and others
    with patch.object(quiz_gen, "get_words_for_quiz") as mock_get_words:
        mock_get_words.return_value = [
            word,
            Word(term="hello", definition="greeting", pronunciation=None, synonyms=[], antonyms=[], ai_explanation=None, memory_trick=None),
            Word(term="world", definition="planet", pronunciation=None, synonyms=[], antonyms=[], ai_explanation=None, memory_trick=None),
            Word(term="test", definition="exam", pronunciation=None, synonyms=[], antonyms=[], ai_explanation=None, memory_trick=None),
        ]
        
        question = quiz_gen.generate_question(word)
        assert question["question_type"] == "definition_to_word"
        assert "What word matches this definition?" in question["prompt"]
        assert len(question["options"]) == 4
        assert question["word"] == "ephemeral"
        assert 0 <= question["correct_index"] < 4
        assert question["options"][question["correct_index"]] == "ephemeral"


def test_record_score(quiz_gen, mock_storage):
    """Test recording a quiz score."""
    mock_storage.load.return_value = {}
    mock_storage.save.return_value = True
    
    score_data = {
        "total": 10,
        "correct": 8,
        "percentage": 80.0,
        "timestamp": "2023-01-01T12:00:00"
    }
    
    result = quiz_gen.record_score(score_data)
    assert result is True
    mock_storage.save.assert_called_once()
    # Check that the saved data includes our score with a timestamp key
    args, kwargs = mock_storage.save.call_args
    assert args[0] == "data/scores.json"
    saved_data = args[1]
    assert isinstance(saved_data, dict)
    assert len(saved_data) == 1
    # The key should be a timestamp (we mocked it, so check the value)
    saved_score = list(saved_data.values())[0]
    assert saved_score["total"] == 10
    assert saved_score["correct"] == 8
    assert saved_score["percentage"] == 80.0


def test_get_scores(quiz_gen, mock_storage):
    """Test retrieving scores."""
    mock_storage.load.return_value = {
        "2023-01-01T12:00:00": {"total": 5, "correct": 3, "percentage": 60.0},
        "2023-01-02T12:00:00": {"total": 5, "correct": 5, "percentage": 100.0},
    }
    
    scores = quiz_gen.get_scores()
    assert isinstance(scores, dict)
    assert len(scores) == 2
    assert "2023-01-01T12:00:00" in scores
    assert "2023-01-02T12:00:00" in scores
    assert scores["2023-01-01T12:00:00"]["percentage"] == 60.0
    assert scores["2023-01-02T12:00:00"]["percentage"] == 100.0
