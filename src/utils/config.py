import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class AppConfig:
    """
    Klasa przechowująca konfigurację aplikacji
    """
    # Ścieżki
    last_directory: str = ""  # Ostatnio używany katalog
    index_directory: str = ""  # Katalog z indeksem wyszukiwania
    
    # Ustawienia wyszukiwania
    max_results: int = 100  # Maksymalna liczba wyników
    min_score: float = 0.1  # Minimalna trafność wyniku
    context_size: int = 50  # Liczba znaków kontekstu
    
    # Ustawienia interfejsu
    window_width: int = 800
    window_height: int = 600
    theme: str = "default"
    
    # Ustawienia indeksowania
    index_batch_size: int = 100  # Liczba dokumentów w jednej partii
    auto_index: bool = True  # Automatyczne indeksowanie nowych plików
    
    # Ustawienia języka
    language: str = "english"  # Domyślny język
    stop_words: bool = True  # Usuwanie stop words

class ConfigManager:
    """
    Menedżer konfiguracji aplikacji.
    Zarządza zapisem i odczytem ustawień.
    """
    
    def __init__(self, config_file: str = "config.json"):
        """
        Inicjalizacja menedżera konfiguracji.
        
        Args:
            config_file (str): Ścieżka do pliku konfiguracyjnego
        """
        self.config_file = config_file
        self.config = AppConfig()
        self.load()
    
    def load(self) -> None:
        """
        Wczytuje konfigurację z pliku.
        Jeśli plik nie istnieje, używa domyślnych wartości.
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(self.config, key):
                            setattr(self.config, key, value)
        except Exception as e:
            print(f"Błąd podczas wczytywania konfiguracji: {str(e)}")
    
    def save(self) -> None:
        """
        Zapisuje konfigurację do pliku.
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.config), f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Błąd podczas zapisywania konfiguracji: {str(e)}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Pobiera wartość ustawienia.
        
        Args:
            key (str): Nazwa ustawienia
            default (Any): Wartość domyślna
            
        Returns:
            Any: Wartość ustawienia
        """
        return getattr(self.config, key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Ustawia wartość ustawienia.
        
        Args:
            key (str): Nazwa ustawienia
            value (Any): Nowa wartość
        """
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            self.save()
    
    def reset(self) -> None:
        """
        Resetuje konfigurację do wartości domyślnych.
        """
        self.config = AppConfig()
        self.save()
    
    def get_all(self) -> Dict[str, Any]:
        """
        Pobiera wszystkie ustawienia.
        
        Returns:
            Dict[str, Any]: Słownik z ustawieniami
        """
        return asdict(self.config)

# Globalna instancja menedżera konfiguracji
config_manager = ConfigManager() 