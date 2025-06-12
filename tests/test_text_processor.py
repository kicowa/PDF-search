import unittest
from src.core.text_processor import TextProcessor, ProcessedDocument

class TestTextProcessor(unittest.TestCase):
    """
    Testy jednostkowe dla klasy TextProcessor
    """
    
    def setUp(self):
        """
        Przygotowanie środowiska testowego
        """
        self.processor = TextProcessor()
        self.test_text = """
        To jest przykładowy tekst do testów.
        Zawiera on różne słowa oraz znaki specjalne!
        Niektóre słowa się powtarzają, a niektóre nie.
        To jest kolejne zdanie z powtórzeniem.
        """
    
    def test_normalize_text(self):
        """
        Test normalizacji tekstu
        """
        normalized = self.processor._normalize_text(self.test_text)
        
        # Sprawdzamy czy tekst jest małymi literami
        self.assertEqual(normalized, normalized.lower())
        
        # Sprawdzamy czy usunięto znaki specjalne
        self.assertNotIn('!', normalized)
        self.assertNotIn('.', normalized)
        
        # Sprawdzamy czy nie ma nadmiarowych spacji
        self.assertNotIn('  ', normalized)
        
        # Sprawdzamy czy zachowano polskie znaki
        self.assertIn('ó', normalized)  # w słowie "różne"
    
    def test_filter_tokens(self):
        """
        Test filtrowania tokenów
        """
        tokens = ['to', 'jest', 'przykładowy', 'tekst', 'oraz', 'i', 'a']
        filtered = self.processor._filter_tokens(tokens)
        
        # Sprawdzamy czy usunięto stop words
        self.assertNotIn('to', filtered)
        self.assertNotIn('jest', filtered)
        self.assertNotIn('oraz', filtered)
        self.assertNotIn('i', filtered)
        self.assertNotIn('a', filtered)
        
        # Sprawdzamy czy pozostały ważne słowa
        self.assertIn('przykładowy', filtered)
        self.assertIn('tekst', filtered)
    
    def test_process_text(self):
        """
        Test przetwarzania całego tekstu
        """
        processed = self.processor.process_text(self.test_text)
        
        # Sprawdzamy czy zwrócono obiekt ProcessedDocument
        self.assertIsInstance(processed, ProcessedDocument)
        
        # Sprawdzamy czy zachowano oryginalny tekst
        self.assertEqual(processed.original_text, self.test_text)
        
        # Sprawdzamy czy utworzono tokeny
        self.assertIsInstance(processed.tokens, list)
        self.assertTrue(len(processed.tokens) > 0)
        
        # Sprawdzamy czy policzono częstotliwości
        self.assertTrue(len(processed.term_frequencies) > 0)
        
        # Sprawdzamy czy utworzono zbiór unikalnych terminów
        self.assertIsInstance(processed.unique_terms, set)
        self.assertTrue(len(processed.unique_terms) > 0)
        
        # Sprawdzamy czy usunięto stop words
        self.assertNotIn('to', processed.tokens)
        self.assertNotIn('jest', processed.tokens)
        self.assertNotIn('oraz', processed.tokens)
        
        # Sprawdzamy czy zachowano ważne słowa
        self.assertIn('przykładowy', processed.tokens)
        self.assertIn('tekst', processed.tokens)
    
    def test_find_phrase_matches(self):
        """
        Test wyszukiwania fraz w tekście
        """
        processed = self.processor.process_text(self.test_text)
        
        # Test dokładnego dopasowania
        matches = self.processor.find_phrase_matches(processed, "przykładowy tekst")
        self.assertTrue(len(matches) > 0)
        
        # Test braku dopasowania
        matches = self.processor.find_phrase_matches(processed, "nieistniejąca fraza")
        self.assertEqual(len(matches), 0)
        
        # Test dopasowania z różną wielkością liter
        matches = self.processor.find_phrase_matches(processed, "PRZYKŁADOWY tekst")
        self.assertTrue(len(matches) > 0)
        
        # Test dopasowania frazy ze stop words (powinny zostać usunięte)
        matches = self.processor.find_phrase_matches(processed, "to jest przykładowy")
        self.assertTrue(len(matches) > 0)

if __name__ == '__main__':
    unittest.main() 