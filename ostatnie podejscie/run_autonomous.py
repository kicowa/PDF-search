
import subprocess
import os
import tempfile
import sys

# Twoja aplikacja Streamlit jako tekst
app_code = r"""# Importowanie wymaganych bibliotek
import streamlit as st  # Framework do tworzenia aplikacji webowych
import pandas as pd    # Biblioteka do manipulacji danymi
import os             # Biblioteka do operacji na systemie plików
from pathlib import Path  # Biblioteka do obsługi ścieżek
import glob           # Biblioteka do wyszukiwania plików
import sys           # For executable path handling
import traceback     # For detailed error reporting

sys.stdout = open("log.txt", "w")
sys.stderr = sys.stdout

def get_base_path():
    """Get the base path for the application, works both for dev and PyInstaller"""
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        return Path(sys._MEIPASS)
    else:
        # Running in normal Python environment
        return Path(os.path.dirname(os.path.abspath(__file__)))

# Konfiguracja strony Streamlit
st.set_page_config(page_title='Wyszukiwarka i dodawanie użytkowników POC.xlsx', layout='centered')
st.title('Wyszukiwarka i dodawanie użytkowników POC.xlsx')

# Funkcja do znajdowania plików Excel w bieżącym katalogu
def get_excel_files():
    base_path = get_base_path()
    excel_files = list(base_path.glob("*.xlsx"))
    return sorted([f.name for f in excel_files])  # Sortowanie alfabetyczne

# Dodaj informację o ścieżce bazowej
base_path = get_base_path()
st.sidebar.info(f"Katalog aplikacji: {base_path}")

# Konfiguracja wyboru pliku Excel
st.sidebar.header('Wybór pliku Excel')
file_option = st.sidebar.radio(
    "Wybierz sposób wskazania pliku:",
    ["Pliki lokalne", "Wybierz plik z systemu", "Podaj ścieżkę"]
)

POC_PATH = None
df = None

if file_option == "Pliki lokalne":
    excel_files = get_excel_files()
    if not excel_files:
        st.sidebar.warning("Nie znaleziono plików .xlsx w bieżącym katalogu!")
        # Inicjalizacja pustego DataFrame z wymaganymi kolumnami
        df = pd.DataFrame(columns=['Full name', 'Department', 'Business reason'])
    else:
        selected_file = st.sidebar.selectbox(
            "Wybierz plik Excel z katalogu:",
            excel_files,
            help="Lista wszystkich plików .xlsx w bieżącym katalogu"
        )
        POC_PATH = selected_file
elif file_option == "Wybierz plik z systemu":
    uploaded_file = st.sidebar.file_uploader("Wybierz plik Excel", type=['xlsx'])
    if uploaded_file is not None:
        # Zapisz tymczasowo uploadowany plik
        with open('temp_upload.xlsx', 'wb') as f:
            f.write(uploaded_file.getvalue())
        POC_PATH = 'temp_upload.xlsx'
    else:
        # Inicjalizacja pustego DataFrame z wymaganymi kolumnami
        df = pd.DataFrame(columns=['Full name', 'Department', 'Business reason'])
else:  # Podaj ścieżkę
    file_path = st.sidebar.text_input("Podaj pełną ścieżkę do pliku Excel:", "")
    if file_path.strip():
        # Sprawdź czy ścieżka istnieje i czy to plik Excel
        path = Path(file_path)
        if path.exists() and path.suffix.lower() in ['.xlsx']:
            POC_PATH = file_path
        else:
            st.sidebar.error("Podana ścieżka jest nieprawidłowa lub plik nie jest w formacie .xlsx")
            # Inicjalizacja pustego DataFrame z wymaganymi kolumnami
            df = pd.DataFrame(columns=['Full name', 'Department', 'Business reason'])
    else:
        # Inicjalizacja pustego DataFrame z wymaganymi kolumnami
        df = pd.DataFrame(columns=['Full name', 'Department', 'Business reason'])

# Wyświetl informację o aktualnie wybranym pliku
if POC_PATH:
    st.sidebar.info(f"Aktualnie wybrany plik: {POC_PATH}")
    # Funkcja do wczytywania danych z pliku Excel
    try:
        df = pd.read_excel(POC_PATH, engine='openpyxl')
    except Exception as e:
        st.error(f"Błąd podczas wczytywania pliku: {str(e)}")
        # Inicjalizacja pustego DataFrame z wymaganymi kolumnami
        df = pd.DataFrame(columns=['Full name', 'Department', 'Business reason'])

# Jeśli df jest None, inicjalizuj pusty DataFrame
if df is None:
    try:
        # Próba wczytania domyślnego pliku POC.xlsx z katalogu aplikacji
        default_poc = base_path / "POC.xlsx"
        if default_poc.exists():
            df = pd.read_excel(default_poc, engine='openpyxl')
            POC_PATH = str(default_poc)
            st.sidebar.success(f"Wczytano domyślny plik: {default_poc}")
        else:
            df = pd.DataFrame(columns=['Full name', 'Department', 'Business reason'])
            st.sidebar.warning("Nie znaleziono domyślnego pliku POC.xlsx")
    except Exception as e:
        st.sidebar.error(f"Błąd podczas wczytywania domyślnego pliku: {str(e)}")
        st.sidebar.text(traceback.format_exc())
        df = pd.DataFrame(columns=['Full name', 'Department', 'Business reason'])

# Przygotowanie danych do formularzy
# Pobieranie unikalnych departamentów (posortowanych) i nazw środowisk
departments = sorted(df['Department'].dropna().unique())
env_columns = [col for col in df.columns if col not in ['Full name', 'Department', 'Business reason']]

# Podział interfejsu na dwie kolumny
col1, col2 = st.columns(2)

# LEWA KOLUMNA - Wyszukiwarka użytkowników
with col1:
    st.header('Wyszukiwarka użytkowników')
    username = st.text_input('Podaj nazwę użytkownika:')
    
    if st.button('Szukaj'):
        if not username.strip():
            st.warning('Wpisz nazwę użytkownika!')
        else:
            # Wczytanie najnowszych danych przed wyszukiwaniem
            if POC_PATH:
                try:
                    df = pd.read_excel(POC_PATH, engine='openpyxl')
                except Exception as e:
                    st.error(f"Błąd podczas wczytywania pliku: {str(e)}")
            # Wyszukiwanie użytkownika (bez uwzględnienia wielkości liter)
            results = df[df['Full name'].str.lower() == username.strip().lower()]
            
            if results.empty:
                st.info(f'Nie znaleziono użytkownika: {username}')
            else:
                # Wyświetlanie znalezionych wyników
                for idx, row in results.iterrows():
                    dept = row['Department']
                    envs = []
                    # Sprawdzanie, które środowiska są przypisane (oznaczone 'X')
                    for col in env_columns:
                        if str(row[col]).strip().upper() == 'X':
                            envs.append(col)
                    if envs:
                        st.write(f"**Department:** {dept}")
                        st.write(f"**Środowiska:** {', '.join(envs)}")
                        st.markdown('---')

# PRAWA KOLUMNA - Formularz dodawania użytkownika
with col2:
    st.header('Dodaj nowego użytkownika')
    with st.form('add_user_form'):
        # Pola formularza
        full_name = st.text_input('Full name')
        department = st.selectbox('Department', [''] + list(departments) if len(departments) > 0 else ['Nowy Department'])
        business_reason = st.text_input('Business reason')
        selected_envs = st.multiselect('Środowiska (zaznacz, gdzie dodać X)', env_columns)
        submitted = st.form_submit_button('Dodaj')

        if submitted:
            if not full_name.strip():
                st.warning('Wpisz nazwę użytkownika!')
            elif not POC_PATH:
                st.error('Najpierw wybierz lub utwórz plik Excel!')
            else:
                try:
                    # Sprawdzanie czy użytkownik już istnieje w danym departamencie
                    mask = (df['Full name'].str.strip().str.lower() == full_name.strip().lower()) & (df['Department'] == department)
                    
                    if mask.any():
                        # Aktualizacja istniejącego użytkownika
                        idx = df[mask].index[0]
                        # Dodawanie zaznaczonych środowisk
                        for env in selected_envs:
                            df.at[idx, env] = 'X'
                        # Aktualizacja business reason
                        df.at[idx, 'Business reason'] = business_reason
                        df.to_excel(POC_PATH, index=False, engine='openpyxl')
                        st.success(f'Zaktualizowano użytkownika {full_name} w departmentcie {department}!')
                    else:
                        # Dodawanie nowego użytkownika
                        # Tworzenie nowego wiersza z pustymi wartościami
                        new_row = {col: '' for col in df.columns}
                        new_row['Full name'] = full_name.strip()
                        new_row['Department'] = department
                        new_row['Business reason'] = business_reason
                        # Dodawanie zaznaczonych środowisk
                        for env in selected_envs:
                            new_row[env] = 'X'
                        # Dodawanie wiersza do DataFrame i zapis do pliku
                        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                        df.to_excel(POC_PATH, index=False, engine='openpyxl')
                        st.success(f'Dodano użytkownika {full_name} do pliku!')
                except Exception as e:
                    st.error(f"Błąd podczas zapisywania do pliku: {str(e)}") """

# Zapisz aplikację tymczasowo jako .py
with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py", encoding="utf-8") as f:
    f.write(app_code)
    app_path = f.name

# Uruchom tymczasową aplikację za pomocą lokalnego streamlit
subprocess.run(["streamlit", "run", app_path])
