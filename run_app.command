#!/bin/bash

# Znajdź i zakończ wszystkie poprzednie procesy streamlit
pkill -f "streamlit run"

# Przejdź do katalogu skryptu
cd "$(dirname "$0")"

# Aktywuj środowisko wirtualne
source venv/bin/activate

# Uruchom aplikację Streamlit
streamlit run "nowy skrypt wersja 2.py" 