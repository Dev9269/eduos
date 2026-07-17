import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                             QListWidget, QGroupBox, QCheckBox, QSlider,
                             QComboBox, QLineEdit, QSpinBox, QFormLayout,
                             QStatusBar, QMessageBox, QFileDialog, QTabWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

DARK_STYLE = """
QMainWindow, QWidget { background-color: #1a1a2e; color: #e0e0e0; }
QPushButton {
    background-color: #0d7377; color: #ffffff; border: none;
    padding: 8px 16px; border-radius: 6px; font-size: 13px;
}
QPushButton:hover { background-color: #14a3a8; }
QPushButton.apply { background-color: #27ae60; }
QPushButton.apply:hover { background-color: #2ecc71; }
QListWidget {
    background-color: #16213e; color: #e0e0e0; border: 1px solid #0f3460;
    border-radius: 6px; padding: 5px; font-size: 14px;
}
QListWidget::item:selected { background-color: #0d7377; }
QLabel { color: #e0e0e0; }
QGroupBox {
    border: 1px solid #0f3460; border-radius: 8px; margin-top: 10px;
    padding-top: 10px; color: #00d4ff; font-weight: bold;
}
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
QCheckBox { color: #e0e0e0; spacing: 8px; }
QSlider::groove:horizontal {
    border: 1px solid #0f3460; height: 6px; background: #16213e;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #0d7377; border: none; width: 16px; height: 16px;
    margin: -5px 0; border-radius: 8px;
}
QComboBox, QLineEdit, QSpinBox {
    background-color: #16213e; color: #e0e0e0; border: 1px solid #0f3460;
    border-radius: 6px; padding: 6px;
}
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView {
    background-color: #16213e; color: #e0e0e0; selection-background-color: #0d7377;
}
QStatusBar { background-color: #0f3460; color: #e0e0e0; }
"""

