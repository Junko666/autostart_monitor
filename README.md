# README.md - Autostart Monitor  
### Light Mode (English)  
![image](https://github.com/user-attachments/assets/46e57805-9cc4-4992-aedd-d755698b5721)

### Dark Mode (German)  
![image](https://github.com/user-attachments/assets/622daeaa-c577-4195-9401-2695e04dad70)

A Windows monitoring tool that detects unauthorized changes to autostart locations. Continuously checks startup folders, registry entries, services and scheduled tasks. Alerts via notifications/sounds and provides direct access to relevant system tools for analysis.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Translations](#translations)
- [Developer Notes](#developer-notes)
- [License](#license)
- [Contributors](#contributors)

## Introduction
Autostart Monitor is a security-oriented tool that monitors 12+ Windows autostart locations for unauthorized changes:
- Startup folders (User/All Users)
- Registry entries (HKCU/HKLM Run keys)
- Context menu handlers (Files/Folders/Background)
- System services (Startup type changes)
- Scheduled tasks

Key capabilities:
- Real-time monitoring with configurable interval (10-300s)
- Visual/Sound alerts with actionable dialogs
- Dark/Light mode with smooth animations
- German/English language support
- Persistent configuration

## Features
### Core Monitoring
- **Startup Folders**:  
  Tracks additions/removals in `%AppData%\Microsoft\Windows\Start Menu\Startup` and system-wide folder.

- **Registry Monitoring**:  
  - HKCU: `Software\Microsoft\Windows\CurrentVersion\Run`  
  - HKLM: `SOFTWARE\Microsoft\Windows\CurrentVersion\Run`  
  - Context Menu Handlers (Files/Folders/Background)

- **Services**:  
  Detects changes to service startup types via registry.

- **Scheduled Tasks**:  
  Monitors task additions/removals (basic implementation).

### Alert System
- **Multi-Channel Notifications**:  
  Choose between Windows Toasts, modal dialogs or both.

- **System Integration**:  
  - Alert sound via `winsound`  
  - Window flashing for background alerts  
  - Direct links to Regedit/Task Scheduler/Services  

- **Actionable Dialogs**:  
  One-click access to:  
  - Registry Editor  
  - Task Scheduler  
  - Services Console  
  - Autoruns.exe (auto-downloads if missing)

### UI Features
- **Dynamic Theme System**:  
  Smooth color transitions between dark/light modes.

- **Language Support**:  
  Switch between German/English on-the-fly.

- **Auto-Hide**:  
  Option to minimize to tray after 20s startup.

- **Persistent Settings**:  
  Saves configuration to `settings.json`.

## Requirements
- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.9+ (tested with 3.11)
- **Dependencies**:
  ```bash
  pip install pyqt6 win10toast pywin32 ctypes
  ```

## Installation
1. Clone repository:
   ```bash
   git clone https://github.com/Junko666/autostart-monitor.git
   cd autostart-monitor
   ```
2. Create virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
4. Start application:
   ```bash
   python main.py
   ```

## Usage
### Interface Overview
1. **Monitoring Methods**: Check which autostart locations to monitor
2. **Notification Channels**: Select alert types (Toasts/Dialogs)
3. **Settings**:  
   - Language: DE/EN  
   - Theme: Dark/Light  
   - Scan Interval: 10-300 seconds  
   - Auto-Hide: Minimize after launch

### Basic Workflow
1. Select monitoring methods (default: all enabled)
2. Choose notification preferences
3. Click "Start Monitoring"
4. On changes:  
   - Sound alert plays  
   - Window flashes (if minimized)  
   - Toast/Dialog shows details  
   - Buttons open relevant admin tools

### Context Actions
When a change dialog appears:
- **Registry Changes**: Opens Regedit at relevant path
- **Service Changes**: Launches Services Console
- **Tasks Changes**: Opens Task Scheduler
- **Autoruns**: Downloads/Runs Sysinternals Autoruns

## Configuration
Settings persist in `settings.json`:
```json
{
  "selected_methods": {
    "startup_folders": true,
    "registry": true,
    "registry_hklm_run": true,
    "context_handlers_star": true,
    "...": "..."
  },
  "notification_methods": {
    "windows_toast": true,
    "dialog": true
  },
  "auto_start": false,
  "language": "de",
  "dark_mode": false,
  "scan_interval": 60
}
```

### Key Settings
| Setting Group         | Options                          | Default  |
|-----------------------|----------------------------------|----------|
| Monitoring Methods    | 12 toggleable checkboxes         | All ON   |
| Notifications         | Toast/Dialog                     | Both ON  |
| Interface             | Language (DE/EN), Dark Mode      | DE, Light|
| Behavior              | Scan Interval (10-300s), Auto-Hide| 60s, OFF |

## Translations
### Supported Languages
- German (de) - Default
- English (en)

### Add New Language
1. Extend `update_language()` method in `AutostartMonitorWindow` class
2. Add translations for all UI elements
3. Create JSON file for system messages
4. Update language combo box

## Developer Notes
### Architecture Highlights
![image](https://github.com/user-attachments/assets/1c529b72-a07b-481a-85cc-7199f7bf2b41)

### Key Components
| File               | Responsibility                  |
|--------------------|---------------------------------|
| `main.py`          | Application entry point         |
| `AutostartMonitorWindow` | Main UI/PyQt6 logic      |
| `DEFAULT_SETTINGS` | Configuration defaults          |
| `compare_*` funcs  | Change detection algorithms     |

### Extension Ideas
1. **Tray Icon**:  
   Minimize to tray with monitoring status indicator.

2. **History Logging**:  
   Save change history to CSV/SQLite.

3. **Network Alerts**:  
   Send notifications via Email/Telegram API.

4. **Whitelisting**:  
   Allow users to exclude known-safe entries.

## License
MIT License - See [LICENSE](LICENSE) file.

## Contributors
1. [Junko](https://github.com/Junko666) - Development Director
2. OpenAI o3 Mini High - Code Development
3. DeepSeek-R1 - Documentation

---

**Disclaimer**: This tool interacts with critical system components. Use at your own risk. Always create system restore points before making changes.



# README.md - Autostart Monitor  
### Hellmodus (Englisch)  
![image](https://github.com/user-attachments/assets/46e57805-9cc4-4992-aedd-d755698b5721)

### Dunkelmodus (Deutsch)  
![image](https://github.com/user-attachments/assets/622daeaa-c577-4195-9401-2695e04dad70)

Ein Windows-Überwachungstool, das unbefugte Änderungen an Autostart-Orten erkennt. Überwacht kontinuierlich Startordner, Registrierungseinträge, Dienste und geplante Aufgaben. Benachrichtigt über Benachrichtigungen/Töne und bietet direkten Zugriff auf relevante Systemtools zur Analyse.

## Inhaltsverzeichnis
- [Einführung](#einführung)
- [Funktionen](#funktionen)
- [Voraussetzungen](#voraussetzungen)
- [Installation](#installation)
- [Verwendung](#verwendung)
- [Konfiguration](#konfiguration)
- [Übersetzungen](#übersetzungen)
- [Hinweise für Entwickler](#hinweise-für-entwickler)
- [Lizenz](#lizenz)
- [Mitwirkende](#mitwirkende)

## Einführung
Autostart Monitor ist ein sicherheitsorientiertes Tool, das mehr als 12 Windows-Autostart-Orte auf unbefugte Änderungen überwacht:
- Startordner (Benutzer/Alle Benutzer)
- Registrierungseinträge (HKCU/HKLM Run-Schlüssel)
- Kontextmenü-Handler (Dateien/Ordner/Hintergrund)
- Systemdienste (Änderungen des Starttyps)
- Geplante Aufgaben

Wichtige Funktionen:
- Echtzeit-Überwachung mit konfigurierbarem Intervall (10-300s)
- Visuelle/Ton-Benachrichtigungen mit aktionsfähigen Dialogen
- Dunkel/Hell-Modus mit flüssigen Animationen
- Deutsch/Englisch Sprachunterstützung
- Persistente Konfiguration

## Funktionen
### Kernüberwachung
- **Startordner**:  
  Verfolgt Hinzufügungen/Entfernungen in `%AppData%\Microsoft\Windows\Start Menu\Startup` und systemweiten Ordnern.

- **Registrierungsüberwachung**:  
  - HKCU: `Software\Microsoft\Windows\CurrentVersion\Run`  
  - HKLM: `SOFTWARE\Microsoft\Windows\CurrentVersion\Run`  
  - Kontextmenü-Handler (Dateien/Ordner/Hintergrund)

- **Dienste**:  
  Erkennt Änderungen an Dienststarttypen über die Registrierung.

- **Geplante Aufgaben**:  
  Überwacht das Hinzufügen/Entfernen von Aufgaben (grundlegende Implementierung).

### Benachrichtigungssystem
- **Multi-Kanal-Benachrichtigungen**:  
  Wählen Sie zwischen Windows-Toasts, modalen Dialogen oder beidem.

- **Systemintegration**:  
  - Benachrichtigungston über `winsound`  
  - Fensterblinken für Hintergrundbenachrichtigungen  
  - Direkte Links zu Regedit/Taskplaner/Dienste  

- **Aktionsfähige Dialoge**:  
  Ein-Klick-Zugriff auf:  
  - Registrierungseditor  
  - Taskplaner  
  - Dienstekonsole  
  - Autoruns.exe (wird automatisch heruntergeladen, falls fehlend)

### UI-Funktionen
- **Dynamisches Themesystem**:  
  Flüssige Farbübergänge zwischen Dunkel/Hell-Modi.

- **Sprachunterstützung**:  
  Wechseln Sie zwischen Deutsch/Englisch im laufenden Betrieb.

- **Automatisches Ausblenden**:  
  Option, nach 20s Start in das Systray zu minimieren.

- **Persistente Einstellungen**:  
  Speichert die Konfiguration in `settings.json`.

## Voraussetzungen
- **Betriebssystem**: Windows 10/11 (64-Bit)
- **Python**: 3.9+ (getestet mit 3.11)
- **Abhängigkeiten**:
  ```bash
  pip install pyqt6 win10toast pywin32 ctypes
  ```

## Installation
1. Repository klonen:
   ```bash
   git clone https://github.com/Junko666/autostart-monitor.git
   cd autostart-monitor
   ```
2. Virtuelle Umgebung erstellen:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. Anforderungen installieren:
   ```bash
   pip install -r requirements.txt
   ```
4. Anwendung starten:
   ```bash
   python main.py
   ```

## Verwendung
### Überblick über die Oberfläche
1. **Überwachungsmethoden**: Wählen Sie, welche Autostart-Orte überwacht werden sollen
2. **Benachrichtigungskanäle**: Wählen Sie Benachrichtigungstypen (Toasts/Dialoge)
3. **Einstellungen**:  
   - Sprache: DE/EN  
   - Thema: Dunkel/Hell  
   - Scan-Intervall: 10-300 Sekunden  
   - Automatisches Ausblenden: Nach dem Start minimieren

### Grundlegender Arbeitsablauf
1. Wählen Sie Überwachungsmethoden (Standard: alle aktiviert)
2. Wählen Sie Benachrichtigungseinstellungen
3. Klicken Sie auf "Überwachung starten"
4. Bei Änderungen:  
   - Benachrichtigungston wird abgespielt  
   - Fenster blinkt (wenn minimiert)  
   - Toast/Dialog zeigt Details an  
   - Schaltflächen öffnen relevante Admin-Tools

### Kontextaktionen
Wenn ein Änderungsdialog erscheint:
- **Registrierungsänderungen**: Öffnet Regedit am relevanten Pfad
- **Dienständerungen**: Startet die Dienstekonsole
- **Aufgabenänderungen**: Öffnet den Taskplaner
- **Autoruns**: Lädt/Startet Sysinternals Autoruns

## Konfiguration
Einstellungen werden in `settings.json` gespeichert:
```json
{
  "selected_methods": {
    "startup_folders": true,
    "registry": true,
    "registry_hklm_run": true,
    "context_handlers_star": true,
    "...": "..."
  },
  "notification_methods": {
    "windows_toast": true,
    "dialog": true
  },
  "auto_start": false,
  "language": "de",
  "dark_mode": false,
  "scan_interval": 60
}
```

### Wichtige Einstellungen
| Einstellungsgruppe    | Optionen                          | Standard  |
|-----------------------|----------------------------------|----------|
| Überwachungsmethoden  | 12 umschaltbare Kontrollkästchen | Alle AN  |
| Benachrichtigungen    | Toast/Dialog                     | Beide AN |
| Oberfläche            | Sprache (DE/EN), Dunkelmodus     | DE, Hell |
| Verhalten             | Scan-Intervall (10-300s), Automatisches Ausblenden| 60s, AUS |

## Übersetzungen
### Unterstützte Sprachen
- Deutsch (de) - Standard
- Englisch (en)

### Neue Sprache hinzufügen
1. Erweitern Sie die Methode `update_language()` in der Klasse `AutostartMonitorWindow`
2. Fügen Sie Übersetzungen für alle UI-Elemente hinzu
3. Erstellen Sie eine JSON-Datei für Systemnachrichten
4. Aktualisieren Sie das Sprachauswahlmenü

## Hinweise für Entwickler
### Architektur-Highlights
![image](https://github.com/user-attachments/assets/1c529b72-a07b-481a-85cc-7199f7bf2b41)

### Wichtige Komponenten
| Datei               | Verantwortung                  |
|--------------------|---------------------------------|
| `main.py`          | Anwendungseinstiegspunkt         |
| `AutostartMonitorWindow` | Haupt-UI/PyQt6-Logik      |
| `DEFAULT_SETTINGS` | Standardkonfiguration          |
| `compare_*` funcs  | Änderungserkennungsalgorithmen     |

### Erweiterungsideen
1. **Systray-Symbol**:  
   Minimieren in das Systray mit Überwachungsstatusanzeige.

2. **Verlaufsprotokollierung**:  
   Speichern des Änderungsverlaufs in CSV/SQLite.

3. **Netzwerkbenachrichtigungen**:  
   Senden von Benachrichtigungen über E-Mail/Telegramm-API.

4. **Whitelisting**:  
   Benutzern erlauben, bekannte sichere Einträge auszuschließen.

## Lizenz
MIT-Lizenz - Siehe [LICENSE](LICENSE)-Datei.

## Mitwirkende
1. [Junko](https://github.com/Junko666) - Entwicklungsleiter
2. OpenAI o3 Mini High - Code-Entwicklung
3. DeepSeek-R1 - Dokumentation

---

**Haftungsausschluss**: Dieses Tool interagiert mit kritischen Systemkomponenten. Verwenden Sie es auf eigenes Risiko. Erstellen Sie immer Systemwiederherstellungspunkte, bevor Sie Änderungen vornehmen.
