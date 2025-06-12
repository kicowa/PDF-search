@echo off
REM Zatrzymaj wszystkie poprzednie instancje streamlit
taskkill /F /IM "streamlit.exe" /T 2>nul
taskkill /F /IM "python.exe" /T 2>nul

REM Przejdz do katalogu skryptu
cd /d "%~dp0"

REM Sprawdz czy srodowisko wirtualne istnieje
if not exist "venv\Scripts\activate.bat" (
    echo Tworzenie nowego srodowiska wirtualnego...
    python -m venv venv
    if errorlevel 1 (
        echo Probuje z alternatywna komenda...
        py -m venv venv
        if errorlevel 1 (
            echo Blad podczas tworzenia srodowiska wirtualnego!
            echo Upewnij sie, ze Python jest zainstalowany i dodany do PATH.
            pause
            exit /b 1
        )
    )
)

REM Aktywuj srodowisko wirtualne
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Blad podczas aktywacji srodowiska wirtualnego!
    pause
    exit /b 1
)

REM Sprawdz czy requirements.txt istnieje
if not exist "requirements.txt" (
    echo Blad: Nie znaleziono pliku requirements.txt!
    pause
    exit /b 1
)

REM Instaluj/aktualizuj pakiety
echo Instalowanie/aktualizowanie wymaganych pakietow...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Blad podczas instalacji pakietow!
    pause
    exit /b 1
)

REM Sprawdz czy plik skryptu istnieje
if not exist "nowy skrypt wersja 2.py" (
    echo Blad: Nie znaleziono pliku 'nowy skrypt wersja 2.py'!
    pause
    exit /b 1
)

echo.
echo Uruchamianie aplikacji Streamlit...
echo Aby zatrzymac aplikacje, nacisnij Ctrl+C
echo.
streamlit run "nowy skrypt wersja 2.py"
if errorlevel 1 (
    echo Blad podczas uruchamiania aplikacji!
    pause
    exit /b 1
)

REM Jeśli chcesz, żeby okno konsoli nie zamykało się od razu po błędzie, odkomentuj poniższą linię:
REM pause 