# Importowanie wymaganych bibliotek
import streamlit as st  # Framework do tworzenia aplikacji webowych
import pandas as pd    # Biblioteka do manipulacji danymi
import os             # Biblioteka do operacji na systemie plików
from pathlib import Path  # Biblioteka do obsługi ścieżek
import glob           # Biblioteka do wyszukiwania plików

# Konfiguracja strony Streamlit
st.set_page_config(page_title='Wyszukiwarka i dodawanie użytkowników POC.xlsx', layout='centered')
st.title('Wyszukiwarka i dodawanie użytkowników POC.xlsx')

# Funkcja do znajdowania plików Excel w bieżącym katalogu
def get_excel_files():
    excel_files = glob.glob("*.xlsx")
    return sorted(excel_files)  # Sortowanie alfabetyczne

# Konfiguracja wyboru pliku Excel
st.sidebar.header('Wybór pliku Excel')
file_option = st.sidebar.radio(
    "Wybierz sposób wskazania pliku:",
    ["Pliki lokalne", "Wybierz plik z systemu", "Podaj ścieżkę"]
)

if file_option == "Pliki lokalne":
    excel_files = get_excel_files()
    if not excel_files:
        st.sidebar.warning("Nie znaleziono plików .xlsx w bieżącym katalogu!")
        st.stop()
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
        st.sidebar.warning("Proszę wybrać plik Excel")
        st.stop()
else:  # Podaj ścieżkę
    file_path = st.sidebar.text_input("Podaj pełną ścieżkę do pliku Excel:", "")
    if file_path.strip():
        # Sprawdź czy ścieżka istnieje i czy to plik Excel
        path = Path(file_path)
        if path.exists() and path.suffix.lower() in ['.xlsx']:
            POC_PATH = file_path
        else:
            st.sidebar.error("Podana ścieżka jest nieprawidłowa lub plik nie jest w formacie .xlsx")
            st.stop()
    else:
        st.sidebar.warning("Proszę podać ścieżkę do pliku Excel")
        st.stop()

# Wyświetl informację o aktualnie wybranym pliku
st.sidebar.info(f"Aktualnie wybrany plik: {POC_PATH}")

# Funkcja do wczytywania danych z pliku Excel
def load_data():
    try:
        return pd.read_excel(POC_PATH, engine='openpyxl')
    except Exception as e:
        st.error(f"Błąd podczas wczytywania pliku: {str(e)}")
        st.stop()

# Funkcja do zapisywania danych do pliku Excel
def save_data(df):
    try:
        df.to_excel(POC_PATH, index=False, engine='openpyxl')
    except Exception as e:
        st.error(f"Błąd podczas zapisywania pliku: {str(e)}")
        st.stop()

# Inicjalizacja zmiennych
df = None
error_message = ''

# Próba wczytania danych z pliku Excel
try:
    df = load_data()
except Exception as e:
    error_message = str(e)

# Obsługa błędów wczytywania pliku
if error_message:
    st.error(f'Nie można wczytać pliku Excel: {error_message}')
else:
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
                df = load_data()
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
            department = st.selectbox('Department', departments)
            business_reason = st.text_input('Business reason')
            selected_envs = st.multiselect('Środowiska (zaznacz, gdzie dodać X)', env_columns)
            submitted = st.form_submit_button('Dodaj')

            if submitted:
                if not full_name.strip():
                    st.warning('Wpisz nazwę użytkownika!')
                else:
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
                        save_data(df)
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
                        save_data(df)
                        st.success(f'Dodano użytkownika {full_name} do pliku POC.xlsx!')
                    # Zatrzymanie wykonywania aplikacji po dodaniu/aktualizacji
                    st.stop() 