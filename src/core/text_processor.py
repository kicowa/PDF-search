from typing import List, Set, Dict, Any
import re
import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from utils.config import config_manager

class TextProcessor:
    """
    Klasa odpowiedzialna za przetwarzanie tekstu.
    Wykonuje tokenizację, usuwanie stop-words, lematyzację itp.
    """
    
    def __init__(self):
        """
        Inicjalizacja procesora tekstu
        """
        # Inicjalizacja komponentów NLTK
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Dodaj słowa specyficzne dla dokumentów PDF
        self.stop_words.update(['page', 'pdf', 'document'])
        
    def preprocess_text(self, text: str) -> str:
        """
        Wstępne przetwarzanie tekstu
        
        Args:
            text: Tekst do przetworzenia
            
        Returns:
            Przetworzony tekst
        """
        # Konwersja na małe litery
        text = text.lower()
        
        # Usunięcie znaków specjalnych i cyfr
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\d+', ' ', text)
        
        # Usunięcie nadmiarowych białych znaków
        text = ' '.join(text.split())
        
        return text
        
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenizacja tekstu
        
        Args:
            text: Tekst do tokenizacji
            
        Returns:
            Lista tokenów
        """
        return word_tokenize(text)
        
    def remove_stop_words(self, tokens: List[str]) -> List[str]:
        """
        Usuwanie stop-words
        
        Args:
            tokens: Lista tokenów
            
        Returns:
            Lista tokenów bez stop-words
        """
        return [token for token in tokens if token not in self.stop_words]
        
    def lemmatize(self, tokens: List[str]) -> List[str]:
        """
        Lematyzacja tokenów
        
        Args:
            tokens: Lista tokenów
            
        Returns:
            Lista zlematyzowanych tokenów
        """
        return [self.lemmatizer.lemmatize(token) for token in tokens]
        
    def process_text(self, text: str) -> List[str]:
        """
        Pełne przetwarzanie tekstu
        
        Args:
            text: Tekst do przetworzenia
            
        Returns:
            Lista przetworzonych tokenów
        """
        # Wstępne przetwarzanie
        text = self.preprocess_text(text)
        
        # Tokenizacja
        tokens = self.tokenize(text)
        
        # Usuwanie stop-words
        tokens = self.remove_stop_words(tokens)
        
        # Lematyzacja
        tokens = self.lemmatize(tokens)
        
        return tokens
        
    def extract_keywords(self, text: str, top_n: int = None) -> Dict[str, int]:
        """
        Wydobywa słowa kluczowe z tekstu
        
        Args:
            text: Tekst do analizy
            top_n: Liczba najważniejszych słów do zwrócenia
            
        Returns:
            Słownik {słowo: częstość}
        """
        # Przetwarzanie tekstu
        tokens = self.process_text(text)
        
        # Zliczanie częstości
        freq_dict = {}
        for token in tokens:
            freq_dict[token] = freq_dict.get(token, 0) + 1
            
        # Sortowanie po częstości
        sorted_words = sorted(
            freq_dict.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Zwracamy top_n słów lub wszystkie
        if top_n:
            sorted_words = sorted_words[:top_n]
            
        return dict(sorted_words)
        
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Oblicza podobieństwo między dwoma tekstami
        
        Args:
            text1: Pierwszy tekst
            text2: Drugi tekst
            
        Returns:
            Wartość podobieństwa (0-1)
        """
        # Przetwarzanie tekstów
        tokens1 = set(self.process_text(text1))
        tokens2 = set(self.process_text(text2))
        
        # Obliczanie współczynnika Jaccarda
        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))
        
        if union == 0:
            return 0.0
            
        return intersection / union
        
    def find_phrase_matches(self, text: str, phrase: str) -> List[int]:
        """
        Znajduje wystąpienia frazy w tekście
        
        Args:
            text: Tekst do przeszukania
            phrase: Fraza do znalezienia
            
        Returns:
            Lista indeksów początków znalezionych fraz
        """
        # Najpierw szukamy dokładnego dopasowania
        matches = []
        start = 0
        while True:
            index = text.find(phrase, start)
            if index != -1:
                matches.append(index)
                start = index + 1
            else:
                break
                
        # Jeśli nie znaleziono dokładnych dopasowań, szukamy z ignorowaniem wielkości liter
        if not matches:
            text_lower = text.lower()
            phrase_lower = phrase.lower()
            start = 0
            while True:
                index = text_lower.find(phrase_lower, start)
                if index != -1:
                    matches.append(index)
                    start = index + 1
                else:
                    break
                    
        return matches

    def calculate_term_importance(self, term: str, doc_count: int, total_docs: int) -> float:
        """
        Oblicza ważność terminu na podstawie IDF (Inverse Document Frequency).
        
        Args:
            term (str): Term do obliczenia ważności
            doc_count (int): Liczba dokumentów zawierających term
            total_docs (int): Całkowita liczba dokumentów
            
        Returns:
            float: Ważność terminu (IDF)
        """
        if doc_count == 0 or total_docs == 0:
            return 0.0
            
        # Dodajemy 1 do obu wartości aby uniknąć dzielenia przez zero
        # i logarytmu z zera
        return math.log((total_docs + 1) / (doc_count + 1)) + 1 