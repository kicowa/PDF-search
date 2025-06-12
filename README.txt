INSTRUKCJA INSTALACJI I URUCHOMIENIA APLIKACJI
==========================================

1. WYMAGANIA WSTĘPNE
-------------------
- System Windows
- Python 3.x (jeśli nie jest zainstalowany, patrz punkt 2)
- Dostęp do internetu (wymagany tylko przy pierwszym uruchomieniu)

2. INSTALACJA PYTHONA (jeśli nie jest zainstalowany)
-------------------------------------------------
a) Wejdź na stronę: https://www.python.org/downloads/
b) Kliknij "Download Python 3.x.x" (najnowsza wersja)
c) Uruchom pobrany instalator
d) WAŻNE: Zaznacz opcję "Add Python to PATH" podczas instalacji
e) Kliknij "Install Now"

3. PLIKI APLIKACJI
-----------------
Upewnij się, że masz wszystkie wymagane pliki w tym samym folderze:
- nowy skrypt wersja 2.py
- run_app.bat
- requirements.txt
- POC.xlsx (jeśli używasz pliku z danymi)

4. URUCHOMIENIE APLIKACJI
------------------------
a) Kliknij dwukrotnie na plik run_app.bat
b) Przy pierwszym uruchomieniu:
   - Poczekaj, aż zostaną zainstalowane wszystkie wymagane pakiety
   - Może to potrwać kilka minut
   - Nie zamykaj okna terminala podczas instalacji
c) Aplikacja uruchomi się automatycznie w przeglądarce
d) Jeśli nie otworzy się automatycznie, otwórz przeglądarkę i wejdź na adres:
   http://localhost:8501

5. ZAMYKANIE APLIKACJI
---------------------
a) Aby zamknąć aplikację, naciśnij Ctrl+C w oknie terminala
b) Możesz też po prostu zamknąć okno terminala

6. ROZWIĄZYWANIE PROBLEMÓW
-------------------------
Jeśli pojawią się problemy:
1. Upewnij się, że Python jest zainstalowany (wpisz 'python --version' w CMD)
2. Sprawdź, czy wszystkie pliki są w tym samym folderze
3. Spróbuj uruchomić run_app.bat ponownie
4. Upewnij się, że masz połączenie z internetem przy pierwszym uruchomieniu

W razie problemów z uruchomieniem, sprawdź komunikaty błędów w oknie terminala. 