from typing import Dict, Optional, Tuple
import PyPDF2
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PDFMetadata:
    """
    Klasa przechowująca metadane dokumentu PDF
    """
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    page_count: int = 0

class PDFProcessor:
    """
    Klasa odpowiedzialna za przetwarzanie dokumentów PDF.
    Wydobywa tekst i metadane z plików PDF.
    """

    def __init__(self):
        """
        Inicjalizacja procesora PDF
        """
        self._current_file = None
        self._current_reader = None

    def extract_text(self, file_path: str) -> str:
        """
        Wydobywa tekst z pliku PDF.
        
        Args:
            file_path (str): Ścieżka do pliku PDF
            
        Returns:
            str: Wydobyty tekst
            
        Raises:
            ValueError: Gdy plik nie może zostać przetworzony
        """
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text_parts = []
                for page in reader.pages:
                    try:
                        text = page.extract_text()
                        if text:
                            text_parts.append(text)
                    except Exception as e:
                        print(f"Ostrzeżenie: Nie można wydobyć tekstu ze strony: {str(e)}")
                return "\n".join(text_parts)
        except Exception as e:
            raise ValueError(f"Nie można przetworzyć pliku PDF: {str(e)}")

    def extract_title(self, file_path: str) -> str:
        """
        Wydobywa tytuł z pliku PDF.
        
        Args:
            file_path (str): Ścieżka do pliku PDF
            
        Returns:
            str: Tytuł dokumentu lub nazwa pliku jeśli brak tytułu
        """
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                if '/Title' in reader.metadata:
                    return reader.metadata['/Title']
                return file_path.split('/')[-1]
        except:
            return file_path.split('/')[-1]

    def extract_page_count(self, file_path: str) -> int:
        """
        Zwraca liczbę stron w dokumencie PDF.
        
        Args:
            file_path (str): Ścieżka do pliku PDF
            
        Returns:
            int: Liczba stron
        """
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                return len(reader.pages)
        except:
            return 0

    def process_file(self, file_path: str) -> Tuple[str, PDFMetadata]:
        """
        Przetwarza plik PDF, wydobywając tekst i metadane.
        
        Args:
            file_path (str): Ścieżka do pliku PDF
            
        Returns:
            Tuple[str, PDFMetadata]: Krotka zawierająca wydobyty tekst i metadane
            
        Raises:
            ValueError: Gdy plik nie może zostać przetworzony
        """
        try:
            with open(file_path, 'rb') as file:
                self._current_reader = PyPDF2.PdfReader(file)
                text = self._extract_text()
                metadata = self._extract_metadata()
                return text, metadata
        except Exception as e:
            raise ValueError(f"Nie można przetworzyć pliku PDF: {str(e)}")
        finally:
            self._current_reader = None
            self._current_file = None

    def _extract_text(self) -> str:
        """
        Wydobywa tekst ze wszystkich stron dokumentu PDF.
        
        Returns:
            str: Połączony tekst ze wszystkich stron
        """
        if not self._current_reader:
            return ""

        text_parts = []
        for page in self._current_reader.pages:
            try:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            except Exception as e:
                print(f"Ostrzeżenie: Nie można wydobyć tekstu ze strony: {str(e)}")

        return "\n".join(text_parts)

    def _extract_metadata(self) -> PDFMetadata:
        """
        Wydobywa metadane z dokumentu PDF.
        
        Returns:
            PDFMetadata: Obiekt zawierający metadane dokumentu
        """
        if not self._current_reader:
            return PDFMetadata()

        try:
            metadata = self._current_reader.metadata
            return PDFMetadata(
                title=metadata.get('/Title', None),
                author=metadata.get('/Author', None),
                subject=metadata.get('/Subject', None),
                creation_date=self._parse_pdf_date(metadata.get('/CreationDate', None)),
                modification_date=self._parse_pdf_date(metadata.get('/ModDate', None)),
                page_count=len(self._current_reader.pages)
            )
        except Exception as e:
            print(f"Ostrzeżenie: Nie można wydobyć metadanych: {str(e)}")
            return PDFMetadata(page_count=len(self._current_reader.pages))

    def _parse_pdf_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Parsuje datę z formatu PDF do obiektu datetime.
        
        Args:
            date_str (Optional[str]): Data w formacie PDF (D:YYYYMMDDHHmmSS)
            
        Returns:
            Optional[datetime]: Sparsowana data lub None w przypadku błędu
        """
        if not date_str:
            return None

        try:
            # Usuń prefix 'D:' jeśli istnieje
            if date_str.startswith('D:'):
                date_str = date_str[2:]
            
            # Podstawowy format PDF: YYYYMMDDHHmmSS
            return datetime.strptime(date_str[:14], '%Y%m%d%H%M%S')
        except Exception:
            return None 