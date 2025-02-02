# autostart_monitor


Download precompiled .exe file:
https://drive.google.com/file/d/1DGvHrQz69dM82pknP6AnQi7RykHWLReO/view?usp=sharing


# README.md (English)

## Autostart Monitor

Autostart Monitor is a desktop application designed to monitor and manage the autostart entries on Windows systems. It allows users to keep track of changes in startup folders, registry entries, services, and scheduled tasks. The application provides notifications for any detected changes, ensuring that users are aware of any modifications that could affect system performance or security.

### Features

- Monitor startup folders, registry entries, services, and scheduled tasks.
- Notifications via Windows Toast and dialog messages.
- Customizable settings including scan interval, language, and dark mode.
- Auto-hide feature to minimize the application after a specified time.

### Dependencies

- Python 3.x
- PyQt6
- win10toast
- logging
- json
- threading
- ctypes
- winsound
- winreg

### Installation

1. Clone the repository or download the source code.
2. Install the required dependencies using pip:
   ```bash
   pip install PyQt6 win10toast
   ```
3. Run the application:
   ```bash
   python autostart_monitor.py
   ```

### Usage

1. Launch the application.
2. Select the methods you want to monitor (Startup folders, Registry, Services, Scheduled Tasks).
3. Choose your preferred notification methods (Windows Toast, Dialog).
4. Set the scan interval and other preferences.
5. Start monitoring by clicking the "Start Monitoring" button.

### Logging

The application logs all activities and errors to a file named `monitor.log`. This log file can be useful for troubleshooting and understanding the application's behavior.

### License

This project is licensed under the MIT License. See the LICENSE file for more details.

---

# README.md (Deutsch)

## Autostart Monitor

Der Autostart Monitor ist eine Desktop-Anwendung, die entwickelt wurde, um die Autostart-Einträge auf Windows-Systemen zu überwachen und zu verwalten. Die Anwendung ermöglicht es Benutzern, Änderungen in den Startup-Ordnern, Registrierungseinträgen, Diensten und geplanten Aufgaben zu verfolgen. Sie bietet Benachrichtigungen für alle erkannten Änderungen, sodass die Benutzer über Modifikationen informiert sind, die die Systemleistung oder -sicherheit beeinträchtigen könnten.

### Funktionen

- Überwachung von Startup-Ordnern, Registrierungseinträgen, Diensten und geplanten Aufgaben.
- Benachrichtigungen über Windows Toast und Dialognachrichten.
- Anpassbare Einstellungen, einschließlich Scan-Intervall, Sprache und Dunkelmodus.
- Auto-Hide-Funktion, um die Anwendung nach einer bestimmten Zeit zu minimieren.

### Abhängigkeiten

- Python 3.x
- PyQt6
- win10toast
- logging
- json
- threading
- ctypes
- winsound
- winreg

### Installation

1. Klonen Sie das Repository oder laden Sie den Quellcode herunter.
2. Installieren Sie die erforderlichen Abhängigkeiten mit pip:
   ```bash
   pip install PyQt6 win10toast
   ```
3. Führen Sie die Anwendung aus:
   ```bash
   python autostart_monitor.py
   ```

### Verwendung

1. Starten Sie die Anwendung.
2. Wählen Sie die Methoden aus, die Sie überwachen möchten (Startup-Ordner, Registrierung, Dienste, Geplante Aufgaben).
3. Wählen Sie Ihre bevorzugten Benachrichtigungsmethoden (Windows Toast, Dialog).
4. Stellen Sie das Scan-Intervall und andere Präferenzen ein.
5. Starten Sie die Überwachung, indem Sie auf die Schaltfläche "Überwachung starten" klicken.

### Protokollierung

Die Anwendung protokolliert alle Aktivitäten und Fehler in einer Datei namens `monitor.log`. Diese Protokolldatei kann nützlich sein, um Probleme zu beheben und das Verhalten der Anwendung zu verstehen.

### Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Weitere Informationen finden Sie in der LICENSE-Datei.
