import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any
import os
import subprocess
import platform
from utils.config import config_manager
from core.models import SearchResult

class ResultsView(ttk.Frame):
    """
    Widok wyników wyszukiwania.
    Wyświetla wyniki w formie tabeli z możliwością sortowania
    i podglądu fragmentów tekstu.
    """

    def __init__(self, parent: tk.Widget):
        """
        Inicjalizacja widoku wyników.
        
        Args:
            parent (tk.Widget): Widget rodzica
        """
        super().__init__(parent)
        self._init_components()
        self._results: List[SearchResult] = []
        self._sort_column = "score"
        self._sort_reverse = True

    def _init_components(self):
        """
        Inicjalizacja komponentów interfejsu
        """
        # Treeview do wyświetlania wyników
        self.tree = ttk.Treeview(
            self,
            columns=("title", "score", "path"),
            show="headings"
        )
        
        # Konfiguracja kolumn
        self.tree.heading("title", text="Tytuł", command=lambda: self._sort_by("title"))
        self.tree.heading("score", text="Trafność", command=lambda: self._sort_by("score"))
        self.tree.heading("path", text="Ścieżka", command=lambda: self._sort_by("path"))
        
        self.tree.column("title", width=200)
        self.tree.column("score", width=100)
        self.tree.column("path", width=300)
        
        # Pasek przewijania dla tabeli
        tree_scrollbar = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Podgląd tekstu
        preview_frame = ttk.LabelFrame(self, text="Podgląd fragmentów", padding="5")
        
        self.preview_text = tk.Text(
            preview_frame,
            wrap=tk.WORD,
            height=10,
            state="disabled"
        )
        
        # Pasek przewijania dla podglądu
        preview_scrollbar = ttk.Scrollbar(
            preview_frame,
            orient=tk.VERTICAL,
            command=self.preview_text.yview
        )
        self.preview_text.configure(yscrollcommand=preview_scrollbar.set)
        
        # Rozmieszczenie elementów
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        preview_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Konfiguracja rozciągania
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=1)
        
        # Podpięcie obsługi zdarzeń
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def set_results(self, results: List[SearchResult]):
        """
        Ustawia wyniki wyszukiwania.
        
        Args:
            results (List[SearchResult]): Lista wyników
        """
        self._results = results
        self._refresh_view()

    def _refresh_view(self):
        """
        Odświeża widok tabeli
        """
        # Czyszczenie tabeli
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Sortowanie wyników
        sorted_results = sorted(
            self._results,
            key=lambda x: getattr(x, self._sort_column),
            reverse=self._sort_reverse
        )

        # Dodawanie wyników do tabeli
        for result in sorted_results:
            self.tree.insert(
                "",
                "end",
                values=(
                    result.title,
                    f"{result.score:.2%}",
                    result.file_path
                ),
                tags=(result.file_path,)
            )

    def _sort_by(self, column: str):
        """
        Sortuje wyniki według wybranej kolumny.
        
        Args:
            column (str): Nazwa kolumny
        """
        if self._sort_column == column:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column = column
            self._sort_reverse = True
        self._refresh_view()

    def _on_select(self, event):
        """
        Obsługa zdarzenia wyboru wiersza.
        
        Args:
            event: Zdarzenie wyboru
        """
        selection = self.tree.selection()
        if not selection:
            return

        # Pobieramy wybrany wynik
        item = self.tree.item(selection[0])
        file_path = item["tags"][0]
        result = next(
            (r for r in self._results if r.file_path == file_path),
            None
        )

        if result:
            # Aktualizujemy podgląd
            self.preview_text.config(state="normal")
            self.preview_text.delete(1.0, tk.END)
            for match in result.matches:
                self.preview_text.insert(tk.END, match + "\n\n")
            self.preview_text.config(state="disabled")

    def _on_double_click(self, event):
        """
        Obsługa podwójnego kliknięcia na wynik
        
        Args:
            event: Zdarzenie kliknięcia
        """
        selection = self.tree.selection()
        if not selection:
            return
            
        # Pobierz zaznaczony element
        item = selection[0]
        path = self.tree.item(item)["values"][2]
        
        # Otwórz plik PDF w domyślnej aplikacji
        if os.path.exists(path):
            if platform.system() == "Darwin":  # macOS
                subprocess.run(["open", path])
            elif platform.system() == "Windows":
                os.startfile(path)
            else:  # Linux
                subprocess.run(["xdg-open", path])

    def clear(self):
        """
        Czyści widok wyników
        """
        self._results = []
        self._refresh_view()
        self.preview_text.config(state="normal")
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.config(state="disabled")

    def update_results(self, results: List[Dict[str, Any]]):
        """
        Aktualizuje listę wyników
        
        Args:
            results: Lista wyników wyszukiwania
        """
        self.clear()
        for result in results:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    result["title"],
                    f"{result['score']:.2f}",
                    result["path"]
                )
            ) 