# Importowanie wymaganych bibliotek
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

# Dodaj po inicjalizacji df, przed podziałem na kolumny

# Funkcja do wczytywania zapisanej liczby użytkowników
def load_total_users(excel_path):
    try:
        total_users_dict = {}
        
        # Próba wczytania arkusza Summary
        try:
            summary_df = pd.read_excel(excel_path, sheet_name='Summary', engine='openpyxl')
            # Pobierz departamenty i liczby użytkowników z Summary (pomijając wiersz SUMA)
            summary_dict = dict(zip(
                summary_df[summary_df['Department'] != 'SUMA']['Department'],
                summary_df[summary_df['Department'] != 'SUMA']['Liczba użytkowników']
            ))
            total_users_dict.update(summary_dict)
        except Exception:
            pass  # Jeśli nie ma arkusza Summary, kontynuuj
        
        # Próba wczytania arkusza Total_Users (zachowanie kompatybilności wstecznej)
        try:
            total_users_df = pd.read_excel(excel_path, sheet_name='Total_Users', engine='openpyxl')
            total_users_dict.update(dict(zip(total_users_df['Department'], total_users_df['Total Users'])))
        except Exception:
            pass
            
        return total_users_dict
    except Exception:
        return {}

# Funkcja do zapisywania liczby użytkowników
def save_total_users(total_users_dict, excel_path):
    try:
        total_users_df = pd.DataFrame({
            'Department': list(total_users_dict.keys()),
            'Total Users': list(total_users_dict.values())
        })
        with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            total_users_df.to_excel(writer, sheet_name='Total_Users', index=False)
        return True
    except Exception as e:
        st.error(f"Błąd podczas zapisywania liczby użytkowników: {str(e)}")
        return False

# Inicjalizacja słownika z liczbą użytkowników
if 'total_users_dict' not in st.session_state:
    st.session_state.total_users_dict = {}

# Wczytaj zapisane wartości jeśli istnieją
if POC_PATH:
    st.session_state.total_users_dict = load_total_users(POC_PATH)

# Dodaj sekcję do wprowadzania liczby użytkowników
st.sidebar.header('Całkowita liczba użytkowników')
st.sidebar.info('Wprowadź całkowitą liczbę użytkowników dla każdego departamentu')

# Funkcja do pobierania wszystkich unikalnych departamentów
def get_all_departments(df, excel_path):
    """
    Pobiera unikalne departamenty z głównego arkusza i z arkusza Summary
    """
    departments = set(df['Department'].dropna().unique())
    
    try:
        # Próba wczytania departamentów z arkusza Summary
        summary_df = pd.read_excel(excel_path, sheet_name='Summary', engine='openpyxl')
        summary_depts = set(summary_df[summary_df['Department'] != 'SUMA']['Department'])
        departments.update(summary_depts)
    except Exception:
        pass
        
    return sorted(list(departments))

# Przygotowanie danych do formularzy
# Pobieranie unikalnych departamentów (posortowanych) i nazw środowisk
departments = get_all_departments(df, POC_PATH) if POC_PATH else sorted(df['Department'].dropna().unique())
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
        full_name = st.text_input('Full name*', help='Pole wymagane')
        department = st.selectbox(
            'Department*', 
            [''] + list(departments) if len(departments) > 0 else ['Nowy Department'],
            help='Pole wymagane'
        )
        business_reason = st.text_input('Business reason', 
                                      value='Business use',
                                      help='Domyślnie: Business use')
        selected_envs = st.multiselect('Środowiska (zaznacz, gdzie dodać X)*', 
                                     env_columns,
                                     help='Wybierz przynajmniej jedno środowisko')
        submitted = st.form_submit_button('Dodaj')

        if submitted:
            # Walidacja pól
            validation_errors = []
            
            if not full_name.strip():
                validation_errors.append("❌ Pole 'Full name' jest wymagane")
            
            if not department:
                validation_errors.append("❌ Pole 'Department' jest wymagane")
            
            if not selected_envs:
                validation_errors.append("❌ Wybierz przynajmniej jedno środowisko")
            
            # Sprawdź czy użytkownik już istnieje
            if full_name.strip() and department:
                existing_user = df[
                    (df['Full name'].str.strip().str.lower() == full_name.strip().lower()) &
                    (df['Department'].str.strip().str.lower() == department.strip().lower())
                ]
                if not existing_user.empty:
                    validation_errors.append(f"❌ Użytkownik {full_name} już istnieje w departamencie {department}")
            
            # Jeśli są błędy, wyświetl je
            if validation_errors:
                for error in validation_errors:
                    st.error(error)
            elif not POC_PATH:
                st.error('❌ Najpierw wybierz lub utwórz plik Excel!')
            else:
                try:
                    # Dodawanie nowego użytkownika
                    new_row = {col: '' for col in df.columns}
                    new_row['Full name'] = full_name.strip()
                    new_row['Department'] = department
                    new_row['Business reason'] = business_reason.strip() if business_reason.strip() else 'Business use'
                    
                    # Dodawanie zaznaczonych środowisk
                    for env in selected_envs:
                        new_row[env] = 'X'
                    
                    # Dodawanie wiersza do DataFrame i zapis do pliku
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    df.to_excel(POC_PATH, index=False, engine='openpyxl')
                    st.success(f'✅ Dodano użytkownika {full_name} do pliku!')
                    
                    # Odśwież formularz - wyczyść pola
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Błąd podczas zapisywania do pliku: {str(e)}")

