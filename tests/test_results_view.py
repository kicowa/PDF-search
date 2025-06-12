import unittest
import tkinter as tk
from src.ui.results_view import ResultsView, SearchResult

class TestResultsView(unittest.TestCase):
    """
    Testy jednostkowe dla klasy ResultsView
    """
    
    def setUp(self):
        """
        Przygotowanie środowiska testowego
        """
        self.root = tk.Tk()
        self.view = ResultsView(self.root)
        
        # Przykładowe wyniki wyszukiwania
        self.test_results = [
            SearchResult(
                file_path="/test/doc1.pdf",
                title="Test Document 1",
                score=0.8,
                matches=["Fragment 1", "Fragment 2"],
                page_count=10
            ),
            SearchResult(
                file_path="/test/doc2.pdf",
                title="Test Document 2",
                score=0.6,
                matches=["Fragment 3"],
                page_count=5
            )
        ]
    
    def tearDown(self):
        """
        Sprzątanie po testach
        """
        self.root.destroy()
    
    def test_set_results(self):
        """
        Test ustawiania wyników wyszukiwania
        """
        self.view.set_results(self.test_results)
        
        # Sprawdzamy czy wyniki zostały dodane do tabeli
        items = self.view.tree.get_children()
        self.assertEqual(len(items), 2)
        
        # Sprawdzamy wartości w pierwszym wierszu
        values = self.view.tree.item(items[0])["values"]
        self.assertEqual(values[0], "Test Document 1")
        self.assertEqual(values[1], "80.00%")
        self.assertEqual(values[2], 10)
        self.assertEqual(values[3], "/test/doc1.pdf")
    
    def test_sort_by_score(self):
        """
        Test sortowania według trafności
        """
        self.view.set_results(self.test_results)
        
        # Sortujemy według trafności (domyślnie malejąco)
        self.view._sort_by("score")
        items = self.view.tree.get_children()
        
        # Sprawdzamy czy wyniki są posortowane
        values1 = self.view.tree.item(items[0])["values"]
        values2 = self.view.tree.item(items[1])["values"]
        self.assertEqual(values1[0], "Test Document 1")  # 80%
        self.assertEqual(values2[0], "Test Document 2")  # 60%
        
        # Zmieniamy kierunek sortowania
        self.view._sort_by("score")
        items = self.view.tree.get_children()
        values1 = self.view.tree.item(items[0])["values"]
        values2 = self.view.tree.item(items[1])["values"]
        self.assertEqual(values1[0], "Test Document 2")  # 60%
        self.assertEqual(values2[0], "Test Document 1")  # 80%
    
    def test_sort_by_title(self):
        """
        Test sortowania według tytułu
        """
        self.view.set_results(self.test_results)
        
        # Sortujemy według tytułu
        self.view._sort_by("title")
        items = self.view.tree.get_children()
        
        # Sprawdzamy czy wyniki są posortowane alfabetycznie
        values1 = self.view.tree.item(items[0])["values"]
        values2 = self.view.tree.item(items[1])["values"]
        self.assertEqual(values1[0], "Test Document 1")
        self.assertEqual(values2[0], "Test Document 2")
    
    def test_clear(self):
        """
        Test czyszczenia widoku
        """
        self.view.set_results(self.test_results)
        self.view.clear()
        
        # Sprawdzamy czy tabela jest pusta
        items = self.view.tree.get_children()
        self.assertEqual(len(items), 0)
        
        # Sprawdzamy czy podgląd jest pusty
        text = self.view.preview_text.get(1.0, tk.END).strip()
        self.assertEqual(text, "")

if __name__ == '__main__':
    unittest.main() 