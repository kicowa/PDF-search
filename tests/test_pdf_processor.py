import unittest
import os
import tempfile
from datetime import datetime
from PyPDF2 import PdfWriter, PdfReader
from io import BytesIO
from reportlab.pdfgen import canvas
from src.core.pdf_processor import PDFProcessor, PDFMetadata

class TestPDFProcessor(unittest.TestCase):
    """
    Testy jednostkowe dla klasy PDFProcessor
    """
    
    def setUp(self):
        """
        Przygotowanie środowiska testowego.
        Tworzy tymczasowy plik PDF do testów.
        """
        self.processor = PDFProcessor()
        
        # Tworzymy tymczasowy plik PDF
        self.test_dir = tempfile.mkdtemp()
        self.test_pdf_path = os.path.join(self.test_dir, "test.pdf")
        
        # Tworzymy PDF używając reportlab
        buffer = BytesIO()
        c = canvas.Canvas(buffer)
        c.drawString(100, 750, "To jest testowy dokument PDF.")
        c.save()
        buffer.seek(0)
        
        # Konwertujemy do PyPDF2 i dodajemy metadane
        reader = PdfReader(buffer)
        writer = PdfWriter()
        writer.add_page(reader.pages[0])
        
        # Dodajemy metadane
        metadata = {
            "/Title": "Test PDF",
            "/Author": "Test Author",
            "/Subject": "Test Subject",
            "/CreationDate": "D:20240101000000",
            "/ModDate": "D:20240102000000"
        }
        writer.add_metadata(metadata)
        
        # Zapisujemy plik
        with open(self.test_pdf_path, "wb") as file:
            writer.write(file)
    
    def tearDown(self):
        """
        Sprzątanie po testach.
        Usuwa tymczasowe pliki.
        """
        if os.path.exists(self.test_pdf_path):
            os.remove(self.test_pdf_path)
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)
    
    def test_process_file(self):
        """
        Test przetwarzania pliku PDF
        """
        text, metadata = self.processor.process_file(self.test_pdf_path)
        
        # Sprawdzamy czy tekst został wydobyty
        self.assertIsInstance(text, str)
        self.assertIn("testowy dokument", text.lower())
        
        # Sprawdzamy metadane
        self.assertIsInstance(metadata, PDFMetadata)
        self.assertEqual(metadata.title, "Test PDF")
        self.assertEqual(metadata.author, "Test Author")
        self.assertEqual(metadata.subject, "Test Subject")
        self.assertEqual(metadata.page_count, 1)
        
        # Sprawdzamy daty
        self.assertIsInstance(metadata.creation_date, datetime)
        self.assertEqual(metadata.creation_date.year, 2024)
        self.assertEqual(metadata.creation_date.month, 1)
        self.assertEqual(metadata.creation_date.day, 1)
        
        self.assertIsInstance(metadata.modification_date, datetime)
        self.assertEqual(metadata.modification_date.year, 2024)
        self.assertEqual(metadata.modification_date.month, 1)
        self.assertEqual(metadata.modification_date.day, 2)
    
    def test_invalid_file(self):
        """
        Test obsługi nieprawidłowego pliku
        """
        invalid_path = os.path.join(self.test_dir, "nonexistent.pdf")
        with self.assertRaises(ValueError):
            self.processor.process_file(invalid_path)

if __name__ == '__main__':
    unittest.main() 