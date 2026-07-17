import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                             QListWidget, QTextEdit, QTabWidget, QSplitter,
                             QStatusBar, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

DARK_STYLE = """
QMainWindow, QWidget { background-color: #1a1a2e; color: #e0e0e0; }
QPushButton {
    background-color: #0d7377; color: #ffffff; border: none;
    padding: 8px 16px; border-radius: 6px; font-size: 13px;
}
QPushButton:hover { background-color: #14a3a8; }
QPushButton.tool { background-color: #8e44ad; }
QPushButton.tool:hover { background-color: #9b59b6; }
QListWidget {
    background-color: #16213e; color: #e0e0e0; border: 1px solid #0f3460;
    border-radius: 6px; padding: 5px; font-size: 14px;
}
QListWidget::item:selected { background-color: #0d7377; }
QLabel { color: #e0e0e0; }
QTextEdit {
    background-color: #0a0a15; color: #00ff00; border: 1px solid #0f3460;
    border-radius: 6px; padding: 8px; font-family: "Consolas", "Courier New", monospace;
    font-size: 13px;
}
QTabWidget::pane { border: 1px solid #0f3460; border-radius: 6px; background-color: #16213e; }
QTabBar::tab {
    background-color: #0f3460; color: #e0e0e0; padding: 8px 16px;
    border-top-left-radius: 6px; border-top-right-radius: 6px;
}
QTabBar::tab:selected { background-color: #0d7377; }
QTableWidget {
    background-color: #16213e; color: #e0e0e0; border: 1px solid #0f3460;
    border-radius: 6px; gridline-color: #0f3460;
}
QHeaderView::section {
    background-color: #0f3460; color: #00d4ff; padding: 6px;
    border: 1px solid #1a1a2e; font-weight: bold;
}
QStatusBar { background-color: #0f3460; color: #e0e0e0; }
QSplitter::handle { background-color: #0f3460; width: 2px; }
"""

class CyberLabWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EduOS Cyber Lab")
        self.resize(1100, 750)
        self.setStyleSheet(DARK_STYLE)
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        header = QLabel("EduOS Cyber Lab")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 28px; padding: 15px; color: #00d4ff;")

        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_tools_tab(), "Security Tools")
        self.tabs.addTab(self.create_labs_tab(), "Labs")
        self.tabs.addTab(self.create_network_tab(), "Network Scanner")

        main_layout.addWidget(header)
        main_layout.addWidget(self.tabs)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Cyber Lab ready")

    def create_tools_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        tools = QListWidget()
        tools.addItems([
            "Network Scanner", "Port Analyzer", "Packet Capture",
            "Hash Generator", "Encryption Tool", "Password Analyzer",
            "Log Viewer", "Vulnerability Scanner"
        ])
        tools.setMaximumHeight(200)
        tools.currentRowChanged.connect(self.on_tool_select)

        self.tool_output = QTextEdit()
        self.tool_output.setReadOnly(True)
        self.tool_output.setPlainText("Select a tool from the list above to get started...")

        btn_layout = QHBoxLayout()
        run_tool_btn = QPushButton("Run Tool")
        run_tool_btn.clicked.connect(self.run_selected_tool)
        clear_btn = QPushButton("Clear Output")
        clear_btn.clicked.connect(lambda: self.tool_output.clear())
        btn_layout.addWidget(run_tool_btn)
        btn_layout.addWidget(clear_btn)
        btn_layout.addStretch()

        layout.addWidget(QLabel("Available Security Tools:"))
        layout.addWidget(tools)
        layout.addLayout(btn_layout)
        layout.addWidget(QLabel("Output:"))
        layout.addWidget(self.tool_output)
        return tab

    def on_tool_select(self, index):
        tools = [
            "Network Scanner - Scan local network for active hosts",
            "Port Analyzer - Analyze open ports on target system",
            "Packet Capture - Capture and analyze network packets",
            "Hash Generator - Generate MD5, SHA-1, SHA-256 hashes",
            "Encryption Tool - Encrypt and decrypt text",
            "Password Analyzer - Check password strength",
            "Log Viewer - View system security logs",
            "Vulnerability Scanner - Scan for common vulnerabilities",
        ]
        if 0 <= index < len(tools):
            self.tool_output.setPlainText(f"Tool: {tools[index]}\nReady to run. Click 'Run Tool' to execute.")

    def run_selected_tool(self):
        self.tool_output.setPlainText(
            "Running security tool...\n"
            "[+] Initializing...\n"
            "[+] Scanning...\n"
            "[+] Analysis complete.\n"
            "No threats detected.\n"
            "Scan completed in 0.42s")

    def create_labs_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        labs = QListWidget()
        labs.addItems([
            "Lab 1: Network Reconnaissance",
            "Lab 2: Password Cracking Basics",
            "Lab 3: Web Application Security",
            "Lab 4: Cryptography Fundamentals",
            "Lab 5: Malware Analysis Intro",
        ])
        labs.setMaximumHeight(200)
        labs.currentRowChanged.connect(lambda i: self.status.showMessage(
            f"Selected: Lab {i+1}" if i >= 0 else ""))

        lab_info = QTextEdit()
        lab_info.setReadOnly(True)
        lab_info.setPlainText(
            "Lab 1: Network Reconnaissance\n\n"
            "Objectives:\n"
            "- Learn to use nmap for network scanning\n"
            "- Identify open ports and services\n"
            "- Understand network topology\n\n"
            "Tools required: nmap, netstat\n"
            "Duration: 45 minutes")

        start_btn = QPushButton("Start Lab")
        start_btn.clicked.connect(lambda: QMessageBox.information(
            self, "Lab Started", "Lab environment is being prepared..."))

        layout.addWidget(QLabel("Available Labs:"))
        layout.addWidget(labs)
        layout.addWidget(start_btn)
        layout.addWidget(QLabel("Lab Details:"))
        layout.addWidget(lab_info)
        return tab

    def create_network_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.host_table = QTableWidget(8, 4)
        self.host_table.setHorizontalHeaderLabels(["IP Address", "Hostname", "Ports", "Status"])
        hosts = [
            ("192.168.1.1", "gateway", "80, 443", "Online"),
            ("192.168.1.10", "server-01", "22, 80, 3306", "Online"),
            ("192.168.1.11", "server-02", "22, 443", "Online"),
            ("192.168.1.20", "workstation-01", "22, 3389", "Online"),
            ("192.168.1.21", "workstation-02", "22", "Offline"),
            ("192.168.1.30", "printer-01", "631, 9100", "Online"),
            ("192.168.1.50", "nas-01", "22, 443, 445", "Online"),
            ("192.168.1.100", "edos-server", "80, 443, 8000", "Online"),
        ]
        for i, (ip, host, ports, status) in enumerate(hosts):
            self.host_table.setItem(i, 0, QTableWidgetItem(ip))
            self.host_table.setItem(i, 1, QTableWidgetItem(host))
            self.host_table.setItem(i, 2, QTableWidgetItem(ports))
            self.host_table.setItem(i, 3, QTableWidgetItem(status))
        self.host_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.host_table)

        btn_layout = QHBoxLayout()
        scan_btn = QPushButton("Scan Network")
        scan_btn.clicked.connect(lambda: self.status.showMessage("Scanning network..."))
        export_btn = QPushButton("Export Results")
        export_btn.clicked.connect(lambda: self.status.showMessage("Results exported"))
        btn_layout.addWidget(scan_btn)
        btn_layout.addWidget(export_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        scan_log = QTextEdit()
        scan_log.setReadOnly(True)
        scan_log.setMaximumHeight(120)
        scan_log.setPlainText("[2026-01-01 00:00] Network scan initialized\n[2026-01-01 00:00] 8 hosts discovered\n[2026-01-01 00:00] Scan complete")
        layout.addWidget(scan_log)
        return tab

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = CyberLabWindow()
    window.show()
    sys.exit(app.exec_())
