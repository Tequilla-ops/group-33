"""Main CLI entry point for the Vocabulary Learning Application."""

import os
import sys
from datetime import datetime
from typing import Optional

from vocabulary_app.models.word import Word
from vocabulary_app.models.flashcard import Flashcard
from vocabulary_app.storage.json_storage import JSONStorage
from vocabulary_app.services.dictionary_client import DictionaryClient
from vocabulary_app.services.ai_helper import AIHelper
from vocabulary_app.services.quiz_generator import QuizGenerator
from vocabulary_app.services.spaced_repetition import SpacedRepetitionManager


class VocabularyApp:
    """Terminal user interface and controller for the app."""

    def __init__(self) -> None:
        self.storage = JSONStorage()
        self.dict_client = DictionaryClient(self.storage)
        self.ai_helper = AIHelper()
        self.quiz_gen = QuizGenerator(self.storage)
        self.sr_manager = SpacedRepetitionManager(self.storage)
        
        self.words_file = "data/words.json"
        self.flashcards_file = "data/flashcards.json"

    def run(self) -> None:
        """Run the main application loop."""
        print("========================================")
        print("   VOCABULARY LEARNING APPLICATION      ")
        print("========================================")
        
        while True:
            print("\\nMain Menu:")
            print("1. Search for a word")
            print("2. Saved words")
            print("3. Review flashcards")
            print("4. Take a quiz")
            print("5. View quiz scores")
            print("6. Exit")
            
            choice = input("\\nSelect an option (1-6): ").strip()
            
            if choice == "1":
                self.search_word_flow()
            elif choice == "2":
                self.saved_words_flow()
            elif choice == "3":
                self.review_flashcards_flow()
            elif choice == "4":
                self.take_quiz_flow()
            elif choice == "5":
                self.view_scores_flow()
            elif choice == "6":
                print("\\nGoodbye and happy learning!")
                break
            else:
                print("Invalid option. Please enter a number between 1 and 6.")

    def search_word_flow(self) -> None:
        """Handle word search and AI enhancements."""
        query = input("\\nEnter a word to search: ").strip()
        if not query:
            print("Error: Input cannot be empty.")
            return

        print(f"Searching for '{query}'...")
        word = self.dict_client.get_word(query)
        if not word:
            print(f"Could not find definitions for '{query}'. Please check spelling or try another word.")
            return

        # Generate AI explanation and memory trick
        enhancements = self.ai_helper.generate_enhancements(word.term, word.definition or "")
        word.ai_explanation = enhancements.get("ai_explanation")
        word.memory_trick = enhancements.get("memory_trick")

        self.display_word(word)

        while True:
            print("\\nOptions:")
            print("[S] Save word")
            print("[F] Create flashcard")
            print("[B] Back to main menu")
            
            action = input("Select action: ").strip().upper()
            if action == "S":
                self.save_word_to_storage(word)
            elif action == "F":
                self.save_flashcard_to_storage(word)
            elif action == "B":
                break
            else:
                print("Invalid action. Choose S, F, or B.")

    def display_word(self, word: Word) -> None:
        """Pretty print word details."""
        print("\\n" + "=" * 40)
        print(f"WORD: {word.term.upper()}")
        print("=" * 40)
        print(f"Pronunciation: {word.pronunciation or 'N/A'}")
        print(f"\\nDefinition:\\n{word.definition or 'N/A'}")
        print(f"\\nSynonyms:\\n{', '.join(word.synonyms) if word.synonyms else 'None'}")
        print(f"\\nAntonyms:\\n{', '.join(word.antonyms) if word.antonyms else 'None'}")
        print(f"\\nAI Explanation:\\n{word.ai_explanation or 'N/A'}")
        print(f"\\nMemory Trick:\\n{word.memory_trick or 'N/A'}")
        print("=" * 40)

    def save_word_to_storage(self, word: Word) -> None:
        """Save word to words.json."""
        words = self.storage.load(self.words_file)
        words[word.term] = {
            "term": word.term,
            "pronunciation": word.pronunciation,
            "definition": word.definition,
            "synonyms": word.synonyms,
            "antonyms": word.antonyms,
            "ai_explanation": word.ai_explanation,
            "memory_trick": word.memory_trick,
        }
        if self.storage.save(self.words_file, words):
            print(f"'{word.term}' saved successfully!")
        else:
            print("Failed to save word.")

    def save_flashcard_to_storage(self, word: Word) -> None:
        """Save flashcard to flashcards.json."""
        flashcards = self.storage.load(self.flashcards_file)
        flashcards[word.term] = {
            "word": {
                "term": word.term,
                "pronunciation": word.pronunciation,
                "definition": word.definition,
                "synonyms": word.synonyms,
                "antonyms": word.antonyms,
                "ai_explanation": word.ai_explanation,
                "memory_trick": word.memory_trick,
            },
            "definition": word.definition,
            "difficulty": 1,  # medium default
            "review_count": 0,
            "next_review_date": datetime.now().isoformat(),
            "last_reviewed": datetime.now().isoformat(),
        }
        if self.storage.save(self.flashcards_file, flashcards):
            print(f"Flashcard for '{word.term}' created successfully!")
        else:
            print("Failed to create flashcard.")

    def saved_words_flow(self) -> None:
        """List all saved words."""
        words = self.storage.load(self.words_file)
        if not words:
            print("\\nNo saved words found.")
            return

        print("\\n========================================")
        print("           SAVED WORDS                  ")
        print("========================================")
        for idx, term in enumerate(words.keys(), 1):
            print(f"{idx}. {term.capitalize()}")
        print("=" * 40)

    def review_flashcards_flow(self) -> None:
        """Review saved flashcards with spaced repetition."""
        flashcards = self.storage.load(self.flashcards_file)
        if not flashcards:
            print("\\nNo flashcards found. Create some by searching words!")
            return

        print("\\n========================================")
        print("          FLASHCARD REVIEW              ")
        print("========================================")

        for term, data in list(flashcards.items()):
            print(f"\\nWord: {term.upper()}")
            input("Press Enter to reveal definition...")
            print(f"Definition: {data.get('definition')}")
            
            while True:
                rating = input("Rate your recall [easy / good / hard]: ").strip().lower()
                if rating in ("easy", "good", "hard"):
                    self.sr_manager.review_card(term, rating)
                    break
                print("Invalid rating. Please enter easy, good, or hard.")

        print("\\nFinished reviewing available flashcards!")

    def take_quiz_flow(self) -> None:
        """Take a multiple-choice quiz."""
        words_pool = self.quiz_gen.get_words_for_quiz(count=5)
        if len(words_pool) < 2:
            print("\\nNot enough saved or searchable words to take a quiz. Search & save more words first!")
            return

        print("\\n========================================")
        print("             VOCABULARY QUIZ            ")
        print("========================================")

        correct_count = 0
        total_questions = len(words_pool)

        for idx, word in enumerate(words_pool, 1):
            q_data = self.quiz_gen.generate_question(word)
            print(f"\\nQuestion {idx}: {q_data['prompt']}")
            for opt_idx, opt in enumerate(q_data['options']):
                print(f"  {opt_idx + 1}. {opt}")

            while True:
                ans = input("Your answer (enter option number): ").strip()
                if ans.isdigit() and 1 <= int(ans) <= len(q_data['options']):
                    chosen_idx = int(ans) - 1
                    break
                print("Invalid answer choice. Try again.")

            if chosen_idx == q_data['correct_index']:
                print("Correct!")
                correct_count += 1
            else:
                print(f"Incorrect. The correct word was: {q_data['word']}")

        percentage = (correct_count / total_questions) * 100
        print(f"\\nQuiz finished! Score: {correct_count}/{total_questions} ({percentage:.1f}%)")

        score_record = {
            "total": total_questions,
            "correct": correct_count,
            "percentage": percentage,
            "timestamp": datetime.now().isoformat(),
        }
        self.quiz_gen.record_score(score_record)

    def view_scores_flow(self) -> None:
        """View recorded quiz scores."""
        scores = self.quiz_gen.get_scores()
        if not scores:
            print("\\nNo quiz scores recorded yet.")
            return

        print("\\n========================================")
        print("            QUIZ SCORES HISTORY         ")
        print("========================================")
        for ts, data in scores.items():
            print(f"Date: {ts[:19]} | Score: {data.get('correct')}/{data.get('total')} ({data.get('percentage'):.1f}%)")
        print("=" * 40)


if __name__ == "__main__":
    app = VocabularyApp()
    app.run()
