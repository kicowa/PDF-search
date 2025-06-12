from typing import List, Set, Dict, Optional
import os
import magic
from dataclasses import dataclass
from datetime import datetime
import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from .exceptions import FileOperationError, PDFProcessingError
from .config import config_manager

@dataclass
class FileInfo:
    """
    Klasa przechowująca informacje o pliku PDF
    """
    path: str  # Ścieżka do pliku
    size: int  # Rozmiar pliku w bajtach
    modified_time: datetime  # Data ostatniej modyfikacji
    is_valid: bool = False  # Czy plik jest prawidłowym PDF-em
    error_message: Optional[str] = None  # Komunikat błędu (jeśli wystąpił)

class FileHandler:
    """
    Klasa do zarządzania plikami PDF.
    Skanuje katalogi, waliduje pliki i śledzi zmiany.
    """

    def __init__(self):
        """
        Inicjalizacja handlera plików
        """
        self.files: Dict[str, FileInfo] = {}  # Ścieżka -> FileInfo
        try:
            self.mime = magic.Magic(mime=True)
        except Exception as e:
            raise FileOperationError(f"Nie można zainicjalizować systemu MIME: {str(e)}")
        self._scan_lock = threading.Lock()
        self._progress_queue: Queue = Queue()
        self.last_directory = None

    def scan_directory(
        self,
        directory: str,
        recursive: bool = True,
        show_progress: bool = True
    ) -> List[FileInfo]:
        """
        Skanuje katalog w poszukiwaniu plików PDF.
        
        Args:
            directory (str): Ścieżka do katalogu
            recursive (bool): Czy skanować podkatalogi
            show_progress (bool): Czy pokazywać pasek postępu
            
        Returns:
            List[FileInfo]: Lista znalezionych plików PDF
            
        Raises:
            FileOperationError: Gdy wystąpi błąd podczas operacji na plikach
        """
        if not os.path.isdir(directory):
            raise FileOperationError(f"Katalog nie istnieje: {directory}")

        try:
            with self._scan_lock:
                # Znajdujemy wszystkie pliki
                all_files = []
                for root, _, files in os.walk(directory):
                    for file in files:
                        if file.lower().endswith('.pdf'):
                            all_files.append(os.path.join(root, file))
                    if not recursive:
                        break

                # Inicjalizujemy pasek postępu
                if show_progress:
                    pbar = tqdm(
                        total=len(all_files),
                        desc="Skanowanie plików PDF",
                        unit="plik"
                    )

                # Przetwarzamy pliki równolegle
                new_files: List[FileInfo] = []
                with ThreadPoolExecutor() as executor:
                    future_to_path = {
                        executor.submit(self._process_file, path): path
                        for path in all_files
                    }
                    
                    for future in future_to_path:
                        try:
                            file_info = future.result()
                            if file_info:
                                new_files.append(file_info)
                                self.files[file_info.path] = file_info
                        except Exception as e:
                            print(f"Błąd podczas przetwarzania pliku: {str(e)}")
                        if show_progress:
                            pbar.update(1)

                if show_progress:
                    pbar.close()

                return new_files

        except Exception as e:
            raise FileOperationError(f"Błąd podczas skanowania katalogu: {str(e)}")

    def _process_file(self, file_path: str) -> Optional[FileInfo]:
        """
        Przetwarza pojedynczy plik PDF.
        
        Args:
            file_path (str): Ścieżka do pliku
            
        Returns:
            Optional[FileInfo]: Informacje o pliku lub None jeśli plik jest nieprawidłowy
            
        Raises:
            PDFProcessingError: Gdy wystąpi błąd podczas przetwarzania PDF
        """
        try:
            # Sprawdzamy czy plik istnieje
            if not os.path.isfile(file_path):
                raise PDFProcessingError(f"Plik nie istnieje: {file_path}")

            # Pobieramy podstawowe informacje o pliku
            try:
                stat = os.stat(file_path)
            except Exception as e:
                raise PDFProcessingError(f"Nie można odczytać informacji o pliku: {str(e)}")
            
            # Tworzymy obiekt FileInfo
            file_info = FileInfo(
                path=file_path,
                size=stat.st_size,
                modified_time=datetime.fromtimestamp(stat.st_mtime),
                is_valid=False
            )

            # Sprawdzamy MIME type
            try:
                mime_type = self.mime.from_file(file_path)
                if mime_type != 'application/pdf':
                    file_info.error_message = f"Nieprawidłowy typ pliku: {mime_type}"
                    return file_info
            except Exception as e:
                raise PDFProcessingError(f"Nie można określić typu pliku: {str(e)}")

            # Sprawdzamy czy plik można otworzyć
            try:
                with open(file_path, 'rb') as f:
                    # Sprawdzamy sygnaturę PDF
                    signature = f.read(4)
                    if signature != b'%PDF':
                        file_info.error_message = "Brak prawidłowej sygnatury PDF"
                        return file_info
            except Exception as e:
                raise PDFProcessingError(f"Nie można otworzyć pliku: {str(e)}")

            # Plik jest prawidłowym PDF-em
            file_info.is_valid = True
            return file_info

        except PDFProcessingError as e:
            # Propagujemy błędy przetwarzania PDF
            raise e
        except Exception as e:
            # Konwertujemy inne błędy na PDFProcessingError
            raise PDFProcessingError(f"Nieoczekiwany błąd podczas przetwarzania pliku: {str(e)}")

    def get_file_info(self, file_path: str) -> Optional[FileInfo]:
        """
        Pobiera informacje o pliku.
        
        Args:
            file_path (str): Ścieżka do pliku
            
        Returns:
            Optional[FileInfo]: Informacje o pliku lub None jeśli plik nie istnieje
            
        Raises:
            FileOperationError: Gdy wystąpi błąd podczas operacji na pliku
        """
        try:
            return self.files.get(file_path)
        except Exception as e:
            raise FileOperationError(f"Błąd podczas pobierania informacji o pliku: {str(e)}")

    def check_file_changes(self, file_path: str) -> bool:
        """
        Sprawdza czy plik został zmodyfikowany.
        
        Args:
            file_path (str): Ścieżka do pliku
            
        Returns:
            bool: True jeśli plik został zmodyfikowany
            
        Raises:
            FileOperationError: Gdy wystąpi błąd podczas sprawdzania pliku
        """
        if file_path not in self.files:
            return True

        try:
            stat = os.stat(file_path)
            current_mtime = datetime.fromtimestamp(stat.st_mtime)
            return current_mtime > self.files[file_path].modified_time
        except Exception as e:
            raise FileOperationError(f"Błąd podczas sprawdzania modyfikacji pliku: {str(e)}")

    def get_valid_files(self) -> List[str]:
        """
        Zwraca listę ścieżek do prawidłowych plików PDF.
        
        Returns:
            List[str]: Lista ścieżek
            
        Raises:
            FileOperationError: Gdy wystąpi błąd podczas operacji
        """
        try:
            return [
                path for path, info in self.files.items()
                if info.is_valid
            ]
        except Exception as e:
            raise FileOperationError(f"Błąd podczas pobierania listy prawidłowych plików: {str(e)}")

    def get_invalid_files(self) -> Dict[str, str]:
        """
        Zwraca słownik nieprawidłowych plików i ich błędów.
        
        Returns:
            Dict[str, str]: Ścieżka -> komunikat błędu
            
        Raises:
            FileOperationError: Gdy wystąpi błąd podczas operacji
        """
        try:
            return {
                path: info.error_message
                for path, info in self.files.items()
                if not info.is_valid and info.error_message
            }
        except Exception as e:
            raise FileOperationError(f"Błąd podczas pobierania listy nieprawidłowych plików: {str(e)}")

    def clear(self):
        """
        Czyści pamięć podręczną plików.
        """
        self.files.clear()

    def get_pdf_files(self, directory: str) -> List[str]:
        """
        Zwraca listę plików PDF w katalogu
        
        Args:
            directory: Ścieżka do katalogu
            
        Returns:
            Lista ścieżek do plików PDF
            
        Raises:
            FileOperationError: Gdy wystąpi błąd dostępu do plików
        """
        try:
            # Sprawdź czy katalog istnieje
            if not os.path.exists(directory):
                raise FileOperationError(f"Katalog {directory} nie istnieje")
                
            # Znajdź wszystkie pliki PDF
            pdf_files = []
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    if self.is_pdf_file(file_path):
                        pdf_files.append(file_path)
                        
            return pdf_files
            
        except Exception as e:
            raise FileOperationError(f"Błąd podczas wyszukiwania plików PDF: {str(e)}")
            
    def is_pdf_file(self, file_path: str) -> bool:
        """
        Sprawdza czy plik jest dokumentem PDF
        
        Args:
            file_path: Ścieżka do pliku
            
        Returns:
            True jeśli plik jest PDF, False w przeciwnym razie
        """
        try:
            # Sprawdź rozszerzenie
            if not file_path.lower().endswith('.pdf'):
                return False
                
            # Sprawdź typ MIME
            mime = magic.Magic(mime=True)
            file_type = mime.from_file(file_path)
            return file_type == 'application/pdf'
            
        except Exception as e:
            print(f"Ostrzeżenie: Nie można określić typu pliku {file_path}: {str(e)}")
            return False
            
    def save_last_directory(self, directory: str) -> None:
        """
        Zapisuje ostatnio używany katalog
        
        Args:
            directory: Ścieżka do katalogu
        """
        self.last_directory = directory
        config_manager.set("last_directory", directory)
        
    def get_last_directory(self) -> Optional[str]:
        """
        Zwraca ostatnio używany katalog
        
        Returns:
            Ścieżka do katalogu lub None
        """
        if self.last_directory:
            return self.last_directory
            
        # Spróbuj wczytać z konfiguracji
        last_dir = config_manager.get("last_directory")
        if last_dir and os.path.exists(last_dir):
            self.last_directory = last_dir
            return last_dir
            
        return None 