# Vocabulary Learning Application

## Overview
A command-line tool that lets users look up words, generate
AI-assisted explanations, create flashcards, review them with a
basic spaced-repetition system, and take quizzes.

It demonstrates advanced Python concepts required for the course:
- **File handling** (JSON persistence)
- **Exception handling**
- **Regular expressions** for input validation
- **Object-oriented design** (Word, Flashcard, services, storage)
- **External API consumption** (free dictionary API and optional AI service)

## Features
1. Search a word – definition, phonetics, examples, synonyms & antonyms.
2. AI-generated plain-language explanation, memory trick and optional example.
3. Save words and generate flashcards.
4. Review flashcards using a simple spaced-repetition algorithm.
5. Take quizzes built from saved words.
6. All data persists between runs (JSON files).

## Project Structure
```
vocabulary_app/
+- main.py                     # entry point / CLI
+- models/
¦   +- __init__.py
¦   +- word.py                # Word dataclass
¦   +- flashcard.py           # Flashcard dataclass
+- services/
¦   +- __init__.py
¦   +- dictionary_client.py   # Wrapper around dictionaryapi.dev
¦   +- ai_helper.py           # Optional AI generation
¦   +- quiz_generator.py      # Quiz logic
¦   +- spaced_repetition.py  # SR algorithm
+- storage/
¦   +- __init__.py
¦   +- json_storage.py        # Generic JSON load / save
+- data/
¦   +- words.json            # saved words
¦   +- flashcards.json       # saved flashcards
¦   +- scores.json           # quiz scores
+- tests/                     # unit tests (run with pytest)
¦   +- __init__.py
¦   +- test_word.py
¦   +- test_storage.py
¦   +- test_spaced.py
¦   +- test_quiz.py
+- requirements.txt
```

## Installation
```bash
# Create a virtual environment (optional but recommended)
python -m venv .venv
.venv\Scripts\activate   # Windows PowerShell
pip install -r requirements.txt
```

## Environment Variables
- `AI_API_KEY` – API key for the optional AI service (e.g. OpenAI). If not set, AI features are disabled but the rest of the app works.

## Running the Application
```bash
python -m vocabulary_app.main
```

## Running Tests
```bash
pip install pytest
pytest
```

## How It Works
* **Dictionary API** – `DictionaryClient` calls `https://api.dictionaryapi.dev/api/v2/entries/en/<word>`
  and maps the JSON to a `Word` instance. Network or parsing errors are caught and reported.
* **AI Integration** – `AIHelper` looks for `AI_API_KEY`. When present it sends a prompt to the AI
  (implementation left generic). If the request fails or the key is missing, the helper returns
  `None` and the UI shows a fallback message.
* **Spaced Repetition** – each `Flashcard` stores `review_count`, `difficulty` (0-2) and `next_review_date`.
  After a review the interval is increased (`1, 2, 4, 7 …` days) – simple enough for a demo.
* **Quiz** – multiple-choice questions are generated from saved words. Scores are stored with a
  timestamp in `data/scores.json`.

Enjoy learning new vocabulary!
