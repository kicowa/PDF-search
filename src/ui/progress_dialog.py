import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Tuple
import threading
import queue

class ProgressDialog:
    """
    Dialog pokazujący postęp długiej operacji
    """
    def __init__(
        self,
        parent: tk.Tk,
        title: str,
        message: str,
        operation: Callable,
        *args,
        **kwargs
    ):
        """
        Inicjalizacja dialogu postępu
        
        Args:
            parent: Okno rodzica
            title: Tytuł okna
            message: Komunikat do wyświetlenia
            operation: Funkcja do wykonania
            *args: Argumenty pozycyjne dla funkcji
            **kwargs: Argumenty nazwane dla funkcji
        """
        self.parent = parent
        self.title = title
        self.message = message
        self.operation = operation
        self.args = args
        self.kwargs = kwargs
        
        # Kolejka do komunikacji między wątkami
        self.queue = queue.Queue()
        
        # Wynik operacji
        self.result = None
        self.error = None
        
        # Flaga zakończenia operacji
        self.done = False
        
        # Tworzymy okno dialogowe
        self._create_dialog()
        
    def _create_dialog(self):
        """
        Tworzy okno dialogowe
        """
        # Tworzymy okno
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Ustawiamy rozmiar i pozycję
        window_width = 300
        window_height = 100
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Dodajemy elementy
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Etykieta z komunikatem
        self.message_label = ttk.Label(main_frame, text=self.message)
        self.message_label.grid(row=0, column=0, pady=(0, 10))
        
        # Pasek postępu
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=200
        )
        self.progress.grid(row=1, column=0)
        
        # Konfiguracja rozciągania
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Uruchamiamy pasek postępu
        self.progress.start()
        
        # Blokujemy zamykanie okna przez użytkownika
        self.dialog.protocol("WM_DELETE_WINDOW", lambda: None)
        
    def _run_operation(self):
        """
        Uruchamia operację w osobnym wątku
        """
        try:
            result = self.operation(*self.args, **self.kwargs)
            self.queue.put(('success', result))
        except Exception as e:
            self.queue.put(('error', e))
        finally:
            self.done = True
    
    def _check_queue(self):
        """
        Sprawdza kolejkę komunikatów
        """
        try:
            status, value = self.queue.get_nowait()
            
            # Zatrzymujemy pasek postępu
            self.progress.stop()
            
            if status == 'success':
                self.result = value
            else:
                self.error = value
            
            # Zamykamy okno
            self.dialog.destroy()
            
        except queue.Empty:
            # Jeśli operacja się zakończyła, ale kolejka jest pusta,
            # oznacza to błąd w wątku operacji
            if self.done:
                self.dialog.destroy()
            else:
                # Jeśli kolejka jest pusta, sprawdzamy ponownie za 100ms
                self.dialog.after(100, self._check_queue)
    
    def run(self) -> Tuple[Optional[object], Optional[Exception]]:
        """
        Uruchamia dialog i zwraca wynik operacji
        
        Returns:
            Krotka (wynik, błąd)
        """
        # Uruchamiamy operację w osobnym wątku
        thread = threading.Thread(target=self._run_operation)
        thread.daemon = True
        thread.start()
        
        # Rozpoczynamy sprawdzanie kolejki
        self._check_queue()
        
        # Czekamy na zamknięcie okna
        self.dialog.wait_window()
        
        return self.result, self.error 