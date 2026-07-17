import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QProgressBar,
    QStatusBar,
    QMessageBox,
    QTextEdit,
    QGroupBox,
)
from PyQt5.QtCore import Qt, QTimer

DARK_STYLE = """
QMainWindow, QWidget { background-color: #1a1a2e; color: #e0e0e0; }
QPushButton {
    background-color: #0d7377; color: #ffffff; border: none;
    padding: 8px 16px; border-radius: 6px; font-size: 13px;
}
QPushButton:hover { background-color: #14a3a8; }
QPushButton.update { background-color: #27ae60; }
QPushButton.update:hover { background-color: #2ecc71; }
QTableWidget {
    background-color: #16213e; color: #e0e0e0; border: 1px solid #0f3460;
    border-radius: 6px; gridline-color: #0f3460;
}
QTableWidget::item:selected { background-color: #0d7377; }
QHeaderView::section {
    background-color: #0f3460; color: #00d4ff; padding: 6px;
    border: 1px solid #1a1a2e; font-weight: bold;
}
QLabel { color: #e0e0e0; }
QGroupBox {
    border: 1px solid #0f3460; border-radius: 8px; margin-top: 10px;
    padding-top: 10px; color: #00d4ff; font-weight: bold;
}
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
QProgressBar {
    border: 1px solid #0f3460; border-radius: 6px; text-align: center;
    background-color: #16213e; color: #e0e0e0; height: 24px;
}
QProgressBar::chunk { background-color: #0d7377; border-radius: 6px; }
QTextEdit {
    background-color: #0a0a15; color: #00ff00; border: 1px solid #0f3460;
    border-radius: 6px; padding: 8px; font-family: "Consolas", "Courier New", monospace;
}
QStatusBar { background-color: #0f3460; color: #e0e0e0; }
"""


class UpdateWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EduOS Update Manager")
        self.resize(800, 600)
        self.setStyleSheet(DARK_STYLE)
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        header = QLabel("EduOS Update Manager")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 28px; padding: 15px; color: #00d4ff;")

        status_group = QGroupBox("System Status")
        status_layout = QVBoxLayout(status_group)
        self.status_label = QLabel("Current Version: 3.0.0 | Status: Up to date")
        self.status_label.setStyleSheet("font-size: 16px; padding: 10px;")
        self.last_check_label = QLabel("Last checked: Never")
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.last_check_label)

        updates_group = QGroupBox("Available Updates")
        updates_layout = QVBoxLayout(updates_group)
        self.update_table = QTableWidget(3, 4)
        self.update_table.setHorizontalHeaderLabels(
            ["Package", "Version", "Size", "Status"]
        )
        updates_data = [
            ("eduos-branding", "3.0.1", "2.5 MB", "Available"),
            ("eduos-exam", "3.0.1", "1.8 MB", "Available"),
            ("eduos-desktop", "3.0.1", "3.2 MB", "Available"),
        ]
        self.update_table.setRowCount(len(updates_data))
        for i, (pkg, ver, size, status) in enumerate(updates_data):
            self.update_table.setItem(i, 0, QTableWidgetItem(pkg))
            self.update_table.setItem(i, 1, QTableWidgetItem(ver))
            self.update_table.setItem(i, 2, QTableWidgetItem(size))
            self.update_table.setItem(i, 3, QTableWidgetItem(status))
        self.update_table.horizontalHeader().setStretchLastSection(True)
        updates_layout.addWidget(self.update_table)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.hide()

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(150)
        self.log.setPlainText(
            "Update Manager initialized.\nReady to check for updates."
        )

        btn_layout = QHBoxLayout()
        check_btn = QPushButton("Check for Updates")
        check_btn.clicked.connect(self.check_updates)
        install_btn = QPushButton("Install Updates")
        install_btn.setStyleSheet("background-color: #27ae60;")
        install_btn.clicked.connect(self.install_updates)
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_status)
        btn_layout.addWidget(check_btn)
        btn_layout.addWidget(install_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(refresh_btn)

        layout.addWidget(header)
        layout.addWidget(status_group)
        layout.addWidget(updates_group)
        layout.addWidget(self.progress)
        layout.addWidget(self.log)
        layout.addLayout(btn_layout)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Update Manager ready")

    def check_updates(self):
        self.log.append("[*] Checking for updates...")
        self.status.showMessage("Checking for updates...")
        self.progress.setRange(0, 0)
        self.progress.show()
        QTimer.singleShot(2000, self.check_complete)

    def check_complete(self):
        self.progress.hide()
        self.progress.setRange(0, 100)
        self.log.append("[+] Update check complete")
        self.log.append("[+] 3 updates available")
        self.status_label.setText("Current Version: 3.0.0 | Status: Updates available")
        self.last_check_label.setText("Last checked: Just now")
        self.status.showMessage("3 updates available")

    def install_updates(self):
        self.log.append("[*] Installing updates...")
        self.status.showMessage("Installing updates...")
        self.progress.setValue(0)
        self.progress.show()
        if hasattr(self, "progress_timer") and self.progress_timer.isActive():
            self.progress_timer.stop()
        self.progress_timer = QTimer()
        self.progress_value = 0
        self.progress_timer.timeout.connect(self.update_progress)
        self.progress_timer.start(100)

    def update_progress(self):
        self.progress_value += 2
        self.progress.setValue(self.progress_value)
        self.log.append(f"[*] Installing... {self.progress_value}%")
        if self.progress_value >= 100:
            self.progress_timer.stop()
            self.progress.hide()
            self.log.append("[+] All updates installed successfully")
            self.status_label.setText("Current Version: 3.0.1 | Status: Up to date")
            self.status.showMessage("Updates installed successfully")
            QMessageBox.information(
                self,
                "Updates Installed",
                "All updates have been installed successfully.\nPlease reboot for changes to take effect.",
            )

    def refresh_status(self):
        self.log.append("[*] Refreshing status...")
        self.status_label.setText("Current Version: 3.0.0 | Status: Checking...")
        QTimer.singleShot(
            1000,
            lambda: self.status_label.setText(
                "Current Version: 3.0.0 | Status: Up to date"
            ),
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = UpdateWindow()
    window.show()
    sys.exit(app.exec_())
