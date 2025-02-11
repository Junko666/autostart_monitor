@echo off

REM -------------------------------
REM 1) System-Python ermitteln
REM -------------------------------
echo [1/5] System-Python ermitteln ...
for /f "delims=" %%P in ('where python') do (
    set "SYSTEM_PYTHON=%%P"
    goto :gotPython
)

echo Konnte keinen Python-Treiber finden.
pause
exit /b 1

:gotPython
echo Gefundener Python-Pfad: %SYSTEM_PYTHON%
echo.

REM -------------------------------
REM 2) Virtuelle Umgebung erstellen
REM -------------------------------
echo [2/5] Erstelle bzw. aktualisiere virtuelle Umgebung "venv" ...
if not exist venv (
    "%SYSTEM_PYTHON%" -m venv venv
) else (
    echo Verzeichnis "venv" existiert bereits, ggf. wird die alte Umgebung weiterbenutzt.
)

if %ERRORLEVEL% NEQ 0 (
    echo Fehler beim Erstellen der virtuellen Umgebung.
    pause
    exit /b %ERRORLEVEL%
)
echo.

REM -------------------------------
REM 3) Aktivieren der virtuellen Umgebung
REM -------------------------------
echo [3/5] Aktiviere virtuelle Umgebung ...
call venv\Scripts\activate

if %ERRORLEVEL% NEQ 0 (
    echo Fehler beim Aktivieren der virtuellen Umgebung.
    pause
    exit /b %ERRORLEVEL%
)
echo.

REM -------------------------------
REM 4) Pip aktualisieren und PyInstaller installieren
REM -------------------------------
echo [4/5] Aktualisiere pip und installiere PyInstaller ...
python -m pip install --upgrade pip
python -m pip install pyinstaller

if %ERRORLEVEL% NEQ 0 (
    echo Fehler beim Installieren von PyInstaller.
    pause
    exit /b %ERRORLEVEL%
)
echo.

REM -------------------------------
REM 5) Executable erstellen
REM -------------------------------
echo [5/5] Erstelle Executable mit PyInstaller ...
python -m pyinstaller --noconfirm --onefile --windowed --icon="autostart_monitor.ico" "autostart_monitor.py"

if %ERRORLEVEL% NEQ 0 (
    echo Fehler beim Erstellen des Executables.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Fertig! Deine EXE befindet sich im Ordner "dist".
pause
