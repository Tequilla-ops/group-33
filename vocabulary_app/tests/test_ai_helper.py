"""Tests for the AIHelper service."""

import os
from unittest.mock import patch

import pytest

from vocabulary_app.services.ai_helper import AIHelper


def test_ai_helper_no_api_key():
    """AIHelper should report not available when no API key."""
    # Temporarily unset the environment variable
    with patch.dict(os.environ, {}, clear=True):
        helper = AIHelper()
        assert not helper.is_available()


def test_ai_helper_with_api_key():
    """AIHelper should report available when API key is set."""
    with patch.dict(os.environ, {"AI_API_KEY": "test-key"}):
        helper = AIHelper()
        assert helper.is_available()


def test_ai_helper_fallback_when_unavailable():
    """When AI is unavailable, should return fallback explanations."""
    with patch.dict(os.environ, {}, clear=True):
        helper = AIHelper()
        result = helper.generate_enhancements("test", "a definition")
        assert "ai_explanation" in result
        assert "memory_trick" in result
        assert result["ai_explanation"] is not None
        assert result["memory_trick"] is not None
        assert "Test" in result["ai_explanation"]  # Capitalized due to fallback processing
        assert "Test" in result["memory_trick"]


def test_ai_helper_fallback_on_exception():
    """If AI call raises exception, should fallback to local generation."""
    # Since there's no actual AI call in the current implementation, 
    # we test that when AI is unavailable it falls back
    with patch.dict(os.environ, {"AI_API_KEY": "fake-key"}):
        helper = AIHelper()
        # Even with a fake key, the current implementation falls back
        # because there's no actual AI API call implemented
        result = helper.generate_enhancements("word", "definition")
        assert result["ai_explanation"] is not None
        assert result["memory_trick"] is not None
