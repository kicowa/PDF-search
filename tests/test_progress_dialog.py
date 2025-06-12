import unittest
import tkinter as tk
import time
from src.ui.progress_dialog import ProgressDialog

class TestProgressDialog(unittest.TestCase):
    """
    Testy jednostkowe dla klasy ProgressDialog
    """
    
    def setUp(self):
        """
        Przygotowanie środowiska testowego
        """
        self.root = tk.Tk()
    
    def tearDown(self):
        """
        Sprzątanie po testach
        """
        self.root.destroy()
    
    def test_successful_operation(self):
        """
        Test pomyślnego wykonania operacji
        """
        def mock_operation():
            time.sleep(0.1)  # Symulacja długiej operacji
            return "success"
        
        dialog = ProgressDialog(
            self.root,
            "Test",
            "Testowa operacja",
            mock_operation
        )
        
        result, error = dialog.run()
        
        self.assertEqual(result, "success")
        self.assertIsNone(error)
    
    def test_failed_operation(self):
        """
        Test nieudanej operacji
        """
        def mock_operation():
            time.sleep(0.1)  # Symulacja długiej operacji
            raise ValueError("Test error")
        
        dialog = ProgressDialog(
            self.root,
            "Test",
            "Testowa operacja",
            mock_operation
        )
        
        result, error = dialog.run()
        
        self.assertIsNone(result)
        self.assertIsInstance(error, ValueError)
        self.assertEqual(str(error), "Test error")
    
    def test_operation_with_arguments(self):
        """
        Test operacji z argumentami
        """
        def mock_operation(x, y, z=None):
            time.sleep(0.1)  # Symulacja długiej operacji
            return x + y + (z or 0)
        
        dialog = ProgressDialog(
            self.root,
            "Test",
            "Testowa operacja",
            mock_operation,
            1, 2,
            z=3
        )
        
        result, error = dialog.run()
        
        self.assertEqual(result, 6)
        self.assertIsNone(error)
    
    def test_dialog_creation(self):
        """
        Test tworzenia okna dialogowego
        """
        def mock_operation():
            time.sleep(0.1)
        
        dialog = ProgressDialog(
            self.root,
            "Test Title",
            "Test Message",
            mock_operation
        )
        
        # Sprawdź czy okno zostało utworzone
        self.assertIsInstance(dialog.dialog, tk.Toplevel)
        
        # Sprawdź tytuł
        self.assertEqual(dialog.dialog.title(), "Test Title")
        
        # Sprawdź czy pasek postępu istnieje
        self.assertIsInstance(dialog.progress, tk.ttk.Progressbar)
        
        # Sprawdź czy etykieta z komunikatem istnieje
        self.assertTrue(
            any(
                isinstance(child, tk.ttk.Label) and child.cget("text") == "Test Message"
                for child in dialog.dialog.winfo_children()[0].winfo_children()
            )
        )

if __name__ == '__main__':
    unittest.main() 