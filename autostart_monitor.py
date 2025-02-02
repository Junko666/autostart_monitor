import os
import sys
import json
import threading
import time
import ctypes
import winsound
import winreg
import logging
from win10toast import ToastNotifier
from PyQt6.QtCore import Qt, QTimer, pyqtProperty, QVariantAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QCheckBox, QPushButton, QComboBox, QSlider, QFormLayout, QMessageBox
)

# --- Logging konfigurieren ---
LOG_FILE = "monitor.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logging.info("Programmstart")

# --- Konstanten für die Einstellungen ---
SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "selected_methods": {
        "startup_folders": True,
        "registry": True,
        "services": True,
        "tasks": True
    },
    "notification_methods": {
        "windows_toast": True,
        "dialog": True
    },
    "auto_start": False,
    "language": "de",
    "dark_mode": False,
    "scan_interval": 60
}

def show_windows_toast(title: str, message: str, duration: int = 5):
    """Zeigt eine Windows-Toast-Benachrichtigung an."""
    try:
        toaster = ToastNotifier()
        toaster.show_toast(
            title,
            message,
            duration=duration,
            icon_path=None,
            threaded=True
        )
    except Exception as e:
        logging.error(f"Fehler bei Windows-Toast: {e}")

def show_dialog(title: str, message: str, parent=None):
    """Zeigt einen Dialog mit der Nachricht an und setzt einen Parent, damit er modal korrekt angezeigt wird."""
    try:
        msg = QMessageBox(parent)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()
    except Exception as e:
        logging.error(f"Fehler bei Dialog: {e}")

def play_alert_sound():
    try:
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
    except Exception as e:
        logging.error(f"Sound-Fehler: {e}")

def flash_window():
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        ctypes.windll.user32.FlashWindowEx(
            hwnd,
            0x00000008,
            0x00000008,
            0x00000060
        )
    except Exception as e:
        logging.error(f"Flash-Fehler: {e}")

# --- Monitoring-Funktionen ---
def check_startup_folders():
    user_dir = os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup")
    common_dir = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"
    try:
        user_files = set(os.listdir(user_dir))
    except Exception:
        user_files = set()
    try:
        common_files = set(os.listdir(common_dir))
    except Exception:
        common_files = set()
    return {'user': user_files, 'common': common_files}

def check_registry_autostart():
    key_path = r'Software\Microsoft\Windows\CurrentVersion\Run'
    entries = {}
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            i = 0
            while True:
                try:
                    name, value, typ = winreg.EnumValue(key, i)
                    entries[name] = value
                    i += 1
                except OSError:
                    break
    except Exception as e:
        logging.error(f"Registry-Fehler: {e}")
    return entries

def get_auto_services():
    return ["ServiceA", "ServiceB", "ServiceC"]

def check_scheduled_tasks():
    return ["TaskA", "TaskB"]

def compare_startup_folders(prev, current):
    messages = []
    prev_user = prev.get('user', set())
    curr_user = current.get('user', set())
    added = curr_user - prev_user
    removed = prev_user - curr_user
    if added:
        messages.append("Startup-Ordner (user) Hinzugefügt: " + ", ".join(added))
    if removed:
        messages.append("Startup-Ordner (user) Entfernt: " + ", ".join(removed))
    prev_common = prev.get('common', set())
    curr_common = current.get('common', set())
    added = curr_common - prev_common
    removed = prev_common - curr_common
    if added:
        messages.append("Startup-Ordner (common) Hinzugefügt: " + ", ".join(added))
    if removed:
        messages.append("Startup-Ordner (common) Entfernt: " + ", ".join(removed))
    return messages

def compare_registry(prev, current):
    messages = []
    prev_keys = set(prev.keys())
    curr_keys = set(current.keys())
    added = curr_keys - prev_keys
    removed = prev_keys - curr_keys
    if added:
        messages.append("Registry Hinzugefügt: " + ", ".join(added))
    if removed:
        messages.append("Registry Entfernt: " + ", ".join(removed))
    return messages

