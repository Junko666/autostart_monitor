import os
import sys
import json
import threading
import time
import ctypes
import winsound
import winreg
import logging
import subprocess
from junk_logger import log_event
from win10toast import ToastNotifier
from PyQt6.QtCore import Qt, QTimer, QVariantAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QCheckBox, QPushButton, QComboBox, QSlider, QFormLayout, QMessageBox, QDialog
)

LOG_FILE = "monitor.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logging.info("Programmstart")

DEFAULT_SETTINGS = {
    "selected_methods": {
        "startup_folders": True,
        "registry": True,
        "registry_hklm_run": True,
        "context_handlers_star": True,
        "context_handlers_allfilesystem": True,
        "context_handlers_directory": True,
        "context_handlers_directory_bg": True,
        "folder_context_handlers": True,
        "directory_dragdrop_handlers": True,
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

def log(msg, level="INFO"):
    print(f"{level}: {msg}")
    log_event(msg, level=level, program_name=__file__)

def show_windows_toast(title: str, message: str, duration: int = 5):
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

def check_startup_folders():
    user_dir = os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Startup")
    common_dir = r"C:\ProgramData\Microsoft\Windows\Start Menu\Startup"
    try:
        user_files = set(os.listdir(user_dir))
    except Exception as e:
        logging.error(f"Fehler beim Lesen des Benutzer-Startup-Ordners: {e}")
        user_files = set()
    try:
        common_files = set(os.listdir(common_dir))
    except Exception as e:
        logging.error(f"Fehler beim Lesen des Common-Startup-Ordners: {e}")
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
                    name, value, _ = winreg.EnumValue(key, i)
                    entries[name] = value
                    i += 1
                except OSError:
                    break
    except Exception as e:
        logging.error(f"Registry-Fehler (HKCU): {e}")
    return entries

def check_registry_autostart_hklm():
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
    entries = {}
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    entries[name] = value
                    i += 1
                except OSError:
                    break
    except Exception as e:
        logging.error(f"Registry HKLM Run Fehler: {e}")
    return entries

def check_context_menu_handler(reg_path):
    handlers = {}
    try:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        try:
                            with winreg.OpenKey(key, subkey_name) as sub_key:
                                default_value, _ = winreg.QueryValueEx(sub_key, None)
                                handlers[subkey_name] = default_value or ""
                        except Exception as e:
                            handlers[subkey_name] = ""
                            logging.error(f"Fehler beim Lesen des Handlers {subkey_name}: {e}")
                        i += 1
                    except OSError:
                        break
        except Exception as e:
            logging.error(f"Fehler beim Lesen des Schlüssels {reg_path}: {e}")
        return handlers
    except Exception as e:
        logging.error(f"Unbekannter Fehler in check_context_menu_handler: {e}")
        return {}

def check_system_services():
    services = {}
    try:
        result = subprocess.check_output(["powershell.exe", "-Command", "Get-Service"])
        services_list = result.decode('utf-8').split('\n')
        for line in services_list:
            if 'Running' in line or 'Stopped' in line:
                parts = line.split()
                service_name = parts[0].strip()
                status = parts[-1].strip()
                services[service_name] = status
        return services
    except Exception as e:
        logging.error(f"Fehler beim Lesen der Dienste via PowerShell: {e}")
        return {}

def get_services_with_powershell():
    services = {}
    try:
        result = subprocess.check_output(["powershell.exe", "-Command", "Get-Service"])
        services_list = result.decode('utf-8').split('\n')
        for line in services_list:
            if 'Running' in line or 'Stopped' in line:
                parts = line.split()
                service_name = parts[0].strip()
                status = parts[-1].strip()
                services[service_name] = status
        return services
    except Exception as e:
        logging.error(f"Fehler beim Lesen der Dienste via PowerShell: {e}")
        return {}

def check_services_start_values():
    services = {}
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services") as key:
            i = 0
            while True:
                try:
                    service_name = winreg.EnumKey(key, i)
                    try:
                        with winreg.OpenKey(key, service_name) as service_key:
                            start_value, _ = winreg.QueryValueEx(service_key, "Start")
                            services[service_name] = start_value
                    except OSError:
                        logging.error(f"Fehler beim Lesen des Dienstes {service_name}")
                        services[service_name] = None
                    i += 1
                except OSError:
                    break
        return services
    except Exception as e:
        logging.error(f"Fehler beim Lesen der Dienste: {e}")
        return {}

def compare_services(prev, current):
    messages = []
    prev_services = prev or {}
    curr_services = current or {}

    for service in prev_services:
        if service in curr_services:
            if prev_services[service] != curr_services[service]:
                messages.append(f"Dienst '{service}' Startwert geändert: von {prev_services[service]} nach {curr_services[service]}")
    for service in curr_services:
        if service not in prev_services:
            messages.append(f"Dienst '{service}' hinzugefügt mit Startwert {curr_services[service]}")
    for service in prev_services:
        if service not in curr_services:
            messages.append(f"Dienst '{service}' entfernt")
    return messages

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

def compare_registry_entries(prev, curr):
    messages = []
    prev_keys = set(prev.keys())
    curr_keys = set(curr.keys())
    common_keys = prev_keys.intersection(curr_keys)
    for key in common_keys:
        try:
            if str(prev[key]) != str(curr[key]):
                messages.append(f"Registry {key} geändert: von {prev[key]} zu {curr[key]}")
        except Exception as e:
            logging.error(f"Fehler beim Vergleich von Registry Eintrag {key}: {e}")
    for key in curr_keys - prev_keys:
        messages.append(f"Registry {key} hinzugefügt: {curr[key]}")
    for key in prev_keys - curr_keys:
        messages.append(f"Registry {key} entfernt: {prev[key]}")
    return messages

def compare_tasks(prev, current):
    messages = []
    prev_set = set(prev)
    curr_set = set(current)
    added = curr_set - prev_set
    removed = prev_set - curr_set
    if added:
        messages.append("Geplante Tasks Hinzugefügt: " + ", ".join(added))
    if removed:
        messages.append("Geplante Tasks Entfernt: " + ", ".join(removed))
    return messages

class CustomDialog(QDialog):
    def __init__(self, title: str, message: str, change_type: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.message = message
        self.change_type = change_type

        layout = QVBoxLayout()
        self.setLayout(layout)

        text_label = QLabel(message)
        text_label.setWordWrap(True)
        layout.addWidget(text_label)

        button_box = QHBoxLayout()

        if change_type == "registry":
            reg_button = QPushButton("Regedit öffnen")
            reg_button.clicked.connect(lambda: os.startfile("regedit.exe"))
            button_box.addWidget(reg_button)

        if change_type == "tasks":
            tasks_button = QPushButton("Taskplanung öffnen")
            tasks_button.clicked.connect(lambda: os.startfile("taskschd.msc"))
            button_box.addWidget(tasks_button)

        if change_type == "services":
            services_button = QPushButton("Dienste öffnen")
            services_button.clicked.connect(lambda: os.startfile("services.msc"))
            button_box.addWidget(services_button)

        autoruns_button = QPushButton("Autoruns.exe starten")
        autoruns_button.clicked.connect(self.start_autoruns)
        button_box.addWidget(autoruns_button)

        cancel_button = QPushButton("Abbrechen")
        cancel_button.clicked.connect(self.reject)
        button_box.addWidget(cancel_button)

        layout.addLayout(button_box)

    def start_autoruns(self):
        try:
            if not os.path.exists("autoruns.exe"):
                url = "https://live.sysinternals.com/autoruns.exe"
                response = subprocess.check_output([
                    "powershell.exe",
                    "-Command",
                    f"Invoke-WebRequest -Uri '{url}' -OutFile 'autoruns.exe'"
                ])
            subprocess.Popen(["autoruns.exe"])
        except Exception as e:
            logging.error(f"Fehler beim Starten von Autoruns.exe: {e}")

class AutostartMonitorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = DEFAULT_SETTINGS.copy()
        self.load_settings()
        self.setWindowTitle("Autostart Monitor")
        self.resize(600, 500)

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout(self.central)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        header = QLabel("Autostart Monitor")
        header.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(header)

        self.grp_methods = QGroupBox("Zu überwachende Methoden:")
        self.grp_methods.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.methods_layout = QVBoxLayout()
        self.grp_methods.setLayout(self.methods_layout)
        self.chk_startup = QCheckBox("Startup-Ordner")
        self.chk_registry = QCheckBox("Registry-Einträge (HKCU)")
        self.chk_reg_hklm_run = QCheckBox("Registry (HKLM Run)")
        self.chk_ctx_star = QCheckBox("Kontextmenü Handler (* ShellEx)")
        self.chk_ctx_allfilesystem = QCheckBox("Kontextmenü Handler (AllFilesystemObjects)")
        self.chk_ctx_directory = QCheckBox("Kontextmenü Handler (Directory)")
        self.chk_ctx_directory_bg = QCheckBox("Kontextmenü Handler (Directory Hintergrund)")
        self.chk_folder_ctx = QCheckBox("Kontextmenü Handler (Folder)")
        self.chk_directory_dragdrop = QCheckBox("Kontextmenü Handler (Directory)")
        self.chk_services = QCheckBox("Dienste")
        self.chk_tasks = QCheckBox("Geplante Tasks")
        self.methods_layout.addWidget(self.chk_startup)
        self.methods_layout.addWidget(self.chk_registry)
        self.methods_layout.addWidget(self.chk_reg_hklm_run)
        self.methods_layout.addWidget(self.chk_ctx_star)
        self.methods_layout.addWidget(self.chk_ctx_allfilesystem)
        self.methods_layout.addWidget(self.chk_ctx_directory)
        self.methods_layout.addWidget(self.chk_ctx_directory_bg)
        self.methods_layout.addWidget(self.chk_folder_ctx)
        self.methods_layout.addWidget(self.chk_directory_dragdrop)
        self.methods_layout.addWidget(self.chk_services)
        self.methods_layout.addWidget(self.chk_tasks)
        self.main_layout.addWidget(self.grp_methods)

        self.grp_notifications = QGroupBox("Benachrichtigungswege:")
        self.grp_notifications.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.noti_layout = QVBoxLayout()
        self.grp_notifications.setLayout(self.noti_layout)
        self.chk_toast = QCheckBox("Windows-Benachrichtigung")
        self.chk_dialog = QCheckBox("Dialog")
        self.noti_layout.addWidget(self.chk_toast)
        self.noti_layout.addWidget(self.chk_dialog)
        self.main_layout.addWidget(self.grp_notifications)

        self.grp_settings = QGroupBox("Einstellungen:")
        self.grp_settings.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.settings_layout = QFormLayout()
        self.grp_settings.setLayout(self.settings_layout)

        self.cmb_language = QComboBox()
        self.cmb_language.addItems(["de", "en"])
        self.settings_layout.addRow("Sprache:", self.cmb_language)

        self.chk_dark_mode = QCheckBox("Dark Mode")
        self.settings_layout.addRow("Dark Mode:", self.chk_dark_mode)

        self.sld_interval = QSlider(Qt.Orientation.Horizontal)
        self.sld_interval.setRange(10, 300)
        self.sld_interval.setTickInterval(10)
        self.lbl_interval = QLabel("60 Sek.")
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(self.sld_interval)
        interval_layout.addWidget(self.lbl_interval)
        self.settings_layout.addRow("Scanintervall:", interval_layout)
        self.main_layout.addWidget(self.grp_settings)

        self.chk_autostart = QCheckBox("Automatisch beim Programmstart nach 20 Sekunden verstecken")
        self.main_layout.addWidget(self.chk_autostart)

        self.btn_toggle = QPushButton("Überwachung starten")
        self.btn_toggle.setFont(QFont("Segoe UI", 11))
        self.main_layout.addWidget(self.btn_toggle)

        self.monitoring_active = False
        self.monitor_thread = None
        self.stop_flag = threading.Event()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_interval_label)
        self.sld_interval.valueChanged.connect(self.update_interval_label)

        self.theme_animation = QVariantAnimation(
            self,
            startValue=QColor("#E0E0E0"),
            endValue=QColor("#2E2E2E"),
            duration=300,
            valueChanged=self.on_theme_animate,
            easingCurve=QEasingCurve.Type.InOutQuad
        )

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
        self.chk_reg_hklm_run.stateChanged.connect(self.save_settings)
        self.chk_ctx_star.stateChanged.connect(self.save_settings)
        self.chk_ctx_allfilesystem.stateChanged.connect(self.save_settings)
        self.chk_ctx_directory.stateChanged.connect(self.save_settings)
        self.chk_ctx_directory_bg.stateChanged.connect(self.save_settings)
        self.chk_folder_ctx.stateChanged.connect(self.save_settings)
        self.chk_directory_dragdrop.stateChanged.connect(self.save_settings)
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
        self.chk_reg_hklm_run.setChecked(s["selected_methods"].get("registry_hklm_run", True))
        self.chk_ctx_star.setChecked(s["selected_methods"].get("context_handlers_star", True))
        self.chk_ctx_allfilesystem.setChecked(s["selected_methods"].get("context_handlers_allfilesystem", True))
        self.chk_ctx_directory.setChecked(s["selected_methods"].get("context_handlers_directory", True))
        self.chk_ctx_directory_bg.setChecked(s["selected_methods"].get("context_handlers_directory_bg", True))
        self.chk_folder_ctx.setChecked(s["selected_methods"].get("folder_context_handlers", True))
        self.chk_directory_dragdrop.setChecked(s["selected_methods"].get("directory_dragdrop_handlers", True))
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
        self.central.setStyleSheet(f"background-color: {value.name()};")
        
    def toggle_theme(self):
        # Angepasst: Setzt explizit Start- und Endfarbe, je nachdem ob Dark Mode aktiviert ist
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
            self.chk_registry.setText("Registry-Einträge (HKCU)")
            self.chk_reg_hklm_run.setText("Registry (HKLM Run)")
            self.chk_ctx_star.setText("Kontextmenü Handler (* ShellEx)")
            self.chk_ctx_allfilesystem.setText("Kontextmenü Handler (AllFilesystemObjects)")
            self.chk_ctx_directory.setText("Kontextmenü Handler (Directory)")
            self.chk_ctx_directory_bg.setText("Kontextmenü Handler (Directory Hintergrund)")
            self.chk_folder_ctx.setText("Kontextmenü Handler (Folder)")
            self.chk_directory_dragdrop.setText("Kontextmenü Handler (Directory)")
            self.chk_services.setText("Dienste")
            self.chk_tasks.setText("Geplante Tasks")
            self.grp_notifications.setTitle("Benachrichtigungswege:")
            self.chk_toast.setText("Windows-Benachrichtigung")
            self.chk_dialog.setText("Dialog")
            self.chk_autostart.setText("Automatisch beim Programmstart nach 20 Sekunden verstecken")
            self.btn_toggle.setText("Überwachung starten" if not self.monitoring_active else "Überwachung stoppen")
        else:
            self.grp_methods.setTitle("Methods to Monitor:")
            self.chk_startup.setText("Startup folders")
            self.chk_registry.setText("Registry entries (HKCU)")
            self.chk_reg_hklm_run.setText("Registry (HKLM Run)")
            self.chk_ctx_star.setText("Context menu handlers (* ShellEx)")
            self.chk_ctx_allfilesystem.setText("Context menu handlers (AllFilesystemObjects)")
            self.chk_ctx_directory.setText("Context menu handlers (Directory)")
            self.chk_ctx_directory_bg.setText("Context menu handlers (Directory Background)")
            self.chk_folder_ctx.setText("Context menu handlers (Folder)")
            self.chk_directory_dragdrop.setText("Context menu handlers (Directory)")
            self.chk_services.setText("Services")
            self.chk_tasks.setText("Scheduled tasks")
            self.grp_notifications.setTitle("Notification methods:")
            self.chk_toast.setText("Windows notification")
            self.chk_dialog.setText("Dialog")
            self.chk_autostart.setText("Automatically hide GUI 20 seconds after program start")
            self.btn_toggle.setText("Start monitoring" if not self.monitoring_active else "Stop monitoring")

    def update_interval_label(self, value=None):
        if value is None:
            value = self.sld_interval.value()
        self.lbl_interval.setText(f"{value} Sek.")

    def toggle_autostart(self):
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
        methods = {
            "startup_folders": self.chk_startup.isChecked(),
            "registry": self.chk_registry.isChecked(),
            "registry_hklm_run": self.chk_reg_hklm_run.isChecked(),
            "context_handlers_star": self.chk_ctx_star.isChecked(),
            "context_handlers_allfilesystem": self.chk_ctx_allfilesystem.isChecked(),
            "context_handlers_directory": self.chk_ctx_directory.isChecked(),
            "context_handlers_directory_bg": self.chk_ctx_directory_bg.isChecked(),
            "folder_context_handlers": self.chk_folder_ctx.isChecked(),
            "directory_dragdrop_handlers": self.chk_directory_dragdrop.isChecked(),
            "services": self.chk_services.isChecked(),
            "tasks": self.chk_tasks.isChecked()
        }
        previous_state = {}
        try:
            if methods["startup_folders"]:
                previous_state["startup_folders"] = check_startup_folders()
            if methods["registry"]:
                previous_state["registry"] = check_registry_autostart()
            if methods["registry_hklm_run"]:
                previous_state["registry_hklm_run"] = check_registry_autostart_hklm()
            if methods["context_handlers_star"]:
                previous_state["context_handlers_star"] = check_context_menu_handler(r"SOFTWARE\Classes\*\ShellEx\ContextMenuHandlers")
            if methods["context_handlers_allfilesystem"]:
                previous_state["context_handlers_allfilesystem"] = check_context_menu_handler(r"SOFTWARE\Classes\AllFilesystemObjects\shellex\ContextMenuHandlers")
            if methods["context_handlers_directory"]:
                previous_state["context_handlers_directory"] = check_context_menu_handler(r"SOFTWARE\Classes\Directory\shellex\ContextMenuHandlers")
            if methods["context_handlers_directory_bg"]:
                previous_state["context_handlers_directory_bg"] = check_context_menu_handler(r"SOFTWARE\Classes\Directory\background\shellex\ContextMenuHandlers")
            if methods["folder_context_handlers"]:
                previous_state["folder_context_handlers"] = check_context_menu_handler(r"SOFTWARE\Classes\Folder\ShellEx\ContextMenuHandlers")
            if methods["directory_dragdrop_handlers"]:
                previous_state["directory_dragdrop_handlers"] = check_context_menu_handler(r"SOFTWARE\Classes\Directory\shellex\DragDropHandlers")
            if methods["services"]:
                previous_state["services"] = check_services_start_values()
            if methods["tasks"]:
                previous_state["tasks"] = check_scheduled_tasks()
        except Exception as e:
            logging.error(f"Fehler beim Initialisieren des Zustands: {e}")

        while self.monitoring_active and not self.stop_flag.is_set():
            try:
                time.sleep(self.sld_interval.value())
                current_state = {}
                if methods["startup_folders"]:
                    current_state["startup_folders"] = check_startup_folders()
                if methods["registry"]:
                    current_state["registry"] = check_registry_autostart()
                if methods["registry_hklm_run"]:
                    current_state["registry_hklm_run"] = check_registry_autostart_hklm()
                if methods["context_handlers_star"]:
                    current_state["context_handlers_star"] = check_context_menu_handler(r"SOFTWARE\Classes\*\ShellEx\ContextMenuHandlers")
                if methods["context_handlers_allfilesystem"]:
                    current_state["context_handlers_allfilesystem"] = check_context_menu_handler(r"SOFTWARE\Classes\AllFilesystemObjects\shellex\ContextMenuHandlers")
                if methods["context_handlers_directory"]:
                    current_state["context_handlers_directory"] = check_context_menu_handler(r"SOFTWARE\Classes\Directory\shellex\ContextMenuHandlers")
                if methods["context_handlers_directory_bg"]:
                    current_state["context_handlers_directory_bg"] = check_context_menu_handler(r"SOFTWARE\Classes\Directory\background\shellex\ContextMenuHandlers")
                if methods["folder_context_handlers"]:
                    current_state["folder_context_handlers"] = check_context_menu_handler(r"SOFTWARE\Classes\Folder\ShellEx\ContextMenuHandlers")
                if methods["directory_dragdrop_handlers"]:
                    current_state["directory_dragdrop_handlers"] = check_context_menu_handler(r"SOFTWARE\Classes\Directory\shellex\DragDropHandlers")
                if methods["services"]:
                    current_state["services"] = check_services_start_values()
                if methods["tasks"]:
                    current_state["tasks"] = check_scheduled_tasks()

                messages = []
                if methods["startup_folders"]:
                    messages.extend(compare_startup_folders(
                        previous_state.get("startup_folders", {}),
                        current_state.get("startup_folders", {})
                    ))
                if methods["registry"]:
                    messages.extend(compare_registry_entries(
                        previous_state.get("registry", {}),
                        current_state.get("registry", {})
                    ))
                if methods["registry_hklm_run"]:
                    messages.extend(compare_registry_entries(
                        previous_state.get("registry_hklm_run", {}),
                        current_state.get("registry_hklm_run", {})
                    ))
                if methods["context_handlers_star"]:
                    messages.extend(compare_registry_entries(
                        previous_state.get("context_handlers_star", {}),
                        current_state.get("context_handlers_star", {})
                    ))
                if methods["context_handlers_allfilesystem"]:
                    messages.extend(compare_registry_entries(
                        previous_state.get("context_handlers_allfilesystem", {}),
                        current_state.get("context_handlers_allfilesystem", {})
                    ))
                if methods["context_handlers_directory"]:
                    messages.extend(compare_registry_entries(
                        previous_state.get("context_handlers_directory", {}),
                        current_state.get("context_handlers_directory", {})
                    ))
                if methods["context_handlers_directory_bg"]:
                    messages.extend(compare_registry_entries(
                        previous_state.get("context_handlers_directory_bg", {}),
                        current_state.get("context_handlers_directory_bg", {})
                    ))
                if methods["folder_context_handlers"]:
                    messages.extend(compare_registry_entries(
                        previous_state.get("folder_context_handlers", {}),
                        current_state.get("folder_context_handlers", {})
                    ))
                if methods["directory_dragdrop_handlers"]:
                    messages.extend(compare_registry_entries(
                        previous_state.get("directory_dragdrop_handlers", {}),
                        current_state.get("directory_dragdrop_handlers", {})
                    ))
                if methods["services"]:
                    messages.extend(compare_services(
                        previous_state.get("services", {}),
                        current_state.get("services", {})
                    ))
                if methods["tasks"]:
                    messages.extend(compare_tasks(
                        previous_state.get("tasks", []),
                        current_state.get("tasks", [])
                    ))

                if messages:
                    msg_text = "\n".join(messages)
                    logging.info("Änderungen gefunden:\n" + msg_text)
                    print("Änderungen gefunden:", msg_text)
                    play_alert_sound()
                    flash_window()
                    log(f"Autostart Änderung: {msg_text}", "INFO")
                    if self.chk_toast.isChecked():
                        show_windows_toast("Autostart Änderung", msg_text)
                    if self.chk_dialog.isChecked():
                        self.show_dialog_threadsafe("Autostart Änderung", msg_text, self.get_change_type(msg_text))

                previous_state = current_state
            except KeyboardInterrupt:
                logging.info("Monitoring durch KeyboardInterrupt beendet.")
                break
            except Exception as e:
                logging.error(f"Fehler im Monitoring: {e}")
                continue

        self.monitoring_active = False
        logging.info("Monitoring Thread beendet")

    def get_change_type(self, message):
        if "Registry" in message:
            return "registry"
        elif "Tasks" in message:
            return "tasks"
        elif "Dienst" in message or "Service" in message:
            return "services"
        else:
            return "unknown"

    def show_dialog_threadsafe(self, title: str, message: str, change_type: str):
        try:
            self.dialog_title = title
            self.dialog_message = message
            self.change_type = change_type
            QTimer.singleShot(0, self.display_dialog)
        except Exception as e:
            logging.error(f"Fehler beim threadsicheren Dialog: {e}")

    def display_dialog(self):
        try:
            dialog = CustomDialog(
                self.dialog_title,
                self.dialog_message,
                self.change_type,
                parent=self
            )
            dialog.exec()
        except Exception as e:
            logging.error(f"Fehler beim Anzeigen des Dialogs: {e}")

    def load_settings(self):
        if os.path.exists("settings.json"):
            try:
                with open("settings.json", "r", encoding="utf8") as f:
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
                "registry_hklm_run": self.chk_reg_hklm_run.isChecked(),
                "context_handlers_star": self.chk_ctx_star.isChecked(),
                "context_handlers_allfilesystem": self.chk_ctx_allfilesystem.isChecked(),
                "context_handlers_directory": self.chk_ctx_directory.isChecked(),
                "context_handlers_directory_bg": self.chk_ctx_directory_bg.isChecked(),
                "folder_context_handlers": self.chk_folder_ctx.isChecked(),
                "directory_dragdrop_handlers": self.chk_directory_dragdrop.isChecked(),
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
            with open("settings.json", "w", encoding="utf8") as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            logging.info(f"Einstellungen gespeichert: {json.dumps(self.settings, indent=4)}")
        except Exception as e:
            logging.error(f"Konnte Einstellungen nicht speichern: {e}")

def close_other_instance():
    try:
        hwnd = ctypes.windll.user32.FindWindowW(None, "Autostart Monitor")
        if hwnd:
            WM_CLOSE = 0x0010
            ctypes.windll.user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
            time.sleep(1)
            logging.info("Vorherige Instanz geschlossen")
    except Exception as e:
        logging.error(f"Fehler beim Schließen der anderen Instanz: {e}")

def main():
    close_other_instance()
    app = QApplication(sys.argv)
    window = AutostartMonitorWindow()
    window.show()
    QTimer.singleShot(0, window.toggle_monitoring)
    if window.chk_autostart.isChecked():
        QTimer.singleShot(20000, window.hide)
    app_result = app.exec()
    logging.info("Programm beendet")
    sys.exit(app_result)

if __name__ == "__main__":
    main()
