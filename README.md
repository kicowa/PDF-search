# Przeszukiwarka PDF

Aplikacja do przeszukiwania dokumentów PDF z zaawansowanymi funkcjami wyszukiwania i indeksowania.

## Funkcje

- Wyszukiwanie tekstu w dokumentach PDF
- Wyświetlanie wyników z kontekstem (fragmenty tekstu przed i po znalezionym słowie)
- Sortowanie wyników według trafności
- Podgląd znalezionych fragmentów
- Otwieranie plików PDF bezpośrednio z aplikacji
- Zapamiętywanie ostatnio używanego folderu
- Automatyczne pobieranie wymaganych zasobów NLTK

## Struktura projektu

```
przeszukiwarka PDF/
├── src/
│   ├── core/
│   │   ├── models.py          # Modele danych
│   │   ├── pdf_processor.py   # Przetwarzanie PDF-ów
│   │   ├── text_processor.py  # Przetwarzanie tekstu
│   │   └── search_engine.py   # Silnik wyszukiwania
│   ├── ui/
│   │   ├── main_window.py     # Główne okno aplikacji
│   │   ├── progress_dialog.py # Dialog postępu
│   │   └── results_view.py    # Widok wyników
│   └── utils/
│       ├── file_handler.py    # Obsługa plików
│       ├── config.py          # Zarządzanie konfiguracją
│       └── setup_nltk.py      # Konfiguracja NLTK
├── tests/                     # Testy jednostkowe
└── requirements.txt           # Zależności
```

## Wymagania

- Python 3.8+
- PyPDF2>=3.0.0
- NLTK>=3.8.1
- Pozostałe zależności w pliku requirements.txt

## Instalacja na MacOS

1. Sklonuj repozytorium:
```bash
git clone https://github.com/twoj-username/przeszukiwarka-pdf.git
cd przeszukiwarka-pdf
```

2. Utwórz i aktywuj środowisko wirtualne:
```bash
python -m venv venv
source venv/bin/activate
```

3. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

4. Uruchom aplikację:
```bash
python src/main.py
```

## Instalacja na Windows

1. Sklonuj repozytorium lub skopiuj pliki projektu (bez katalogu `venv`):
```bash
git clone https://github.com/twoj-username/przeszukiwarka-pdf.git
cd przeszukiwarka-pdf
```

2. Utwórz i aktywuj środowisko wirtualne:
```bash
# Utworzenie środowiska
python -m venv venv

# Aktywacja środowiska (w PowerShell)
.\venv\Scripts\Activate.ps1

# LUB w klasycznym wierszu poleceń (cmd.exe)
.\venv\Scripts\activate.bat
```

3. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

4. Uruchom aplikację:
```bash
python src\main.py
```

## Przenoszenie między systemami operacyjnymi

1. **NIE PRZENOŚ** katalogu `venv` między systemami! Zamiast tego:
   - Skopiuj wszystkie pliki projektu OPRÓCZ katalogu `venv`
   - Na nowym systemie utwórz świeże środowisko wirtualne
   - Zainstaluj zależności z requirements.txt

2. **Ważne uwagi:**
   - Ścieżki w Windows używają `\` zamiast `/`
   - Skrypty aktywacyjne są różne dla każdego systemu
   - Niektóre pakiety mogą wymagać dodatkowej konfiguracji na Windows

3. **Rozwiązywanie problemów:**
   - Jeśli pojawi się błąd z `python-magic` na Windows:
     ```bash
     pip uninstall python-magic
     pip install python-magic-bin
     ```
   - Jeśli pojawią się problemy z kodowaniem tekstu:
     ```bash
     # W PowerShell
     $env:PYTHONIOENCODING = "utf-8"
     # LUB w cmd
     set PYTHONIOENCODING=utf-8
     ```

## Użycie

1. Uruchom aplikację
2. Kliknij przycisk "Wybierz folder z dokumentami" i wskaż folder z plikami PDF
3. Wpisz tekst do wyszukania w polu wyszukiwania
4. Kliknij przycisk "Szukaj" lub naciśnij Enter
5. Wyniki pojawią się w tabeli poniżej
6. Kliknij na wynik, aby zobaczyć podgląd znalezionych fragmentów
7. Kliknij dwukrotnie na wynik, aby otworzyć plik PDF

## Funkcje wyszukiwania

- Wyszukiwanie jest niewrażliwe na wielkość liter
- Wyniki są sortowane według trafności (współczynnik Jaccarda)
- Dla każdego wyniku wyświetlany jest:
  - Tytuł (nazwa pliku)
  - Trafność (w procentach)
  - Ścieżka do pliku
  - Podgląd znalezionych fragmentów z kontekstem

## Konfiguracja

Aplikacja używa pliku `config.json` do przechowywania ustawień:

- `window_width`: Szerokość okna (domyślnie: 800)
- `window_height`: Wysokość okna (domyślnie: 600)
- `last_directory`: Ostatnio używany folder

## Licencja

MIT 