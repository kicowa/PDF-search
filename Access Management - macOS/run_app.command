#!/bin/bash

# Przejdź do katalogu ze skryptem
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Sprawdź czy Python jest zainstalowany
if ! command -v python3 &> /dev/null; then
    echo "Python nie jest zainstalowany. Zainstaluj Python ze strony python.org"
    exit 1
fi

# Sprawdź czy virtualenv jest zainstalowany
if ! python3 -m pip list | grep -q virtualenv; then
    echo "Instalowanie virtualenv..."
    python3 -m pip install virtualenv
fi

# Stwórz wirtualne środowisko jeśli nie istnieje
if [ ! -d "venv" ]; then
    echo "Tworzenie wirtualnego środowiska..."
    python3 -m virtualenv venv
fi

# Aktywuj wirtualne środowisko
source "$SCRIPT_DIR/venv/bin/activate"

# Zainstaluj wymagane pakiety
echo "Instalowanie wymaganych pakietów..."
pip install streamlit pandas openpyxl

# Uruchom aplikację
echo "Uruchamianie aplikacji..."
streamlit run "$SCRIPT_DIR/nowy skrypt wersja 2.py" 