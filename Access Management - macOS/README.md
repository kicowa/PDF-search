# Access Management - wersja macOS

Aplikacja do zarządzania dostępami, stworzona w Streamlit. Pozwala na przeglądanie i zarządzanie uprawnieniami użytkowników w różnych środowiskach i departamentach.

## Wymagania systemowe

- macOS
- Python 3.x (jeśli nie jest zainstalowany, można pobrać ze strony [python.org](https://www.python.org/downloads/))

## Instalacja i uruchomienie

1. Pobierz następujące pliki z repozytorium:
   - `run_app.command` - skrypt uruchomieniowy
   - `nowy skrypt wersja 2.py` - główny skrypt aplikacji
   - `POC.xlsx` - plik z danymi

2. Umieść wszystkie pliki w tym samym katalogu.

3. Uruchom aplikację poprzez:
   - Dwukrotne kliknięcie na plik `run_app.command`
   LUB
   - Otwórz Terminal, przejdź do katalogu z plikami i wykonaj:
     ```bash
     ./run_app.command
     ```

4. Przy pierwszym uruchomieniu skrypt:
   - Sprawdzi instalację Pythona
   - Zainstaluje virtualenv (jeśli nie jest zainstalowany)
   - Stworzy wirtualne środowisko Python
   - Zainstaluje wymagane pakiety (streamlit, pandas, openpyxl)
   - Uruchomi aplikację

5. Aplikacja otworzy się automatycznie w domyślnej przeglądarce pod adresem:
   - http://localhost:8501

## Struktura projektu

```
Access Management - macOS/
├── run_app.command          # Skrypt uruchomieniowy
├── nowy skrypt wersja 2.py  # Główny skrypt aplikacji
└── POC.xlsx                 # Plik z danymi
```

## Rozwiązywanie problemów

1. Jeśli skrypt nie chce się uruchomić, upewnij się, że ma uprawnienia do wykonywania:
   ```bash
   chmod +x run_app.command
   ```

2. Jeśli pojawia się błąd "Python nie jest zainstalowany":
   - Pobierz i zainstaluj Python ze strony [python.org](https://www.python.org/downloads/)
   - Upewnij się, że podczas instalacji zaznaczono opcję "Add Python to PATH"

3. Dla lepszej wydajności można zainstalować moduł Watchdog:
   ```bash
   xcode-select --install
   pip install watchdog
   ```

## Uwagi

- Folder `venv` jest tworzony lokalnie na każdym komputerze podczas pierwszego uruchomienia
- Aplikacja wymaga połączenia z internetem podczas pierwszego uruchomienia (do pobrania pakietów)
- Wszystkie dane są przechowywane lokalnie w pliku `POC.xlsx` 