@echo off

echo Ermittle Python-Pfad...
for /f "delims=" %%P in ('where python') do set "PYTHON=%%P"
echo Gefundener Python-Pfad: %PYTHON%

echo Installiere pyinstaller...
"%PYTHON%" -m pip install --upgrade pip
"%PYTHON%" -m pip install pyinstaller

if %ERRORLEVEL% NEQ 0 (
   echo Fehler beim Installieren von pyinstaller.
   pause
   exit /b %ERRORLEVEL%
)

echo Erstelle ausführbare Datei mit pyinstaller...
"%PYTHON%" -m pyinstaller --noconfirm --onefile --windowed --icon "autostart_monitor.ico" "autostart_monitor.py"

if %ERRORLEVEL% NEQ 0 (
   echo Fehler bei der Erstellung der ausführbaren Datei.
   pause
   exit /b %ERRORLEVEL%
)

echo Erstellung abgeschlossen.
pause
