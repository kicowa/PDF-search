import unittest
import os
import json
import tempfile
from src.utils.config import ConfigManager, AppConfig

class TestConfigManager(unittest.TestCase):
    """
    Testy jednostkowe dla klasy ConfigManager
    """
    
    def setUp(self):
        """
        Przygotowanie środowiska testowego
        """
        # Tworzymy tymczasowy plik konfiguracyjny
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        self.manager = ConfigManager(self.config_file)
    
    def tearDown(self):
        """
        Sprzątanie po testach
        """
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_default_values(self):
        """
        Test domyślnych wartości konfiguracji
        """
        config = self.manager.get_all()
        
        # Sprawdzamy czy wszystkie domyślne wartości są poprawne
        self.assertEqual(config["max_results"], 100)
        self.assertEqual(config["min_score"], 0.1)
        self.assertEqual(config["context_size"], 50)
        self.assertEqual(config["window_width"], 800)
        self.assertEqual(config["window_height"], 600)
        self.assertEqual(config["theme"], "default")
        self.assertEqual(config["index_batch_size"], 100)
        self.assertTrue(config["auto_index"])
        self.assertEqual(config["language"], "pl")
        self.assertTrue(config["stop_words"])
    
    def test_save_and_load(self):
        """
        Test zapisywania i wczytywania konfiguracji
        """
        # Zmieniamy kilka wartości
        self.manager.set("max_results", 50)
        self.manager.set("min_score", 0.2)
        self.manager.set("theme", "dark")
        
        # Tworzymy nowego menedżera (wczyta zapisane wartości)
        new_manager = ConfigManager(self.config_file)
        
        # Sprawdzamy czy wartości zostały zachowane
        self.assertEqual(new_manager.get("max_results"), 50)
        self.assertEqual(new_manager.get("min_score"), 0.2)
        self.assertEqual(new_manager.get("theme"), "dark")
    
    def test_get_and_set(self):
        """
        Test pobierania i ustawiania wartości
        """
        # Ustawiamy nową wartość
        self.manager.set("max_results", 200)
        
        # Sprawdzamy czy wartość została zmieniona
        self.assertEqual(self.manager.get("max_results"), 200)
        
        # Sprawdzamy czy wartość została zapisana do pliku
        with open(self.config_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(data["max_results"], 200)
    
    def test_reset(self):
        """
        Test resetowania konfiguracji
        """
        # Zmieniamy kilka wartości
        self.manager.set("max_results", 50)
        self.manager.set("min_score", 0.2)
        
        # Resetujemy konfigurację
        self.manager.reset()
        
        # Sprawdzamy czy wartości wróciły do domyślnych
        self.assertEqual(self.manager.get("max_results"), 100)
        self.assertEqual(self.manager.get("min_score"), 0.1)
    
    def test_invalid_key(self):
        """
        Test obsługi nieprawidłowego klucza
        """
        # Próbujemy pobrać nieistniejący klucz
        value = self.manager.get("invalid_key", "default")
        self.assertEqual(value, "default")
        
        # Próbujemy ustawić nieistniejący klucz
        self.manager.set("invalid_key", "value")
        self.assertNotIn("invalid_key", self.manager.get_all())
    
    def test_file_corruption(self):
        """
        Test obsługi uszkodzonego pliku konfiguracyjnego
        """
        # Zapisujemy nieprawidłowe dane do pliku
        with open(self.config_file, 'w') as f:
            f.write("invalid json data")
        
        # Tworzymy nowego menedżera (powinien użyć domyślnych wartości)
        new_manager = ConfigManager(self.config_file)
        
        # Sprawdzamy czy użyto domyślnych wartości
        self.assertEqual(new_manager.get("max_results"), 100)
        self.assertEqual(new_manager.get("min_score"), 0.1)
    
    def test_all_settings(self):
        """
        Test wszystkich ustawień konfiguracji
        """
        # Testujemy każde ustawienie
        settings = {
            "max_results": 50,
            "min_score": 0.2,
            "context_size": 100,
            "window_width": 1024,
            "window_height": 768,
            "theme": "dark",
            "index_batch_size": 200,
            "auto_index": False,
            "language": "en",
            "stop_words": False
        }
        
        # Ustawiamy wszystkie wartości
        for key, value in settings.items():
            self.manager.set(key, value)
        
        # Sprawdzamy czy wszystkie wartości zostały zapisane
        for key, value in settings.items():
            self.assertEqual(self.manager.get(key), value)
        
        # Sprawdzamy czy wszystkie wartości są w get_all()
        all_settings = self.manager.get_all()
        for key, value in settings.items():
            self.assertEqual(all_settings[key], value)

if __name__ == '__main__':
    unittest.main() 