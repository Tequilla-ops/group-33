"""Tests for the JSONStorage class."""

import json
import os
import tempfile

import pytest

from vocabulary_app.storage.json_storage import JSONStorage


def test_load_missing_file():
    """Loading a non-existent file returns an empty dict."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "missing.json")
        result = JSONStorage.load(path)
        assert result == {}


def test_load_corrupted_file():
    """Loading a corrupted JSON file returns an empty dict."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "corrupted.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write("{ invalid json")
        result = JSONStorage.load(path)
        assert result == {}


def test_save_and_load_roundtrip():
    """Saving and loading preserves data correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "data.json")
        original_data = {"key": "value", "number": 42, "list": [1, 2, 3]}
        success = JSONStorage.save(path, original_data)
        assert success is True
        loaded_data = JSONStorage.load(path)
        assert loaded_data == original_data


def test_save_creates_directories():
    """Saving a file in a non-existent directory creates the directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        nested_path = os.path.join(tmpdir, "nested", "deep", "data.json")
        data = {"test": True}
        success = JSONStorage.save(nested_path, data)
        assert success is True
        assert os.path.exists(os.path.dirname(nested_path))
        loaded = JSONStorage.load(nested_path)
        assert loaded == data