def compare_services(prev, current):
    messages = []
    prev_set = set(prev)
    curr_set = set(current)
    added = curr_set - prev_set
    removed = prev_set - curr_set
    if added:
        messages.append("Services Hinzugefügt: " + ", ".join(added))
    if removed:
        messages.append("Services Entfernt: " + ", ".join(removed))
    return messages

def compare_tasks(prev, current):
    messages = []
    prev_set = set(prev)
    curr_set = set(current)
    added = curr_set - prev_set
    removed = prev_set - curr_set
    if added:
        messages.append("Scheduled Tasks Hinzugefügt: " + ", ".join(added))
    if removed:
        messages.append("Scheduled Tasks Entfernt: " + ", ".join(removed))
    return messages

# --- GUI-Klasse für den Autostart Monitor ---
class AutostartMonitorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = DEFAULT_SETTINGS.copy()
        self.load_settings()
        self.setWindowTitle("Autostart Monitor")
        self.resize(600, 500)

        # Zentraler Container
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout(self.central)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # Überschrift
        header = QLabel("Autostart Monitor")
        header.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(header)

        # Methoden-Gruppierung
        self.grp_methods = QGroupBox("Zu überwachende Methoden:")
        self.grp_methods.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.methods_layout = QVBoxLayout()
        self.grp_methods.setLayout(self.methods_layout)
        self.chk_startup = QCheckBox("Startup-Ordner")
        self.chk_registry = QCheckBox("Registry-Einträge")
        self.chk_services = QCheckBox("Dienste")
        self.chk_tasks = QCheckBox("Geplante Tasks")
        self.methods_layout.addWidget(self.chk_startup)
        self.methods_layout.addWidget(self.chk_registry)
        self.methods_layout.addWidget(self.chk_services)
        self.methods_layout.addWidget(self.chk_tasks)
        self.main_layout.addWidget(self.grp_methods)

        # Benachrichtigungsgruppen
        self.grp_notifications = QGroupBox("Benachrichtigungswege:")
        self.grp_notifications.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.noti_layout = QVBoxLayout()
        self.grp_notifications.setLayout(self.noti_layout)
        self.chk_toast = QCheckBox("Windows Benachrichtigung")
        self.chk_dialog = QCheckBox("Dialog")
        self.noti_layout.addWidget(self.chk_toast)
        self.noti_layout.addWidget(self.chk_dialog)
        self.main_layout.addWidget(self.grp_notifications)

        # Einstellungen (Sprache, Dark Mode, Scanintervall)
        self.grp_settings = QGroupBox("Einstellungen:")
        self.grp_settings.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.settings_layout = QFormLayout()
        self.grp_settings.setLayout(self.settings_layout)

        self.cmb_language = QComboBox()
        self.cmb_language.addItems(["de", "en"])
        self.settings_layout.addRow("Sprache:", self.cmb_language)

        self.chk_dark_mode = QCheckBox("Dark Mode")
        self.settings_layout.addRow("Theme:", self.chk_dark_mode)

        self.sld_interval = QSlider(Qt.Orientation.Horizontal)
        self.sld_interval.setRange(10, 300)
        self.sld_interval.setTickInterval(10)
        self.lbl_interval = QLabel("60 Sek.")
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(self.sld_interval)
        interval_layout.addWidget(self.lbl_interval)
        self.settings_layout.addRow("Scanintervall:", interval_layout)
        self.main_layout.addWidget(self.grp_settings)

        # Auto-hide Option (ehemals: "Automatisch beim Anmelden starten")
        self.chk_autostart = QCheckBox("Automatisch beim Programmstart nach 20 Sekunden Verstecken")
        self.main_layout.addWidget(self.chk_autostart)

        # Steuerungsschaltfläche (Start/Stop)
        self.btn_toggle = QPushButton("Überwachung starten")
        self.btn_toggle.setFont(QFont("Segoe UI", 11))
        self.main_layout.addWidget(self.btn_toggle)

        # Variablen für die Überwachung
        self.monitoring_active = False
        self.monitor_thread = None
        self.stop_flag = threading.Event()

        # Timer für Änderungen im Slider
        self.sld_interval.valueChanged.connect(self.update_interval_label)

        # Animation für den Theme-Wechsel
        self.theme_animation = QVariantAnimation(
            self,
            startValue=QColor("#E0E0E0"),
            endValue=QColor("#2E2E2E"),
            duration=300,
            valueChanged=self.on_theme_animate,
            easingCurve=QEasingCurve.Type.InOutQuad
        )

        # Verbinde Widgets mit Aktionen und setze persistierte Werte
        self.setup_signals()
        self.apply_settings()
        self.apply_style()

    def setup_signals(self):
        self.btn_toggle.clicked.connect(self.toggle_monitoring)
        self.cmb_language.currentTextChanged.connect(self.update_language)
        self.chk_dark_mode.stateChanged.connect(self.toggle_theme)
        self.chk_autostart.stateChanged.connect(self.toggle_autostart)
        self.chk_startup.stateChanged.connect(self.save_settings)
        self.chk_registry.stateChanged.connect(self.save_settings)
        self.chk_services.stateChanged.connect(self.save_settings)
        self.chk_tasks.stateChanged.connect(self.save_settings)
        self.chk_toast.stateChanged.connect(self.save_settings)
        self.chk_dialog.stateChanged.connect(self.save_settings)
        self.cmb_language.currentTextChanged.connect(self.save_settings)
        self.sld_interval.valueChanged.connect(self.save_settings)
        self.chk_dark_mode.stateChanged.connect(self.save_settings)
        self.chk_autostart.stateChanged.connect(self.save_settings)

    def apply_settings(self):
        s = self.settings
        self.chk_startup.setChecked(s["selected_methods"].get("startup_folders", True))
        self.chk_registry.setChecked(s["selected_methods"].get("registry", True))
        self.chk_services.setChecked(s["selected_methods"].get("services", True))
        self.chk_tasks.setChecked(s["selected_methods"].get("tasks", True))
        self.chk_toast.setChecked(s["notification_methods"].get("windows_toast", True))
        self.chk_dialog.setChecked(s["notification_methods"].get("dialog", True))
        self.chk_autostart.setChecked(s.get("auto_start", False))
        self.cmb_language.setCurrentText(s.get("language", "de"))
        self.chk_dark_mode.setChecked(s.get("dark_mode", False))
        self.sld_interval.setValue(s.get("scan_interval", 60))
        self.lbl_interval.setText(f"{self.sld_interval.value()} Sek.")
        self.update_language()

    def apply_style(self):
        base_color = "#2E2E2E" if self.chk_dark_mode.isChecked() else "#E0E0E0"
        text_color = "#FFFFFF" if self.chk_dark_mode.isChecked() else "#000000"
        accent_color = "#5DADE2"
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {base_color};
                color: {text_color};
                font-family: "Segoe UI";
            }}
            QGroupBox {{
                border: 2px solid {accent_color};
                border-radius: 10px;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
            QSlider::groove:horizontal {{
                border: 1px solid #999;
                height: 8px;
                border-radius: 4px;
                background: {accent_color};
            }}
            QSlider::handle:horizontal {{
                background: {text_color};
                border: 1px solid {accent_color};
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
            QPushButton {{
                background-color: {accent_color};
                border: none;
                border-radius: 10px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: #3498DB;
            }}
        """)

    def on_theme_animate(self, value):
        color_name = value.name()
        self.central.setStyleSheet(f"background-color: {color_name};")

    def toggle_theme(self):
        if self.chk_dark_mode.isChecked():
            self.theme_animation.setStartValue(QColor("#E0E0E0"))
            self.theme_animation.setEndValue(QColor("#2E2E2E"))
        else:
            self.theme_animation.setStartValue(QColor("#2E2E2E"))
            self.theme_animation.setEndValue(QColor("#E0E0E0"))
        self.theme_animation.start()
        self.apply_style()

    def update_language(self):
        lang = self.cmb_language.currentText()
        if lang == "de":
            self.grp_methods.setTitle("Zu überwachende Methoden:")
            self.chk_startup.setText("Startup-Ordner")
            self.chk_registry.setText("Registry-Einträge")
            self.chk_services.setText("Dienste")
            self.chk_tasks.setText("Geplante Tasks")
            self.grp_notifications.setTitle("Benachrichtigungswege:")
            self.chk_toast.setText("Windows Benachrichtigung")
            self.chk_dialog.setText("Dialog")
            # Checkbox-Text anpassen (Alt: "Automatisch beim Anmelden starten")
            self.chk_autostart.setText("Automatisch beim Programmstart nach 20 Sekunden Verstecken")
            self.btn_toggle.setText("Überwachung starten" if not self.monitoring_active else "Überwachung stoppen")
        else:
            self.grp_methods.setTitle("Methods to monitor:")
            self.chk_startup.setText("Startup folders")
            self.chk_registry.setText("Registry entries")
            self.chk_services.setText("Services")
            self.chk_tasks.setText("Scheduled tasks")
            self.grp_notifications.setTitle("Notification methods:")
            self.chk_toast.setText("Windows notification")
            self.chk_dialog.setText("Dialog")
            self.chk_autostart.setText("Automatically hide GUI 20 seconds after program start")
            self.btn_toggle.setText("Start monitoring" if not self.monitoring_active else "Stop monitoring")

    def update_interval_label(self, value):
        self.lbl_interval.setText(f"{value} Sek.")

    def toggle_autostart(self):
        # Die frühere Registrierung im Autostart wird nicht mehr verwendet.
        logging.info("Auto-Hide beim Programmstart: " + ("aktiviert" if self.chk_autostart.isChecked() else "deaktiviert"))

    def toggle_monitoring(self):
        if not self.monitoring_active:
            self.monitoring_active = True
            self.stop_flag.clear()
            self.btn_toggle.setText("Überwachung stoppen" if self.cmb_language.currentText() == "de" else "Stop monitoring")
            logging.info("Monitoring gestartet")
            self.monitor_thread = threading.Thread(target=self.run_monitoring, daemon=True)
            self.monitor_thread.start()
        else:
            self.monitoring_active = False
            self.stop_flag.set()
            self.btn_toggle.setText("Überwachung starten" if self.cmb_language.currentText() == "de" else "Start monitoring")
            logging.info("Monitoring gestoppt")

    def run_monitoring(self):
        lang = self.cmb_language.currentText()
        methods = {
            'startup_folders': self.chk_startup.isChecked(),
            'registry': self.chk_registry.isChecked(),
            'services': self.chk_services.isChecked(),
            'tasks': self.chk_tasks.isChecked()
        }
        notifications = {
            'windows_toast': self.chk_toast.isChecked(),
            'dialog': self.chk_dialog.isChecked()
        }
        previous_state = {}
        if methods['startup_folders']:
            previous_state['startup_folders'] = check_startup_folders()
        if methods['registry']:
            previous_state['registry'] = check_registry_autostart()
        if methods['services']:
            previous_state['services'] = get_auto_services()
        if methods['tasks']:
            previous_state['tasks'] = check_scheduled_tasks()

        while self.monitoring_active and not self.stop_flag.is_set():
            try:
                time.sleep(self.sld_interval.value())
                current_state = {}
                if methods['startup_folders']:
                    current_state['startup_folders'] = check_startup_folders()
                if methods['registry']:
                    current_state['registry'] = check_registry_autostart()
                if methods['services']:
                    current_state['services'] = get_auto_services()
                if methods['tasks']:
                    current_state['tasks'] = check_scheduled_tasks()

                messages = []
                if methods['startup_folders']:
                    messages.extend(compare_startup_folders(
                        previous_state.get('startup_folders', {}),
                        current_state.get('startup_folders', {})
                    ))
                if methods['registry']:
                    messages.extend(compare_registry(
                        previous_state.get('registry', {}),
                        current_state.get('registry', {})
                    ))
                if methods['services']:
                    messages.extend(compare_services(
                        previous_state.get('services', []),
                        current_state.get('services', [])
                    ))
                if methods['tasks']:
                    messages.extend(compare_tasks(
                        previous_state.get('tasks', []),
                        current_state.get('tasks', [])
                    ))

                if messages:
                    msg_text = "\n".join(messages)
                    logging.info("Änderungen gefunden:\n" + msg_text)
                    print("Änderungen gefunden:", msg_text)
                    play_alert_sound()
                    flash_window()

                    if notifications['windows_toast']:
                        show_windows_toast("Autostart Änderung", msg_text)
                    if notifications['dialog']:
                        self.show_dialog_threadsafe("Autostart Änderung", msg_text)

                previous_state = current_state
            except Exception as e:
                logging.error(f"Fehler im Monitoring: {e}")
                break

        self.monitoring_active = False
        logging.info("Monitoring Thread beendet")

    def show_dialog_threadsafe(self, title: str, message: str):
        """Zeigt einen Dialog threadsicher an."""
        try:
            self.dialog_title = title
            self.dialog_message = message
            QTimer.singleShot(0, self.display_dialog)
        except Exception as e:
            logging.error(f"Fehler beim threadsicheren Dialog: {e}")

    def display_dialog(self):
        try:
            show_dialog(self.dialog_title, self.dialog_message, parent=self)
        except Exception as e:
            logging.error(f"Fehler beim Anzeigen des Dialogs: {e}")

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf8") as f:
                    self.settings = json.load(f)
                logging.info("Einstellungen erfolgreich geladen")
            except Exception as e:
                logging.error(f"Fehler beim Laden der Einstellungen: {e}")
                self.settings = DEFAULT_SETTINGS.copy()
        else:
            self.settings = DEFAULT_SETTINGS.copy()
            logging.info("Standard-Einstellungen verwendet")

    def save_settings(self):
        current_settings = {
            "selected_methods": {
                "startup_folders": self.chk_startup.isChecked(),
                "registry": self.chk_registry.isChecked(),
                "services": self.chk_services.isChecked(),
                "tasks": self.chk_tasks.isChecked()
            },
            "notification_methods": {
                "windows_toast": self.chk_toast.isChecked(),
                "dialog": self.chk_dialog.isChecked()
            },
            "auto_start": self.chk_autostart.isChecked(),
            "language": self.cmb_language.currentText(),
            "dark_mode": self.chk_dark_mode.isChecked(),
            "scan_interval": self.sld_interval.value()
        }
        self.settings = current_settings
        try:
            with open(SETTINGS_FILE, "w", encoding="utf8") as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            logging.info(f"Einstellungen gespeichert: {json.dumps(self.settings, indent=4)}")
        except Exception as e:
            logging.error(f"Konnte Einstellungen nicht speichern: {e}")

def close_other_instance():
    """Schließt eine andere laufende Instanz basierend auf dem Fenstertitel."""
    try:
        hwnd = ctypes.windll.user32.FindWindowW(None, "Autostart Monitor")
        if hwnd:
            WM_CLOSE = 0x0010
            ctypes.windll.user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
            time.sleep(1)  # Warte kurz, bis die andere Instanz geschlossen wird
            logging.info("Vorherige Instanz geschlossen")
    except Exception as e:
        logging.error(f"Fehler beim Schließen der anderen Instanz: {e}")

def main():
    # Prüfen, ob bereits eine Instanz läuft und ggf. schließen
    close_other_instance()

    app = QApplication(sys.argv)
    window = AutostartMonitorWindow()
    window.show()

    # Starte die Überwachung automatisch (sofort nachdem die GUI erstellt wurde)
    QTimer.singleShot(0, window.toggle_monitoring)

    # Wenn die Checkbox für Auto-Hide aktiviert ist, verstecke die GUI nach 20 Sekunden.
    if window.chk_autostart.isChecked():
        QTimer.singleShot(20000, window.hide)

    app_result = app.exec()
    logging.info("Programm beendet")
    sys.exit(app_result)

if __name__ == "__main__":
    main()
