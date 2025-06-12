#!/usr/bin/env python3
"""
Główny plik uruchomieniowy aplikacji Przeszukiwarka PDF.
"""

import os
import sys
import tkinter as tk
from ui.main_window import MainWindow
from utils.setup_nltk import setup_nltk

def main():
    """
    Główna funkcja aplikacji
    """
    try:
        # Inicjalizacja zasobów NLTK
        setup_nltk()
        
        # Utworzenie głównego okna
        root = tk.Tk()
        root.title("Przeszukiwarka PDF")
        
        # Tworzenie głównego interfejsu
        app = MainWindow(root)
        
        # Uruchomienie pętli zdarzeń
        root.mainloop()
        
    except Exception as e:
        print(f"Błąd podczas uruchamiania aplikacji: {str(e)}")
        raise

if __name__ == "__main__":
    # Dodaj katalog src do PYTHONPATH
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    main() 