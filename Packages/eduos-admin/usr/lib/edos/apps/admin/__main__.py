import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QStackedWidget,
    QListWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QStatusBar,
    QTextEdit,
)
from PyQt5.QtCore import Qt

DARK_STYLE = """
QMainWindow, QWidget { background-color: #1a1a2e; color: #e0e0e0; }
QPushButton {
    background-color: #0d7377; color: #ffffff; border: none;
    padding: 8px 16px; border-radius: 6px; font-size: 13px;
}
QPushButton:hover { background-color: #14a3a8; }
QPushButton.danger { background-color: #c0392b; }
QPushButton.danger:hover { background-color: #e74c3c; }
QListWidget {
    background-color: #16213e; color: #e0e0e0; border: 1px solid #0f3460;
    border-radius: 6px; padding: 5px; font-size: 14px;
}
QListWidget::item:selected { background-color: #0d7377; }
QLabel { color: #e0e0e0; font-size: 13px; }
QTableWidget {
    background-color: #16213e; color: #e0e0e0; border: 1px solid #0f3460;
    border-radius: 6px; gridline-color: #0f3460;
}
QTableWidget::item:selected { background-color: #0d7377; }
QHeaderView::section {
    background-color: #0f3460; color: #00d4ff; padding: 6px;
    border: 1px solid #1a1a2e; font-weight: bold;
}
QLineEdit, QTextEdit {
    background-color: #16213e; color: #e0e0e0; border: 1px solid #0f3460;
    border-radius: 6px; padding: 6px;
}
QGroupBox {
    border: 1px solid #0f3460; border-radius: 8px; margin-top: 10px;
    padding-top: 10px; color: #00d4ff; font-weight: bold;
}
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
QStatusBar { background-color: #0f3460; color: #e0e0e0; }
"""


class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EduOS Admin Center")
        self.resize(1100, 750)
        self.setStyleSheet(DARK_STYLE)
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        nav = QListWidget()
        nav.setMaximumWidth(200)
        nav.addItems(["Users", "Devices", "Exams", "Updates"])
        nav.currentRowChanged.connect(self.on_nav_change)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.create_users_tab())
        self.stack.addWidget(self.create_devices_tab())
        self.stack.addWidget(self.create_exams_tab())
        self.stack.addWidget(self.create_updates_tab())

        main_layout.addWidget(nav)
        main_layout.addWidget(self.stack, 1)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Admin Center ready")

    def on_nav_change(self, index):
        self.stack.setCurrentIndex(index)
        pages = [
            "User Management",
            "Device Management",
            "Exam Management",
            "Update Management",
        ]
        self.status.showMessage(pages[index])

    def create_users_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("User Management"))
        self.user_table = QTableWidget(10, 4)
        self.user_table.setHorizontalHeaderLabels(
            ["Username", "Role", "Status", "Last Login"]
        )
        for i in range(10):
            self.user_table.setItem(i, 0, QTableWidgetItem(f"user{i + 1}"))
            self.user_table.setItem(
                i, 1, QTableWidgetItem("Student" if i % 3 else "Teacher")
            )
            self.user_table.setItem(i, 2, QTableWidgetItem("Active"))
            self.user_table.setItem(i, 3, QTableWidgetItem("2026-01-01"))
        self.user_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.user_table)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add User")
        add_btn.clicked.connect(lambda: self.status.showMessage("Add user dialog"))
        remove_btn = QPushButton("Remove User")
        remove_btn.clicked.connect(lambda: self.status.showMessage("Remove user"))
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(lambda: self.status.showMessage("Users refreshed"))
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(refresh_btn)
        layout.addLayout(btn_layout)
        return tab

    def create_devices_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Device Management"))
        self.device_table = QTableWidget(5, 4)
        self.device_table.setHorizontalHeaderLabels(
            ["Device Name", "Type", "Status", "Last Sync"]
        )
        for i in range(5):
            self.device_table.setItem(i, 0, QTableWidgetItem(f"Device-{i + 1}"))
            self.device_table.setItem(i, 1, QTableWidgetItem("Workstation"))
            self.device_table.setItem(i, 2, QTableWidgetItem("Online"))
            self.device_table.setItem(i, 3, QTableWidgetItem("2026-01-01 00:00"))
        self.device_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.device_table)

        btn_layout = QHBoxLayout()
        sync_btn = QPushButton("Sync All")
        sync_btn.clicked.connect(
            lambda: self.status.showMessage("Syncing all devices...")
        )
        lock_btn = QPushButton("Lock Devices")
        lock_btn.clicked.connect(lambda: self.status.showMessage("Locking devices..."))
        btn_layout.addWidget(sync_btn)
        btn_layout.addWidget(lock_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        return tab

    def create_exams_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Exam Management"))
        self.exam_table = QTableWidget(5, 4)
        self.exam_table.setHorizontalHeaderLabels(
            ["Exam Name", "Duration", "Status", "Submissions"]
        )
        exams = [
            ("Midterm Math", "60 min", "Active", "45"),
            ("Physics Final", "120 min", "Scheduled", "0"),
            ("CS Quiz 3", "30 min", "Completed", "120"),
            ("English Essay", "90 min", "Active", "30"),
            ("History Exam", "60 min", "Draft", "0"),
        ]
        for i, (name, dur, status, subs) in enumerate(exams):
            self.exam_table.setItem(i, 0, QTableWidgetItem(name))
            self.exam_table.setItem(i, 1, QTableWidgetItem(dur))
            self.exam_table.setItem(i, 2, QTableWidgetItem(status))
            self.exam_table.setItem(i, 3, QTableWidgetItem(subs))
        self.exam_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.exam_table)

        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create Exam")
        create_btn.clicked.connect(
            lambda: self.status.showMessage("Create exam dialog")
        )
        grade_btn = QPushButton("Auto-Grade")
        grade_btn.clicked.connect(
            lambda: self.status.showMessage("Auto-grading triggered")
        )
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(grade_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        return tab

    def create_updates_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Update Management"))
        self.update_info = QTextEdit()
        self.update_info.setReadOnly(True)
        self.update_info.setPlainText(
            "Current Version: 3.0.0\n"
            "Update Status: Up to date\n"
            "Last Check: 2026-01-01 00:00\n"
            "Available Updates: None"
        )
        layout.addWidget(self.update_info)
        btn_layout = QHBoxLayout()
        check_btn = QPushButton("Check Updates")
        check_btn.clicked.connect(
            lambda: self.status.showMessage("Checking for updates...")
        )
        deploy_btn = QPushButton("Deploy Update")
        deploy_btn.clicked.connect(
            lambda: self.status.showMessage("Deploying update...")
        )
        btn_layout.addWidget(check_btn)
        btn_layout.addWidget(deploy_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        return tab


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = AdminWindow()
    window.show()
    sys.exit(app.exec_())
