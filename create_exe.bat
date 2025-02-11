@echo off

echo Installiere pyinstaller...
pip install pyinstaller

if %ERRORLEVEL% NEQ 0 (
   echo Fehler beim Installieren von pyinstaller.
   pause
   exit /b %ERRORLEVEL%
)

echo Erstelle ausführbare Datei mit pyinstaller...
python -m pyinstaller --noconfirm --onefile --windowed --icon "autostart_monitor.ico" "autostart_monitor.py"

if %ERRORLEVEL% NEQ 0 (
   echo Fehler bei der Erstellung der ausführbaren Datei.
   pause
   exit /b %ERRORLEVEL%
)

echo Erstellung abgeschlossen.
pause
