"""Dictionary service using Datamuse as the primary API."""

import json
import re
from typing import Optional, List

import requests
from urllib.parse import quote

from ..models.word import Word
from ..storage.json_storage import JSONStorage


class DictionaryClient:
    """Fetch vocabulary data from online dictionary APIs."""

    DATAMUSE_URL = "https://api.datamuse.com/words"
    DICTIONARY_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"

    def __init__(self, storage: Optional[JSONStorage] = None) -> None:
        self.storage = storage or JSONStorage()

    def get_word(self, query: str) -> Optional[Word]:
        """
        Search for a word.

        Datamuse is the primary API.
        DictionaryAPI.dev is used as a backup.
        """

        if not query or not query.strip():
            raise ValueError("Word input cannot be empty")

        cleaned = self._clean_query(query)

        if not cleaned:
            raise ValueError("Word input is invalid after cleaning")

        # -------------------------------------------------
        # 1. DATAMUSE - PRIMARY API
        # -------------------------------------------------
        word = self._get_from_datamuse(cleaned)

        if word:
            print(f"Found '{cleaned}' using Datamuse.")
            return word

        # -------------------------------------------------
        # 2. DICTIONARYAPI.DEV - BACKUP API
        # -------------------------------------------------
        print(f"Datamuse could not find '{cleaned}'. Trying backup API...")

        try:
            response = requests.get(
                f"{self.DICTIONARY_API_URL}{quote(cleaned)}",
                timeout=5,
            )

            response.raise_for_status()

            data = response.json()

            if isinstance(data, list) and data:
                word = self._parse_dictionary_api(data, cleaned)

                if word:
                    print(f"Found '{cleaned}' using DictionaryAPI.")
                    return word

        except requests.RequestException as exc:
            print(f"DictionaryAPI unavailable: {exc}")

        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            print(f"Failed to parse DictionaryAPI response: {exc}")

        # -------------------------------------------------
        # 3. NOTHING FOUND
        # -------------------------------------------------
        print(f"Word '{cleaned}' was not found.")

        return None

    # =====================================================
    # DATAMUSE
    # =====================================================

    def _get_from_datamuse(self, term: str) -> Optional[Word]:
        """Get word information from Datamuse."""

        try:
            response = requests.get(
                self.DATAMUSE_URL,
                params={
                    "sp": term,
                    "md": "dpr",
                    "max": 5,
                    "ipa": "1",
                },
                timeout=5,
            )

            response.raise_for_status()

            data = response.json()

            if not isinstance(data, list) or not data:
                return None

            # Look for an exact match.
            exact_match = None

            for item in data:
                if item.get("word", "").lower() == term.lower():
                    exact_match = item
                    break

            if exact_match is None:
                return None

            # -------------------------------------------------
            # Definition
            # -------------------------------------------------

            definition = ""

            definitions = exact_match.get("defs", [])

            if definitions:
                # Datamuse definitions are usually:
                # "n\tdefinition here"
                first_definition = definitions[0]

                if "\t" in first_definition:
                    definition = first_definition.split("\t", 1)[1]
                else:
                    definition = first_definition

            # -------------------------------------------------
            # Pronunciation
            # -------------------------------------------------

            pronunciation = None

            tags = exact_match.get("tags", [])

            for tag in tags:
                if tag.startswith("pron:"):
                    pronunciation = tag.replace("pron:", "", 1)
                    break

            # -------------------------------------------------
            # Synonyms
            # -------------------------------------------------

            synonyms = self._get_datamuse_related(
                term,
                "rel_syn",
            )

            # -------------------------------------------------
            # Antonyms
            # -------------------------------------------------

            antonyms = self._get_datamuse_related(
                term,
                "rel_ant",
            )

            # If Datamuse somehow has no definition,
            # don't treat it as a successful dictionary result.
            if not definition:
                return None

            return Word(
                term=term,
                pronunciation=pronunciation,
                definition=definition,
                synonyms=synonyms[:10],
                antonyms=antonyms[:10],
                ai_explanation=None,
                memory_trick=None,
            )

        except requests.RequestException as exc:
            print(f"Datamuse unavailable: {exc}")

        except (ValueError, KeyError, IndexError, TypeError) as exc:
            print(f"Failed to parse Datamuse response: {exc}")

        return None

    def _get_datamuse_related(
        self,
        term: str,
        relation: str,
    ) -> List[str]:
        """Get related words from Datamuse."""

        try:
            response = requests.get(
                self.DATAMUSE_URL,
                params={
                    relation: term,
                    "max": 10,
                },
                timeout=5,
            )

            response.raise_for_status()

            data = response.json()

            if not isinstance(data, list):
                return []

            words = []

            for item in data:
                word = item.get("word")

                if word and word.lower() != term.lower():
                    words.append(word)

            return words

        except requests.RequestException as exc:
            print(f"Datamuse related-word request failed: {exc}")
            return []

        except (ValueError, TypeError):
            return []

    # =====================================================
    # DICTIONARYAPI.DEV
    # =====================================================

    def _parse_dictionary_api(
        self,
        data: list,
        term: str,
    ) -> Optional[Word]:
        """Convert DictionaryAPI.dev response into a Word object."""

        if not data:
            return None

        entry = data[0]

        # -------------------------------------------------
        # Pronunciation
        # -------------------------------------------------

        pronunciation = None

        for phonetic in entry.get("phonetics", []):
            if phonetic.get("text"):
                pronunciation = phonetic["text"]
                break

        # -------------------------------------------------
        # Definitions
        # -------------------------------------------------

        meanings = entry.get("meanings", [])

        definition = ""

        synonyms: List[str] = []
        antonyms: List[str] = []

        if meanings:
            first_meaning = meanings[0]

            definitions = first_meaning.get(
                "definitions",
                [],
            )

            if definitions:
                definition = definitions[0].get(
                    "definition",
                    "",
                )

            synonyms.extend(
                first_meaning.get(
                    "synonyms",
                    [],
                )
            )

            antonyms.extend(
                first_meaning.get(
                    "antonyms",
                    [],
                )
            )

            # Collect synonyms and antonyms from
            # additional meanings as well.
            for meaning in meanings[1:]:
                synonyms.extend(
                    meaning.get(
                        "synonyms",
                        [],
                    )
                )

                antonyms.extend(
                    meaning.get(
                        "antonyms",
                        [],
                    )
                )

        return Word(
            term=term,
            pronunciation=pronunciation,
            definition=definition,
            synonyms=list(dict.fromkeys(synonyms))[:10],
            antonyms=list(dict.fromkeys(antonyms))[:10],
            ai_explanation=None,
            memory_trick=None,
        )

    # =====================================================
    # INPUT CLEANING
    # =====================================================

    def _clean_query(self, query: str) -> str:
        """Clean the user's search input."""

        cleaned = re.sub(
            r"[^a-zA-Z]",
            "",
            query.strip(),
        )

        return cleaned.lower()