class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EduOS Settings")
        self.resize(900, 650)
        self.setStyleSheet(DARK_STYLE)
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        nav = QListWidget()
        nav.setMaximumWidth(200)
        nav.addItems(["Appearance", "System", "Network", "Privacy", "About"])
        nav.currentRowChanged.connect(self.on_nav_change)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.create_appearance_panel())
        self.stack.addWidget(self.create_system_panel())
        self.stack.addWidget(self.create_network_panel())
        self.stack.addWidget(self.create_privacy_panel())
        self.stack.addWidget(self.create_about_panel())

        main_layout.addWidget(nav)
        main_layout.addWidget(self.stack, 1)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Settings ready")

    def on_nav_change(self, index):
        self.stack.setCurrentIndex(index)
        panels = ["Appearance", "System", "Network", "Privacy", "About"]
        self.status.showMessage(f"Settings: {panels[index]}")

    def create_appearance_panel(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        g1 = QGroupBox("Theme")
        g1_layout = QFormLayout(g1)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["EduOS Dark", "EduOS Light", "System Default"])
        self.accent_combo = QComboBox()
        self.accent_combo.addItems(["Cyan", "Blue", "Green", "Purple", "Red"])
        g1_layout.addRow("Theme:", self.theme_combo)
        g1_layout.addRow("Accent Color:", self.accent_combo)
        layout.addWidget(g1)

        g2 = QGroupBox("Fonts")
        g2_layout = QFormLayout(g2)
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Noto Sans", "DejaVu Sans", "Liberation Sans"])
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(10)
        g2_layout.addRow("Font:", self.font_combo)
        g2_layout.addRow("Size:", self.font_size)
        layout.addWidget(g2)

        g3 = QGroupBox("Desktop")
        g3_layout = QFormLayout(g3)
        self.wallpaper_btn = QPushButton("Choose Wallpaper...")
        self.wallpaper_btn.clicked.connect(self.choose_wallpaper)
        self.blur_cb = QCheckBox("Enable blur effects")
        self.blur_cb.setChecked(True)
        g3_layout.addRow("Wallpaper:", self.wallpaper_btn)
        g3_layout.addRow("", self.blur_cb)
        layout.addWidget(g3)
        layout.addStretch()
        apply_btn = QPushButton("Apply Appearance Settings")
        apply_btn.setStyleSheet("background-color: #27ae60;")
        apply_btn.clicked.connect(lambda: self.status.showMessage("Appearance settings applied"))
        layout.addWidget(apply_btn)
        return tab

    def choose_wallpaper(self):
        fname, _ = QFileDialog.getOpenFileName(
            self, "Choose Wallpaper", "",
            "Images (*.png *.jpg *.jpeg *.svg)")
        if fname:
            self.status.showMessage(f"Wallpaper set: {fname.split('/')[-1].split('\\')[-1]}")

    def create_system_panel(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        g1 = QGroupBox("Date & Time")
        g1_layout = QFormLayout(g1)
        self.timezone_combo = QComboBox()
        self.timezone_combo.addItems(["UTC", "America/New_York", "Europe/London", "Asia/Kolkata"])
        self.time_format = QComboBox()
        self.time_format.addItems(["24-hour", "12-hour"])
        g1_layout.addRow("Timezone:", self.timezone_combo)
        g1_layout.addRow("Time Format:", self.time_format)
        layout.addWidget(g1)

        g2 = QGroupBox("Updates")
        g2_layout = QVBoxLayout(g2)
        self.auto_update = QCheckBox("Enable automatic updates")
        self.auto_update.setChecked(True)
        self.beta_updates = QCheckBox("Include beta updates")
        g2_layout.addWidget(self.auto_update)
        g2_layout.addWidget(self.beta_updates)
        layout.addWidget(g2)

        g3 = QGroupBox("Power")
        g3_layout = QFormLayout(g3)
        self.suspend_combo = QComboBox()
        self.suspend_combo.addItems(["15 minutes", "30 minutes", "1 hour", "Never"])
        g3_layout.addRow("Suspend when inactive:", self.suspend_combo)
        layout.addWidget(g3)
        layout.addStretch()
        apply_btn = QPushButton("Apply System Settings")
        apply_btn.setStyleSheet("background-color: #27ae60;")
        apply_btn.clicked.connect(lambda: self.status.showMessage("System settings applied"))
        layout.addWidget(apply_btn)
        return tab

    def create_network_panel(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        g1 = QGroupBox("Network")
        g1_layout = QFormLayout(g1)
        self.proxy_cb = QCheckBox("Use proxy server")
        self.proxy_host = QLineEdit()
        self.proxy_host.setPlaceholderText("proxy.example.com")
        self.proxy_port = QSpinBox()
        self.proxy_port.setRange(1, 65535)
        self.proxy_port.setValue(8080)
        g1_layout.addRow("", self.proxy_cb)
        g1_layout.addRow("Proxy Host:", self.proxy_host)
        g1_layout.addRow("Proxy Port:", self.proxy_port)
        layout.addWidget(g1)

        g2 = QGroupBox("Sync Settings")
        g2_layout = QFormLayout(g2)
        self.sync_cb = QCheckBox("Enable cloud sync")
        self.sync_cb.setChecked(True)
        self.sync_interval = QComboBox()
        self.sync_interval.addItems(["Every 5 minutes", "Every 15 minutes", "Every hour"])
        g2_layout.addRow("", self.sync_cb)
        g2_layout.addRow("Sync interval:", self.sync_interval)
        layout.addWidget(g2)
        layout.addStretch()
        apply_btn = QPushButton("Apply Network Settings")
        apply_btn.setStyleSheet("background-color: #27ae60;")
        apply_btn.clicked.connect(lambda: self.status.showMessage("Network settings applied"))
        layout.addWidget(apply_btn)
        return tab

    def create_privacy_panel(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        g1 = QGroupBox("Privacy Controls")
        g1_layout = QVBoxLayout(g1)
        self.telemetry_cb = QCheckBox("Send anonymous usage data")
        self.telemetry_cb.setChecked(False)
        self.diagnostics_cb = QCheckBox("Share diagnostic information")
        self.diagnostics_cb.setChecked(False)
        self.location_cb = QCheckBox("Enable location services")
        self.location_cb.setChecked(False)
        g1_layout.addWidget(self.telemetry_cb)
        g1_layout.addWidget(self.diagnostics_cb)
        g1_layout.addWidget(self.location_cb)
        layout.addWidget(g1)

        g2 = QGroupBox("Data Management")
        g2_layout = QVBoxLayout(g2)
        clear_cache = QPushButton("Clear Application Cache")
        clear_cache.clicked.connect(lambda: self.status.showMessage("Cache cleared"))
        export_data = QPushButton("Export My Data")
        export_data.clicked.connect(lambda: self.status.showMessage("Data exported"))
        g2_layout.addWidget(clear_cache)
        g2_layout.addWidget(export_data)
        layout.addWidget(g2)
        layout.addStretch()
        apply_btn = QPushButton("Apply Privacy Settings")
        apply_btn.setStyleSheet("background-color: #27ae60;")
        apply_btn.clicked.connect(lambda: self.status.showMessage("Privacy settings applied"))
        layout.addWidget(apply_btn)
        return tab

    def create_about_panel(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        about_text = QLabel(
            "<h2 style='color: #00d4ff;'>EduOS v3.0.0</h2>"
            "<p>Educational Operating System</p>"
            "<p>Built for modern education</p>"
            "<hr style='border-color: #0f3460;'>"
            "<p><b>Version:</b> 3.0.0</p>"
            "<p><b>Build:</b> 2026-01-01</p>"
            "<p><b>Platform:</b> Debian 12</p>"
            "<p><b>Kernel:</b> Linux 6.x</p>"
            "<hr style='border-color: #0f3460;'>"
            "<p>EduOS Team &lt;team@edos.edu&gt;</p>"
        )
        about_text.setWordWrap(True)
        about_text.setAlignment(Qt.AlignCenter)
        about_text.setTextFormat(Qt.RichText)
        layout.addWidget(about_text)
        layout.addStretch()
        return tab

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = SettingsWindow()
    window.show()
    sys.exit(app.exec_())
