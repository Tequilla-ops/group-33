"""Quiz generator for creating vocabulary quizzes."""

import random
from typing import List, Dict, Any, Optional
from ..models.word import Word
from ..storage.json_storage import JSONStorage

class QuizGenerator:
    """Generate quiz questions from saved words."""

    def __init__(self, storage: Optional[JSONStorage] = None) -> None:
        self.storage = storage or JSONStorage()
        self.words_file = "data/words.json"
        self.scores_file = "data/scores.json"

    def get_words_for_quiz(self, count: int = 10) -> List[Word]:
        """Get a list of words for a quiz."""
        words_data = self.storage.load(self.words_file)
        words = []
        for word_dict in words_data.values():
            try:
                word = Word(
                    term=word_dict.get("term", ""),
                    pronunciation=word_dict.get("pronunciation"),
                    definition=word_dict.get("definition"),
                    synonyms=word_dict.get("synonyms", []),
                    antonyms=word_dict.get("antonyms", []),
                    ai_explanation=word_dict.get("ai_explanation"),
                    memory_trick=word_dict.get("memory_trick"),
                )
                words.append(word)
            except Exception:
                # Skip invalid word entries
                continue
        # Shuffle and limit count
        random.shuffle(words)
        return words[:count]

    def generate_question(self, word: Word) -> Dict[str, Any]:
        """Generate a single multiple-choice question."""
        # For simplicity, we do: Definition -> choose the correct word
        # We need 3 incorrect options (other words)
        all_words = self.get_words_for_quiz(count=20)  # Get a pool
        # Remove the current word from the pool
        other_words = [w for w in all_words if w.term.lower() != word.term.lower()]
        if len(other_words) < 3:
            # If not enough words, we might repeat or use placeholders; but for simplicity, we just use what we have
            other_words = other_words * 3  # repeat to have at least 3
        incorrect_terms = random.sample(other_words, min(3, len(other_words)))
        incorrect_terms = [w.term for w in incorrect_terms]
        options = incorrect_terms + [word.term]
        random.shuffle(options)
        correct_index = options.index(word.term)
        return {
            "question_type": "definition_to_word",
            "prompt": f"What word matches this definition?\\n\\n{word.definition}",
            "options": options,
            "correct_index": correct_index,
            "word": word.term,
        }

    def record_score(self, score_data: Dict[str, Any]) -> bool:
        """Record quiz score to the scores file."""
        scores = self.storage.load(self.scores_file)
        # Use a timestamp as key
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        scores[timestamp] = score_data
        return self.storage.save(self.scores_file, scores)

    def get_scores(self) -> Dict[str, Any]:
        """Retrieve all recorded scores."""
        return self.storage.load(self.scores_file)
