"""Spaced repetition manager for review calculations."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from ..models.flashcard import Flashcard
from ..storage.json_storage import JSONStorage

class SpacedRepetitionManager:
    """Manages spaced repetition review schedules and difficulty updates."""

    def __init__(self, storage: Optional[JSONStorage] = None) -> None:
        self.storage = storage or JSONStorage()
        self.flashcards_file = "data/flashcards.json"

    def review_card(self, term: str, result: str) -> bool:
        """Update flashcard based on review result ('easy', 'good', 'hard')."""
        flashcards_data = self.storage.load(self.flashcards_file)
        if term not in flashcards_data:
            return False

        card_dict = flashcards_data[term]
        review_count = card_dict.get("review_count", 0) + 1
        
        # Calculate interval based on result
        days_added = 1
        if result == "easy":
            days_added = 4 * (review_count)
            difficulty = 0
        elif result == "good":
            days_added = 2 * (review_count)
            difficulty = 1
        else:  # hard
            days_added = 1
            difficulty = 2

        next_review = datetime.now() + timedelta(days=days_added)
        
        card_dict["review_count"] = review_count
        card_dict["difficulty"] = difficulty
        card_dict["next_review_date"] = next_review.isoformat()
        card_dict["last_reviewed"] = datetime.now().isoformat()

        flashcards_data[term] = card_dict
        return self.storage.save(self.flashcards_file, flashcards_data)
