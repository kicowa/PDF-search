import os
import json
import pickle
import zlib
from typing import Dict, List, Optional
from datetime import datetime
from src.core.search_engine import DocumentIndex
from src.utils.config import config_manager

class IndexStorage:
    """
    Klasa odpowiedzialna za zapisywanie i wczytywanie indeksu wyszukiwania
    """
    def __init__(self):
        """
        Inicjalizacja przechowywania indeksu
        """
        # Pobierz ścieżkę do katalogu indeksu z konfiguracji
        self.index_dir = config_manager.get("index_directory")
        if not self.index_dir:
            # Jeśli nie ma w konfiguracji, użyj domyślnej ścieżki
            self.index_dir = os.path.join(os.path.expanduser("~"), ".pdf_search", "index")
        
        # Upewnij się, że katalog istnieje
        os.makedirs(self.index_dir, exist_ok=True)
        
        # Ścieżki do plików indeksu
        self.index_file = os.path.join(self.index_dir, "search_index.pkl")
        self.metadata_file = os.path.join(self.index_dir, "metadata.json")
    
    def save_index(self, documents: Dict[str, DocumentIndex]) -> bool:
        """
        Zapisuje indeks wyszukiwania do pliku
        
        Args:
            documents: Słownik dokumentów do zapisania
            
        Returns:
            bool: True jeśli zapis się powiódł, False w przeciwnym razie
        """
        try:
            # Przygotuj metadane
            metadata = {
                "version": "1.0",
                "document_count": len(documents),
                "last_updated": datetime.now().isoformat(),
                "document_paths": list(documents.keys())
            }
            
            # Kompresuj i zapisz indeks
            compressed_data = zlib.compress(pickle.dumps(documents))
            with open(self.index_file, 'wb') as f:
                f.write(compressed_data)
            
            # Zapisz metadane
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Błąd podczas zapisywania indeksu: {str(e)}")
            return False
    
    def load_index(self) -> Optional[Dict[str, DocumentIndex]]:
        """
        Wczytuje indeks wyszukiwania z pliku
        
        Returns:
            Optional[Dict[str, DocumentIndex]]: Słownik dokumentów lub None w przypadku błędu
        """
        try:
            # Sprawdź czy pliki istnieją
            if not os.path.exists(self.index_file) or not os.path.exists(self.metadata_file):
                return None
            
            # Wczytaj metadane
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Sprawdź wersję
            if metadata["version"] != "1.0":
                print(f"Nieobsługiwana wersja indeksu: {metadata['version']}")
                return None
            
            # Wczytaj i dekompresuj indeks
            with open(self.index_file, 'rb') as f:
                compressed_data = f.read()
            
            documents = pickle.loads(zlib.decompress(compressed_data))
            
            # Sprawdź czy wszystkie dokumenty istnieją
            for path in metadata["document_paths"]:
                if not os.path.exists(path):
                    print(f"Ostrzeżenie: Dokument nie istnieje: {path}")
            
            return documents
            
        except Exception as e:
            print(f"Błąd podczas wczytywania indeksu: {str(e)}")
            return None
    
    def update_index(self, documents: Dict[str, DocumentIndex]) -> bool:
        """
        Aktualizuje istniejący indeks
        
        Args:
            documents: Nowe dokumenty do dodania/aktualizacji
            
        Returns:
            bool: True jeśli aktualizacja się powiodła, False w przeciwnym razie
        """
        try:
            # Wczytaj istniejący indeks
            existing_docs = self.load_index() or {}
            
            # Aktualizuj dokumenty
            existing_docs.update(documents)
            
            # Zapisz zaktualizowany indeks
            return self.save_index(existing_docs)
            
        except Exception as e:
            print(f"Błąd podczas aktualizacji indeksu: {str(e)}")
            return False
    
    def get_index_info(self) -> Optional[Dict]:
        """
        Zwraca informacje o indeksie
        
        Returns:
            Optional[Dict]: Informacje o indeksie lub None w przypadku błędu
        """
        try:
            if not os.path.exists(self.metadata_file):
                return None
            
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"Błąd podczas odczytu informacji o indeksie: {str(e)}")
            return None
    
    def clear_index(self) -> bool:
        """
        Czyści indeks wyszukiwania
        
        Returns:
            bool: True jeśli czyszczenie się powiodło, False w przeciwnym razie
        """
        try:
            if os.path.exists(self.index_file):
                os.remove(self.index_file)
            if os.path.exists(self.metadata_file):
                os.remove(self.metadata_file)
            return True
        except Exception as e:
            print(f"Błąd podczas czyszczenia indeksu: {str(e)}")
            return False 