"""Generic JSON storage helper used by the application."""

import json
import os
from typing import Any, Dict

class JSONStorage:
    """Utility class for reading and writing JSON files safely."""

    @staticmethod
    def load(path: str) -> Dict[str, Any]:
        """Load a JSON file and return its contents."""
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as fp:
                return json.load(fp)
        except (json.JSONDecodeError, OSError) as exc:
            print(f"Failed to read JSON from {path}: {exc}")
            return {}

    @staticmethod
    def save(path: str, data: Dict[str, Any]) -> bool:
        """Write data as JSON to path."""
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w", encoding="utf-8") as fp:
                json.dump(data, fp, ensure_ascii=False, indent=2)
            return True
        except OSError as exc:
            print(f"Failed to write JSON to {path}: {exc}")
            return False
