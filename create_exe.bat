@echo off

:: 1) Python suchen und Pfad speichern
echo Ermittle Python-Pfad...
for /f "delims=" %%P in ('where python') do set "PYTHON=%%P"
echo Gefundener Python-Pfad: %PYTHON%

:: 2) Virtuelle Umgebung erstellen (Ordnername: venv)
echo Erstelle virtuelle Umgebung "venv" ...
"%PYTHON%" -m venv venv

if %ERRORLEVEL% NEQ 0 (
   echo Fehler beim Erstellen der virtuellen Umgebung.
   pause
   exit /b %ERRORLEVEL%
)

:: 3) Virtuelle Umgebung aktivieren
echo Aktiviere virtuelle Umgebung ...
call venv\Scripts\activate

:: 4) Pip aktualisieren und PyInstaller installieren
echo Aktualisiere pip und installiere PyInstaller ...
python -m pip install --upgrade pip
python -m pip install pyinstaller

if %ERRORLEVEL% NEQ 0 (
   echo Fehler beim Installieren von PyInstaller.
   pause
   exit /b %ERRORLEVEL%
)

:: 5) Executable erstellen
echo Erstelle ausführbare Datei mit PyInstaller ...
python -m pyinstaller --noconfirm --onefile --windowed --icon "autostart_monitor.ico" "autostart_monitor.py"

if %ERRORLEVEL% NEQ 0 (
   echo Fehler bei der Erstellung der ausführbaren Datei.
   pause
   exit /b %ERRORLEVEL%
)

echo Erstellung abgeschlossen. 
pause
