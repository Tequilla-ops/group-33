"""Word data model used throughout the application."""

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Word:
    """Represents a vocabulary word with its metadata.

    Attributes
    ----------
    term: The word text.
    pronunciation: Optional[str]  # Phonetic spelling (e.g. "/example/")
    definition: Optional[str]
    synonyms: List[str]
    antonyms: List[str]
    ai_explanation: Optional[str] = None
    memory_trick: Optional[str] = None
    examples: List[str] = field(default_factory=list)
    ai_example: Optional[str] = None
    """

    term: str
    pronunciation: Optional[str]
    definition: Optional[str]
    synonyms: List[str]
    antonyms: List[str]
    ai_explanation: Optional[str] = None
    memory_trick: Optional[str] = None
    examples: List[str] = field(default_factory=list)
    ai_example: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.term or not self.term.strip():
            raise ValueError("Word term cannot be empty")
        if len(self.term) < 2:
            raise ValueError("Word term must be at least 2 characters")