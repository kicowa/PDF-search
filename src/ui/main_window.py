import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from core.pdf_processor import PDFProcessor
from core.text_processor import TextProcessor
from core.search_engine import SearchEngine
from utils.file_handler import FileHandler
from utils.config import config_manager
from ui.results_view import ResultsView
from ui.progress_dialog import ProgressDialog
from utils.exceptions import FileOperationError, PDFProcessingError
from typing import List, Optional
import os

class MainWindow:
    """
    Główne okno aplikacji
    """
    def __init__(self, root=None):
        """
        Inicjalizacja głównego okna
        
        Args:
            root: Główne okno aplikacji (opcjonalne)
        """
        # Inicjalizacja głównego okna
        self.root = root or tk.Tk()
        self.root.title("Przeszukiwarka PDF")
        
        # Ustawienie rozmiaru okna z konfiguracji
        self.root.geometry(f"{config_manager.get('window_width')}x{config_manager.get('window_height')}")
        
        try:
            # Inicjalizacja komponentów
            self._init_components()
            self._init_handlers()
            
            # Inicjalizacja silnika wyszukiwania
            self.search_engine = SearchEngine()
            self.file_handler = FileHandler()
            
            # Wczytaj ostatnio używany folder
            self._load_last_directory()
            
        except Exception as e:
            messagebox.showerror(
                "Błąd inicjalizacji",
                f"Wystąpił błąd podczas inicjalizacji aplikacji:\n{str(e)}"
            )
            self.root.destroy()
            raise

    def _init_components(self):
        """
        Inicjalizacja komponentów interfejsu
        """
        # Główny kontener
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Przycisk wyboru folderu
        self.folder_button = ttk.Button(
            main_frame,
            text="Wybierz folder z dokumentami",
            command=self._on_folder_select
        )
        self.folder_button.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Pole wyszukiwania
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=50
        )
        self.search_entry.grid(row=0, column=0, padx=(0, 5))
        self.search_entry.bind('<Return>', lambda e: self._on_search())
        
        self.search_button = ttk.Button(
            search_frame,
            text="Szukaj",
            command=self._on_search
        )
        self.search_button.grid(row=0, column=1)
        
        # Widok wyników
        self.results_view = ResultsView(main_frame)
        self.results_view.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Pasek statusu
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN
        )
        self.status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Konfiguracja rozciągania
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def _init_handlers(self):
        """
        Inicjalizacja obsługi zdarzeń
        """
        # Obsługa zamknięcia okna
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Obsługa zmiany rozmiaru okna
        self.root.bind('<Configure>', self._on_window_resize)
    
    def _run_with_progress(
        self,
        operation,
        title: str,
        message: str,
        error_title: str,
        *args,
        **kwargs
    ) -> Optional[object]:
        """
        Uruchamia operację z paskiem postępu
        
        Args:
            operation: Funkcja do wykonania
            title: Tytuł okna dialogowego
            message: Komunikat w oknie dialogowym
            error_title: Tytuł okna błędu
            *args: Argumenty pozycyjne dla funkcji
            **kwargs: Argumenty nazwane dla funkcji
            
        Returns:
            Optional[object]: Wynik operacji lub None w przypadku błędu
        """
        dialog = ProgressDialog(
            self.root,
            title,
            message,
            operation,
            *args,
            **kwargs
        )
        result, error = dialog.run()
        
        if error:
            messagebox.showerror(
                error_title,
                f"Wystąpił błąd:\n{str(error)}"
            )
            return None
            
        return result
    
    def _load_last_directory(self):
        """
        Wczytuje ostatnio używany folder
        """
        last_dir = config_manager.get("last_directory")
        if last_dir and os.path.exists(last_dir):
            try:
                self.search_engine.index_directory(last_dir)
                self._update_status()
            except Exception as e:
                print(f"Błąd wczytywania ostatniego folderu: {str(e)}")
    
    def _on_folder_select(self):
        """
        Obsługa wyboru folderu z dokumentami
        """
        folder = filedialog.askdirectory(
            title="Wybierz folder z dokumentami PDF",
            initialdir=config_manager.get("last_directory", os.path.expanduser("~"))
        )
        
        if folder:
            try:
                # Zapisz wybrany folder w konfiguracji
                config_manager.set("last_directory", folder)
                
                # Indeksuj dokumenty
                self.search_engine.index_directory(folder)
                
                # Aktualizuj status
                self._update_status()
                
            except Exception as e:
                messagebox.showerror(
                    "Błąd indeksowania",
                    f"Wystąpił błąd podczas indeksowania dokumentów:\n{str(e)}"
                )
    
    def _on_search(self):
        """
        Obsługa wyszukiwania
        """
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning(
                "Puste zapytanie",
                "Wprowadź frazę do wyszukania."
            )
            return
        
        try:
            # Wyszukaj dokumenty
            results = self.search_engine.search(query)
            
            if results:
                # Wyświetl wyniki
                self.results_view.set_results(results)
                
                # Aktualizuj status
                self._update_status(f"Znaleziono {len(results)} wyników")
            else:
                messagebox.showinfo(
                    "Brak wyników",
                    "Nie znaleziono dokumentów pasujących do zapytania."
                )
                
        except Exception as e:
            messagebox.showerror(
                "Błąd wyszukiwania",
                f"Wystąpił błąd podczas wyszukiwania:\n{str(e)}"
            )
    
    def _update_status(self, message: Optional[str] = None):
        """
        Aktualizacja paska statusu
        
        Args:
            message: Opcjonalna wiadomość do wyświetlenia
        """
        try:
            if hasattr(self, 'file_handler'):
                valid_files = self.file_handler.get_valid_files()
                current_dir = config_manager.get("last_directory", "Nie wybrano folderu")
                status = f"Folder: {current_dir} | "
                status += f"Liczba dokumentów: {len(valid_files)}"
                if message:
                    status += f" | {message}"
            else:
                status = "Wybierz folder z dokumentami"
            
            self.status_var.set(status)
            
        except Exception as e:
            self.status_var.set("Błąd aktualizacji statusu")
            print(f"Błąd podczas aktualizacji statusu: {str(e)}")
    
    def _on_window_resize(self, event):
        """
        Obsługa zmiany rozmiaru okna
        """
        if event.widget == self.root:
            try:
                # Zapisz nowy rozmiar w konfiguracji
                config_manager.set("window_width", self.root.winfo_width())
                config_manager.set("window_height", self.root.winfo_height())
            except Exception as e:
                print(f"Błąd podczas zapisywania rozmiaru okna: {str(e)}")
    
    def _on_close(self):
        """
        Obsługa zamknięcia okna
        """
        try:
            # Zapisz konfigurację przed zamknięciem
            config_manager.save()
        except Exception as e:
            print(f"Błąd podczas zapisywania konfiguracji: {str(e)}")
        finally:
            self.root.destroy()
    
    def run(self):
        """
        Uruchamia aplikację
        """
        self.root.mainloop() 