# Funkcja do generowania podsumowania departamentów i środowisk
def generate_summary(df, total_users_dict):
    """
    Generuje podsumowanie ilości 'X' dla każdego departamentu i środowiska,
    używając ręcznie wprowadzonej liczby użytkowników
    """
    # Pobierz unikalne departamenty i środowiska
    departments = sorted(df['Department'].dropna().unique())
    env_columns = [col for col in df.columns if col not in ['Full name', 'Department', 'Business reason']]
    
    # Przygotuj DataFrame na podsumowanie
    summary_data = []
    
    # Dla każdego departamentu policz statystyki
    for dept in departments:
        dept_data = {'Department': dept}
        dept_df = df[df['Department'] == dept]
        
        # Użyj ręcznie wprowadzonej liczby użytkowników
        total_users = total_users_dict.get(dept, 0)
        dept_data['Liczba użytkowników'] = total_users
        
        # Dla każdego środowiska policz statystyki
        for env in env_columns:
            # Liczba uprawnień (X) w danym środowisku
            x_count = dept_df[env].fillna('').astype(str).str.strip().str.upper().eq('X').sum()
            
            # Podstawowe liczby
            dept_data[f'{env} - Liczba X'] = x_count
            
            # Oblicz procent
            percentage = (x_count / total_users * 100) if total_users > 0 else 0
            dept_data[f'{env} - Procent'] = f'{percentage:.1f}%'
            
        summary_data.append(dept_data)
    
    # Utwórz DataFrame z podsumowaniem
    summary_df = pd.DataFrame(summary_data)
    
    # Dodaj wiersz z sumą całkowitą
    total_row = {'Department': 'SUMA'}
    total_row['Liczba użytkowników'] = sum(total_users_dict.values())
    
    for env in env_columns:
        total_x = summary_df[f'{env} - Liczba X'].sum()
        total_row[f'{env} - Liczba X'] = total_x
        total_percentage = (total_x / total_row['Liczba użytkowników'] * 100) if total_row['Liczba użytkowników'] > 0 else 0
        total_row[f'{env} - Procent'] = f'{total_percentage:.1f}%'
    
    summary_df = pd.concat([summary_df, pd.DataFrame([total_row])], ignore_index=True)
    
    return summary_df

# Funkcja do zapisywania podsumowania w Excel
def save_summary_to_excel(current_summary_df, excel_path):
    """
    Zapisuje podsumowanie do arkusza 'Summary' w pliku Excel, zachowując ręczne zmiany
    """
    try:
        # Wczytaj istniejący arkusz Summary, jeśli istnieje
        try:
            existing_summary_df = pd.read_excel(excel_path, sheet_name='Summary', engine='openpyxl')
            
            # Usuń wiersz SUMA z obu DataFrame'ów
            existing_without_sum = existing_summary_df[existing_summary_df['Department'] != 'SUMA'].copy()
            current_without_sum = current_summary_df[current_summary_df['Department'] != 'SUMA'].copy()
            
            # Zachowaj ręcznie dodane departamenty
            manual_depts = set(existing_without_sum['Department']) - set(current_without_sum['Department'])
            manual_rows = existing_without_sum[existing_without_sum['Department'].isin(manual_depts)]
            
            # Połącz automatycznie wygenerowane dane z ręcznie dodanymi
            merged_df = pd.concat([current_without_sum, manual_rows], ignore_index=True)
            
            # Posortuj po nazwie departamentu
            merged_df = merged_df.sort_values('Department').reset_index(drop=True)
            
            # Przelicz sumę
            total_row = {'Department': 'SUMA'}
            total_row['Liczba użytkowników'] = merged_df['Liczba użytkowników'].sum()
            
            # Przelicz sumy dla każdej kolumny z 'X'
            for col in merged_df.columns:
                if ' - Liczba X' in col:
                    total_row[col] = merged_df[col].sum()
                    # Przelicz procent
                    if total_row['Liczba użytkowników'] > 0:
                        percentage = (total_row[col] / total_row['Liczba użytkowników']) * 100
                        total_row[col.replace('Liczba X', 'Procent')] = f'{percentage:.1f}%'
                    else:
                        total_row[col.replace('Liczba X', 'Procent')] = '0.0%'
            
            # Dodaj wiersz sumy
            final_df = pd.concat([merged_df, pd.DataFrame([total_row])], ignore_index=True)
            
        except Exception:
            # Jeśli nie ma arkusza Summary, użyj bieżącego DataFrame
            final_df = current_summary_df
        
        # Wczytaj wszystkie istniejące arkusze (oprócz Summary)
        with pd.ExcelFile(excel_path) as excel_file:
            existing_sheets = {
                name: pd.read_excel(excel_file, sheet_name=name)
                for name in excel_file.sheet_names
                if name != 'Summary'
            }
        
        # Zapisz wszystkie arkusze z powrotem do pliku
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Najpierw zapisz pozostałe arkusze
            for sheet_name, sheet_data in existing_sheets.items():
                sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Na końcu zapisz zaktualizowany arkusz Summary
            final_df.to_excel(writer, sheet_name='Summary', index=False)
            
        return True
    except Exception as e:
        st.error(f"Błąd podczas zapisywania podsumowania: {str(e)}")
        return False

