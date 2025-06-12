import unittest
import os
import tempfile
import shutil
from datetime import datetime
import nltk
from src.utils.index_storage import IndexStorage
from src.core.search_engine import DocumentIndex
from src.core.text_processor import TextProcessor, ProcessedDocument

# Pobierz wymagane dane NLTK
nltk.download('punkt')
nltk.download('stopwords')

class TestIndexStorage(unittest.TestCase):
    """
    Testy jednostkowe dla klasy IndexStorage
    """
    
    def setUp(self):
        """
        Przygotowanie środowiska testowego
        """
        # Tworzymy tymczasowy katalog na indeks
        self.temp_dir = tempfile.mkdtemp()
        
        # Tworzymy instancję IndexStorage z tymczasowym katalogiem
        self.storage = IndexStorage()
        self.storage.index_dir = self.temp_dir
        self.storage.index_file = os.path.join(self.temp_dir, "search_index.pkl")
        self.storage.metadata_file = os.path.join(self.temp_dir, "metadata.json")
        
        # Tworzymy przykładowe dokumenty do testów
        text_processor = TextProcessor()
        self.test_documents = {
            "test1.pdf": DocumentIndex(
                file_path="test1.pdf",
                processed_doc=text_processor.process_text("This is a test document"),
                title="Test Document 1",
                page_count=1,
                content="This is a test document"
            ),
            "test2.pdf": DocumentIndex(
                file_path="test2.pdf",
                processed_doc=text_processor.process_text("Another test document"),
                title="Test Document 2",
                page_count=1,
                content="Another test document"
            )
        }
    
    def tearDown(self):
        """
        Sprzątanie po testach
        """
        # Usuwamy tymczasowy katalog
        shutil.rmtree(self.temp_dir)
    
    def test_save_and_load_index(self):
        """
        Test zapisywania i wczytywania indeksu
        """
        # Zapisujemy indeks
        self.assertTrue(self.storage.save_index(self.test_documents))
        
        # Wczytujemy indeks
        loaded_docs = self.storage.load_index()
        
        # Sprawdzamy czy dane są poprawne
        self.assertIsNotNone(loaded_docs)
        self.assertEqual(len(loaded_docs), 2)
        self.assertIn("test1.pdf", loaded_docs)
        self.assertIn("test2.pdf", loaded_docs)
        
        # Sprawdzamy zawartość dokumentów
        doc1 = loaded_docs["test1.pdf"]
        self.assertEqual(doc1.title, "Test Document 1")
        self.assertEqual(doc1.content, "This is a test document")
    
    def test_update_index(self):
        """
        Test aktualizacji indeksu
        """
        # Zapisujemy początkowy indeks
        self.assertTrue(self.storage.save_index(self.test_documents))
        
        # Tworzymy nowy dokument do dodania
        text_processor = TextProcessor()
        new_doc = DocumentIndex(
            file_path="test3.pdf",
            processed_doc=text_processor.process_text("New test document"),
            title="Test Document 3",
            page_count=1,
            content="New test document"
        )
        
        # Aktualizujemy indeks
        self.assertTrue(self.storage.update_index({"test3.pdf": new_doc}))
        
        # Wczytujemy zaktualizowany indeks
        loaded_docs = self.storage.load_index()
        
        # Sprawdzamy czy wszystkie dokumenty są obecne
        self.assertEqual(len(loaded_docs), 3)
        self.assertIn("test1.pdf", loaded_docs)
        self.assertIn("test2.pdf", loaded_docs)
        self.assertIn("test3.pdf", loaded_docs)
    
    def test_get_index_info(self):
        """
        Test pobierania informacji o indeksie
        """
        # Zapisujemy indeks
        self.assertTrue(self.storage.save_index(self.test_documents))
        
        # Pobieramy informacje
        info = self.storage.get_index_info()
        
        # Sprawdzamy czy informacje są poprawne
        self.assertIsNotNone(info)
        self.assertEqual(info["version"], "1.0")
        self.assertEqual(info["document_count"], 2)
        self.assertIn("last_updated", info)
        self.assertEqual(len(info["document_paths"]), 2)
    
    def test_clear_index(self):
        """
        Test czyszczenia indeksu
        """
        # Zapisujemy indeks
        self.assertTrue(self.storage.save_index(self.test_documents))
        
        # Czyścimy indeks
        self.assertTrue(self.storage.clear_index())
        
        # Sprawdzamy czy pliki zostały usunięte
        self.assertFalse(os.path.exists(self.storage.index_file))
        self.assertFalse(os.path.exists(self.storage.metadata_file))
        
        # Sprawdzamy czy wczytanie zwraca None
        self.assertIsNone(self.storage.load_index())
    
    def test_load_nonexistent_index(self):
        """
        Test wczytywania nieistniejącego indeksu
        """
        # Próbujemy wczytać nieistniejący indeks
        loaded_docs = self.storage.load_index()
        
        # Sprawdzamy czy zwrócono None
        self.assertIsNone(loaded_docs)
    
    def test_corrupted_index(self):
        """
        Test obsługi uszkodzonego indeksu
        """
        # Zapisujemy nieprawidłowe dane do pliku indeksu
        with open(self.storage.index_file, 'wb') as f:
            f.write(b'invalid data')
        
        # Zapisujemy nieprawidłowe metadane
        with open(self.storage.metadata_file, 'w') as f:
            f.write('invalid json')
        
        # Próbujemy wczytać uszkodzony indeks
        loaded_docs = self.storage.load_index()
        
        # Sprawdzamy czy zwrócono None
        self.assertIsNone(loaded_docs)

if __name__ == '__main__':
    unittest.main() 