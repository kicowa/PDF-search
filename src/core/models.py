from dataclasses import dataclass
from typing import List

@dataclass
class SearchResult:
    """
    Klasa reprezentująca wynik wyszukiwania dokumentu
    """
    file_path: str  # Ścieżka do pliku PDF
    title: str      # Tytuł dokumentu
    score: float    # Wynik podobieństwa (0-1)
    matches: List[str]  # Lista znalezionych fragmentów tekstu 