# Funkcja do weryfikacji czy były ręczne zmiany w Excel
def verify_excel_changes(current_summary_df, excel_path):
    """
    Sprawdza czy były ręczne zmiany w arkuszu Summary i aktualizuje dane jeśli potrzeba
    """
    try:
        # Wczytaj arkusz Summary z pliku Excel
        excel_summary_df = pd.read_excel(excel_path, sheet_name='Summary', engine='openpyxl')
        
        # Usuń wiersz SUMA z obu DataFrame'ów do porównania
        current_without_sum = current_summary_df[current_summary_df['Department'] != 'SUMA'].copy()
        excel_without_sum = excel_summary_df[excel_summary_df['Department'] != 'SUMA'].copy()
        
        # Sprawdź czy są nowe departamenty w Excel
        excel_depts = set(excel_without_sum['Department'])
        current_depts = set(current_without_sum['Department'])
        
        new_depts = excel_depts - current_depts
        if new_depts:
            st.info(f"⚠️ Znaleziono nowe departamenty w arkuszu Summary: {', '.join(new_depts)}")
            
        # Sprawdź zmiany w liczbie użytkowników
        for dept in excel_depts & current_depts:
            excel_users = excel_without_sum[excel_without_sum['Department'] == dept]['Liczba użytkowników'].iloc[0]
            current_users = current_without_sum[current_without_sum['Department'] == dept]['Liczba użytkowników'].iloc[0]
            
            if excel_users != current_users:
                st.info(f"⚠️ Zmieniono liczbę użytkowników dla departamentu {dept}: {current_users} -> {excel_users}")
                
        # Aktualizuj słownik total_users_dict
        if new_depts or (excel_depts & current_depts):
            st.session_state.total_users_dict.update(
                dict(zip(excel_without_sum['Department'], excel_without_sum['Liczba użytkowników']))
            )
            
    except Exception:
        # Jeśli arkusz nie istnieje, nie ma co weryfikować
        pass

# Modyfikacja sekcji wyświetlania podsumowania
st.header('Podsumowanie uprawnień')

if df is not None and not df.empty:
    # Generuj podsumowanie używając ręcznie wprowadzonej liczby użytkowników
    summary_df = generate_summary(df, st.session_state.total_users_dict)
    
    # Wyświetl podsumowanie w formie tabeli
    st.write("Statystyki uprawnień per Department i Environment:")
    
    # Formatowanie wyświetlania
    st.dataframe(
        summary_df,
        column_config={
            'Liczba użytkowników': st.column_config.NumberColumn(
                'Liczba użytkowników',
                help='Całkowita liczba użytkowników w departamencie'
            ),
            **{
                f'{env} - Liczba X': st.column_config.NumberColumn(
                    f'{env} - Liczba X',
                    help=f'Liczba uprawnień X w środowisku {env}'
                )
                for env in [col.replace(' - Liczba X', '') 
                           for col in summary_df.columns 
                           if col.endswith(' - Liczba X')]
            },
            **{
                f'{env} - Procent': st.column_config.TextColumn(
                    f'{env} - %',
                    help=f'Procent użytkowników z uprawnieniem w środowisku {env}'
                )
                for env in [col.replace(' - Procent', '') 
                           for col in summary_df.columns 
                           if col.endswith(' - Procent')]
            }
        }
    )
    
    # Jeśli mamy ścieżkę do pliku Excel
    if POC_PATH:
        # Sprawdź czy były ręczne zmiany
        verify_excel_changes(summary_df, POC_PATH)
        
        # Zapisz podsumowanie do Excel
        if save_summary_to_excel(summary_df, POC_PATH):
            st.success("✅ Podsumowanie zostało zaktualizowane w pliku Excel")

# Formularz do wprowadzania liczby użytkowników
with st.sidebar.form("total_users_form"):
    changed = False
    for dept in departments:
        current_value = st.session_state.total_users_dict.get(dept, 0)
        new_value = st.number_input(
            f"Liczba użytkowników - {dept}",
            min_value=0,
            value=int(current_value),
            step=1,
            key=f"total_users_{dept}"
        )
        if new_value != current_value:
            st.session_state.total_users_dict[dept] = new_value
            changed = True
    
    if st.form_submit_button("Zapisz liczbę użytkowników"):
        if POC_PATH and changed:
            if save_total_users(st.session_state.total_users_dict, POC_PATH):
                st.sidebar.success("✅ Zapisano liczbę użytkowników") 