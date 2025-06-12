import unittest
import os
import tempfile
import shutil
from datetime import datetime
from src.utils.file_handler import FileHandler
from src.utils.exceptions import FileOperationError, PDFProcessingError

class TestFileHandler(unittest.TestCase):
    """
    Testy jednostkowe dla klasy FileHandler
    """
    
    def setUp(self):
        """
        Przygotowanie środowiska testowego.
        Tworzy tymczasowy katalog z przykładowymi plikami.
        """
        # Tworzymy tymczasowy katalog
        self.test_dir = tempfile.mkdtemp()
        
        # Tworzymy strukturę katalogów do testów
        self.subdirs = ['folder1', 'folder2/subfolder']
        for subdir in self.subdirs:
            os.makedirs(os.path.join(self.test_dir, subdir), exist_ok=True)
        
        # Tworzymy przykładowe pliki
        self.test_files = {
            'test1.pdf': b'%PDF-1.4\nTest content',  # Prawidłowy PDF
            'folder1/test2.pdf': b'Invalid content',  # Nieprawidłowy PDF
            'folder2/subfolder/test3.pdf': b'%PDF-1.5\nTest content',  # Prawidłowy PDF
            'not_a_pdf.txt': b'Text content'  # Nie PDF
        }
        
        for file_name, content in self.test_files.items():
            with open(os.path.join(self.test_dir, file_name), 'wb') as f:
                f.write(content)
        
        # Inicjalizujemy FileHandler
        self.file_handler = FileHandler()
    
    def tearDown(self):
        """
        Sprzątanie po testach.
        Usuwa tymczasowy katalog testowy.
        """
        shutil.rmtree(self.test_dir)
    
    def test_init(self):
        """
        Test inicjalizacji klasy FileHandler
        """
        self.assertIsNotNone(self.file_handler.mime)
        self.assertEqual(len(self.file_handler.files), 0)
    
    def test_scan_directory_invalid_path(self):
        """
        Test skanowania nieistniejącego katalogu
        """
        with self.assertRaises(FileOperationError) as context:
            self.file_handler.scan_directory("/nonexistent/path")
        self.assertIn("Katalog nie istnieje", str(context.exception))
    
    def test_scan_directory_recursive(self):
        """
        Test rekursywnego skanowania katalogów
        """
        files = self.file_handler.scan_directory(self.test_dir)
        self.assertEqual(len(files), 3)  # 3 pliki PDF (2 prawidłowe, 1 nieprawidłowy)
        
        valid_files = self.file_handler.get_valid_files()
        self.assertEqual(len(valid_files), 2)  # 2 prawidłowe pliki PDF
        
        invalid_files = self.file_handler.get_invalid_files()
        self.assertEqual(len(invalid_files), 1)  # 1 nieprawidłowy plik PDF
    
    def test_scan_directory_non_recursive(self):
        """
        Test niekursywnego skanowania katalogów
        """
        files = self.file_handler.scan_directory(self.test_dir, recursive=False)
        self.assertEqual(len(files), 1)  # Tylko 1 plik PDF w głównym katalogu
    
    def test_process_file_nonexistent(self):
        """
        Test przetwarzania nieistniejącego pliku
        """
        with self.assertRaises(PDFProcessingError) as context:
            self.file_handler._process_file("/nonexistent/file.pdf")
        self.assertIn("Plik nie istnieje", str(context.exception))
    
    def test_process_file_invalid_pdf(self):
        """
        Test przetwarzania nieprawidłowego pliku PDF
        """
        invalid_pdf = os.path.join(self.test_dir, 'folder1/test2.pdf')
        file_info = self.file_handler._process_file(invalid_pdf)
        self.assertFalse(file_info.is_valid)
        self.assertIsNotNone(file_info.error_message)
    
    def test_process_file_valid_pdf(self):
        """
        Test przetwarzania prawidłowego pliku PDF
        """
        valid_pdf = os.path.join(self.test_dir, 'test1.pdf')
        file_info = self.file_handler._process_file(valid_pdf)
        self.assertTrue(file_info.is_valid)
        self.assertIsNone(file_info.error_message)
    
    def test_check_file_changes(self):
        """
        Test sprawdzania zmian w pliku
        """
        # Najpierw skanujemy katalog
        self.file_handler.scan_directory(self.test_dir)
        
        # Sprawdzamy istniejący plik
        test_file = os.path.join(self.test_dir, 'test1.pdf')
        self.assertFalse(self.file_handler.check_file_changes(test_file))
        
        # Modyfikujemy plik
        with open(test_file, 'wb') as f:
            f.write(b'%PDF-1.4\nModified content')
        
        # Sprawdzamy czy wykryto zmianę
        self.assertTrue(self.file_handler.check_file_changes(test_file))
    
    def test_check_file_changes_error(self):
        """
        Test obsługi błędów podczas sprawdzania zmian
        """
        # Usuwamy plik po zeskanowaniu
        self.file_handler.scan_directory(self.test_dir)
        test_file = os.path.join(self.test_dir, 'test1.pdf')
        os.remove(test_file)
        
        # Sprawdzamy czy zgłoszono błąd
        with self.assertRaises(FileOperationError) as context:
            self.file_handler.check_file_changes(test_file)
        self.assertIn("Błąd podczas sprawdzania modyfikacji pliku", str(context.exception))
    
    def test_get_file_info_nonexistent(self):
        """
        Test pobierania informacji o nieistniejącym pliku
        """
        info = self.file_handler.get_file_info("/nonexistent/file.pdf")
        self.assertIsNone(info)
    
    def test_clear(self):
        """
        Test czyszczenia pamięci podręcznej
        """
        # Najpierw skanujemy katalog
        self.file_handler.scan_directory(self.test_dir)
        self.assertGreater(len(self.file_handler.files), 0)
        
        # Czyścimy pamięć podręczną
        self.file_handler.clear()
        self.assertEqual(len(self.file_handler.files), 0)

if __name__ == '__main__':
    unittest.main() 