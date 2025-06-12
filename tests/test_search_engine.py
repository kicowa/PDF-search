import unittest
from src.core.search_engine import SearchEngine, SearchResult

class TestSearchEngine(unittest.TestCase):
    """
    Testy jednostkowe dla klasy SearchEngine
    """
    
    def setUp(self):
        """
        Przygotowanie środowiska testowego
        """
        self.engine = SearchEngine()
        
        # Przykładowe dokumenty do testów
        self.docs = {
            "doc1.pdf": (
                "To jest przykładowy dokument o programowaniu w Pythonie. "
                "Python jest językiem wysokiego poziomu.",
                "Python Programming",
                10
            ),
            "doc2.pdf": (
                "JavaScript jest językiem programowania używanym w przeglądarkach. "
                "Programowanie w JavaScript jest popularne.",
                "JavaScript Basics",
                15
            ),
            "doc3.pdf": (
                "Python i JavaScript to popularne języki programowania. "
                "Oba języki są często używane w projektach.",
                "Programming Languages",
                20
            )
        }
        
        # Indeksujemy dokumenty
        for file_path, (text, title, pages) in self.docs.items():
            self.engine.index_document(file_path, text, title, pages)
    
    def test_index_document(self):
        """
        Test indeksowania dokumentów
        """
        # Sprawdzamy czy wszystkie dokumenty zostały zindeksowane
        self.assertEqual(self.engine.get_document_count(), 3)
        
        # Sprawdzamy czy dokumenty są w indeksie
        self.assertIn("doc1.pdf", self.engine.documents)
        self.assertIn("doc2.pdf", self.engine.documents)
        self.assertIn("doc3.pdf", self.engine.documents)
        
        # Sprawdzamy czy tytuły są poprawne
        self.assertEqual(
            self.engine.documents["doc1.pdf"].title,
            "Python Programming"
        )
    
    def test_search_exact_match(self):
        """
        Test wyszukiwania dokładnych dopasowań
        """
        results = self.engine.search("Python")
        
        # Powinniśmy znaleźć dwa dokumenty
        self.assertEqual(len(results), 2)
        
        # Sprawdzamy czy wyniki są posortowane według trafności
        self.assertGreater(results[0].score, results[1].score)
        
        # Sprawdzamy czy znaleziono właściwe dokumenty
        paths = {r.file_path for r in results}
        self.assertIn("doc1.pdf", paths)
        self.assertIn("doc3.pdf", paths)
    
    def test_search_multiple_terms(self):
        """
        Test wyszukiwania wielu terminów
        """
        results = self.engine.search("Python JavaScript")
        
        # Powinniśmy znaleźć wszystkie dokumenty
        self.assertEqual(len(results), 3)
        
        # Dokument zawierający oba terminy powinien być pierwszy
        self.assertEqual(results[0].file_path, "doc3.pdf")
    
    def test_search_no_results(self):
        """
        Test wyszukiwania bez wyników
        """
        results = self.engine.search("nieistniejący tekst")
        self.assertEqual(len(results), 0)
    
    def test_search_with_context(self):
        """
        Test wyszukiwania z kontekstem
        """
        results = self.engine.search("Python")
        
        # Sprawdzamy czy mamy fragmenty tekstu
        self.assertTrue(all(len(r.matches) > 0 for r in results))
        
        # Sprawdzamy czy fragmenty zawierają szukany term
        for result in results:
            for match in result.matches:
                self.assertIn("python", match.lower())
    
    def test_clear_index(self):
        """
        Test czyszczenia indeksu
        """
        self.engine.clear_index()
        
        # Sprawdzamy czy indeks jest pusty
        self.assertEqual(self.engine.get_document_count(), 0)
        self.assertEqual(len(self.engine.documents), 0)
        self.assertEqual(len(self.engine.term_index), 0)

if __name__ == '__main__':
    unittest.main() 