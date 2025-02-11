@echo off
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --icon "autostart_monitor.ico"  "autostart_monitor.py"
