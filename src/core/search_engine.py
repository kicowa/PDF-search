from typing import List, Dict, Any
import os
from .pdf_processor import PDFProcessor
from .text_processor import TextProcessor
from utils.file_handler import FileHandler
from utils.config import config_manager
from .models import SearchResult

class SearchEngine:
    """
    Silnik wyszukiwania w dokumentach PDF
    """
    
    def __init__(self):
        """
        Inicjalizacja silnika wyszukiwania
        """
        self.pdf_processor = PDFProcessor()
        self.text_processor = TextProcessor()
        self.file_handler = FileHandler()
        
        # Słownik przechowujący przetworzone dokumenty
        self.documents: Dict[str, str] = {}
        
    def index_document(self, file_path: str) -> None:
        """
        Indeksuje dokument PDF
        
        Args:
            file_path: Ścieżka do pliku PDF
        """
        try:
            # Wydobycie tekstu z PDF
            text = self.pdf_processor.extract_text(file_path)
            
            # Zapisanie tekstu w słowniku
            self.documents[file_path] = text
            
        except Exception as e:
            print(f"Błąd indeksowania dokumentu {file_path}: {str(e)}")
            
    def index_directory(self, directory: str) -> None:
        """
        Indeksuje wszystkie dokumenty PDF w katalogu
        
        Args:
            directory: Ścieżka do katalogu
        """
        # Pobierz listę plików PDF
        pdf_files = self.file_handler.get_pdf_files(directory)
        
        # Indeksuj każdy plik
        for file_path in pdf_files:
            self.index_document(file_path)
            
    def search(self, query: str) -> List[SearchResult]:
        """
        Wyszukuje frazę w zaindeksowanych dokumentach
        
        Args:
            query: Fraza do wyszukania
            
        Returns:
            Lista wyników wyszukiwania
        """
        results = []
        
        for file_path, text in self.documents.items():
            # Znajdujemy wszystkie wystąpienia frazy
            matches = self.text_processor.find_phrase_matches(text, query)
            
            if matches:
                # Dla każdego indeksu, wydobywamy fragment tekstu (kontekst)
                context_matches = []
                for index in matches:
                    # Pobierz fragment tekstu przed i po znalezionym indeksie
                    start = max(0, index - 50)  # 50 znaków przed
                    end = min(len(text), index + len(query) + 50)  # 50 znaków po
                    context = text[start:end].strip()
                    if start > 0:
                        context = "..." + context
                    if end < len(text):
                        context = context + "..."
                    context_matches.append(context)
                
                # Obliczamy wynik podobieństwa
                score = self.text_processor.calculate_similarity(query, text)
                
                # Tworzymy wynik wyszukiwania
                result = SearchResult(
                    file_path=file_path,
                    title=os.path.basename(file_path),
                    score=score,
                    matches=context_matches
                )
                
                results.append(result)
        
        # Sortujemy wyniki po score (malejąco)
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results
        
    def get_document_count(self) -> int:
        """
        Zwraca liczbę zindeksowanych dokumentów
        
        Returns:
            int: Liczba dokumentów
        """
        return len(self.documents)
        
    def clear_index(self) -> None:
        """
        Czyści indeks wyszukiwania
        """
        self.documents.clear() 