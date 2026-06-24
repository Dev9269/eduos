#!/usr/bin/env python3
"""
EduOS Exam Admin Tool - Manage examinations, view results, control sessions
"""

import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QTabWidget,
    QGroupBox, QTextEdit, QFileDialog, QMessageBox, QHeaderView,
    QListWidget, QSplitter, QFrame, QComboBox, QLineEdit, QSpinBox,
    QDialog, QDialogButtonBox, QFormLayout, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette


EXAM_DATA_DIR = Path.home() / ".eduos" / "exam"
EXAMS_DIR = EXAM_DATA_DIR / "exams"
RESULTS_DIR = EXAM_DATA_DIR / "results"
CONFIG_DIR = EXAM_DATA_DIR / "config"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)


class ExamCreatorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Exam")
        self.setFixedSize(500, 600)
        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("e.g. Mid-Term Examination 2026")
        form.addRow("Exam Title:", self.title_edit)

        self.subject_edit = QLineEdit()
        self.subject_edit.setPlaceholderText("e.g. Computer Science")
        form.addRow("Subject:", self.subject_edit)

        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(5, 480)
        self.duration_spin.setValue(60)
        self.duration_spin.setSuffix(" minutes")
        form.addRow("Duration:", self.duration_spin)

        self.mcq_count = QSpinBox()
        self.mcq_count.setRange(0, 100)
        self.mcq_count.setValue(10)
        form.addRow("MCQ Questions:", self.mcq_count)

        self.prog_count = QSpinBox()
        self.prog_count.setRange(0, 10)
        self.prog_count.setValue(2)
        form.addRow("Programming Questions:", self.prog_count)

        self.short_count = QSpinBox()
        self.short_count.setRange(0, 10)
        self.short_count.setValue(3)
        form.addRow("Short Answer Questions:", self.short_count)

        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("Leave blank for default key")
        form.addRow("Encryption Key:", self.key_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_exam_config(self):
        return {
            "title": self.title_edit.text() or "Untitled Exam",
            "subject": self.subject_edit.text() or "General",
            "duration_minutes": self.duration_spin.value(),
            "mcq_count": self.mcq_count.value(),
            "prog_count": self.prog_count.value(),
            "short_count": self.short_count.value(),
            "encryption_key": self.key_edit.text() or "eduos-exam-default-key"
        }


class ExamAdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EduOS Admin Center - Exam Management")
        self.setGeometry(100, 100, 1200, 700)
        self._setup_ui()
        self._load_results()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        header = QLabel("📋 EduOS Examination Management Console")
        header.setStyleSheet("font-size: 24px; font-weight: bold; padding: 16px; color: #2563eb;")
        layout.addWidget(header)

        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #ddd; border-radius: 8px; padding: 16px; background: white; }
            QTabBar::tab { padding: 10px 20px; font-size: 14px; }
            QTabBar::tab:selected { background: #2563eb; color: white; border-radius: 6px 6px 0 0; }
        """)

        self.results_tab = self._build_results_tab()
        self.create_tab = self._build_create_tab()
        self.control_tab = self._build_control_tab()

        tabs.addTab(self.results_tab, "📊 Results")
        tabs.addTab(self.create_tab, "✏ Create Exam")
        tabs.addTab(self.control_tab, "🎮 Session Control")

        layout.addWidget(tabs)

        status = QLabel("⚡ System Ready | All modules operational")
        status.setStyleSheet("padding: 8px; color: #666; font-size: 12px;")
        layout.addWidget(status)

    def _build_results_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        controls = QHBoxLayout()
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("QPushButton { padding: 8px 16px; font-size: 13px; background: #2563eb; color: white; border: none; border-radius: 6px; } QPushButton:hover { background: #1d4ed8; } QPushButton:pressed { background: #1e40af; padding: 9px 15px 7px 17px; }")
        refresh_btn.clicked.connect(self._load_results)
        controls.addWidget(refresh_btn)

        export_btn = QPushButton("📤 Export Selected")
        export_btn.setStyleSheet("QPushButton { padding: 8px 16px; font-size: 13px; background: #16a34a; color: white; border: none; border-radius: 6px; } QPushButton:hover { background: #15803d; } QPushButton:pressed { background: #166534; padding: 9px 15px 7px 17px; }")
        export_btn.clicked.connect(self._export_results)
        controls.addWidget(export_btn)

        controls.addStretch()
        layout.addLayout(controls)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels(["Student ID", "Name", "Exam", "Date", "Status", "Actions"])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e0e0e0; border-radius: 8px;
                gridline-color: #f0f0f0; font-size: 13px;
            }
            QTableWidget::item { padding: 8px; }
            QHeaderView::section { background: #f8f9fa; padding: 8px; font-weight: bold; border: none; }
        """)
        layout.addWidget(self.results_table)

        return tab

    def _build_create_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        info = QLabel("Create a new examination configuration. Questions will be auto-generated with placeholders.")
        info.setWordWrap(True)
        info.setStyleSheet("font-size: 13px; color: #666; padding: 8px; background: #f0f4ff; border-radius: 6px;")
        layout.addWidget(info)

        form = QFormLayout()
        form.setSpacing(12)

        self.ct_title = QLineEdit()
        self.ct_title.setPlaceholderText("e.g. Final Examination 2026")
        form.addRow("Exam Title:", self.ct_title)

        self.ct_subject = QLineEdit()
        self.ct_subject.setPlaceholderText("e.g. Data Structures")
        form.addRow("Subject:", self.ct_subject)

        self.ct_duration = QSpinBox()
        self.ct_duration.setRange(5, 480)
        self.ct_duration.setValue(60)
        self.ct_duration.setSuffix(" minutes")
        form.addRow("Duration:", self.ct_duration)

        self.ct_mcq = QSpinBox(); self.ct_mcq.setRange(0, 100); self.ct_mcq.setValue(10)
        form.addRow("MCQ Questions:", self.ct_mcq)

        self.ct_prog = QSpinBox(); self.ct_prog.setRange(0, 10); self.ct_prog.setValue(2)
        form.addRow("Programming Questions:", self.ct_prog)

        self.ct_short = QSpinBox(); self.ct_short.setRange(0, 10); self.ct_short.setValue(3)
        form.addRow("Short Answer Questions:", self.ct_short)

        layout.addLayout(form)

        create_btn = QPushButton("📝 Generate Exam Configuration")
        create_btn.setStyleSheet("""
            QPushButton {
                background: #2563eb; color: white; padding: 12px;
                font-size: 16px; border: none; border-radius: 8px;
            }
            QPushButton:hover { background: #1d4ed8; }
            QPushButton:pressed { background: #1e40af; padding: 13px 11px 11px 13px; }
        """)
        create_btn.clicked.connect(self._create_exam)
        layout.addWidget(create_btn)

        layout.addStretch()
        return tab

    def _build_control_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        info = QLabel("Control examination sessions across the lab. Start, monitor, and terminate exams.")
        info.setWordWrap(True)
        info.setStyleSheet("font-size: 13px; color: #666; padding: 8px; background: #f0f4ff; border-radius: 6px;")
        layout.addWidget(info)

        machines_group = QGroupBox("Lab Machines")
        machines_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; padding-top: 16px; }")
        mlayout = QVBoxLayout(machines_group)

        self.machine_list = QListWidget()
        self.machine_list.setStyleSheet("font-size: 13px;")
        for i in range(1, 11):
            self.machine_list.addItem(f"Lab-{i:02d}  ● Available")
        mlayout.addWidget(self.machine_list)
        layout.addWidget(machines_group)

        actions = QHBoxLayout()
        start_btn = QPushButton("▶ Start Exam on Selected")
        start_btn.setStyleSheet("QPushButton { background: #16a34a; color: white; padding: 10px 16px; border: none; border-radius: 6px; font-weight: bold; } QPushButton:hover { background: #15803d; } QPushButton:pressed { background: #166534; padding: 11px 15px 9px 17px; }")
        start_btn.clicked.connect(lambda: QMessageBox.information(self, "Start Exam", "Exam started on selected machine."))
        actions.addWidget(start_btn)

        stop_btn = QPushButton("■ Terminate Exam")
        stop_btn.setStyleSheet("QPushButton { background: #dc2626; color: white; padding: 10px 16px; border: none; border-radius: 6px; font-weight: bold; } QPushButton:hover { background: #b91c1c; } QPushButton:pressed { background: #991b1b; padding: 11px 15px 9px 17px; }")
        stop_btn.clicked.connect(lambda: QMessageBox.information(self, "Terminate Exam", "Exam terminated on selected machine."))
        actions.addWidget(stop_btn)

        lock_btn = QPushButton("🔒 Lock Selected")
        lock_btn.setStyleSheet("QPushButton { background: #f59e0b; color: white; padding: 10px 16px; border: none; border-radius: 6px; font-weight: bold; } QPushButton:hover { background: #d97706; } QPushButton:pressed { background: #b45309; padding: 11px 15px 9px 17px; }")
        lock_btn.clicked.connect(lambda: QMessageBox.information(self, "Lock Machine", "Selected machine locked."))
        actions.addWidget(lock_btn)

        actions.addStretch()
        layout.addLayout(actions)

        broadcast_group = QGroupBox("Send Announcement")
        broadcast_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; padding-top: 16px; }")
        blayout = QVBoxLayout(broadcast_group)
        self.broadcast_msg = QTextEdit()
        self.broadcast_msg.setMaximumHeight(80)
        self.broadcast_msg.setPlaceholderText("Type announcement here...")
        blayout.addWidget(self.broadcast_msg)

        send_btn = QPushButton("📢 Send to All")
        send_btn.setStyleSheet("QPushButton { background: #7c3aed; color: white; padding: 10px; border: none; border-radius: 6px; font-weight: bold; } QPushButton:hover { background: #6d28d9; } QPushButton:pressed { background: #5b21b6; padding: 11px 9px 9px 11px; }")
        send_btn.clicked.connect(self._send_announcement)
        blayout.addWidget(send_btn)
        layout.addWidget(broadcast_group)

        return tab

    def _load_results(self):
        self.results_table.setRowCount(0)
        if RESULTS_DIR.exists():
            files = sorted(RESULTS_DIR.glob("*"), reverse=True)
            for f in files[:50]:
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                self.results_table.setItem(row, 0, QTableWidgetItem(f.stem.split("_")[0] if "_" in f.stem else f.stem))
                self.results_table.setItem(row, 1, QTableWidgetItem("Student"))
                self.results_table.setItem(row, 2, QTableWidgetItem("Exam"))
                self.results_table.setItem(row, 3, QTableWidgetItem(datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")))
                self.results_table.setItem(row, 4, QTableWidgetItem("✅ Submitted"))

                view_btn = QPushButton("📄 View")
                view_btn.setStyleSheet("padding: 4px 8px; font-size: 12px;")
                view_btn.clicked.connect(lambda checked, p=f: self._view_result(p))
                self.results_table.setCellWidget(row, 5, view_btn)

    def _export_results(self):
        QMessageBox.information(self, "Export", "Results export functionality will be implemented.")

    def _view_result(self, filepath):
        try:
            with open(filepath) as f:
                data = json.load(f)
            content = json.dumps(data, indent=2)
            viewer = QTextEdit()
            viewer.setReadOnly(True)
            viewer.setPlainText(content)
            viewer.setStyleSheet("font-family: monospace; font-size: 12px; padding: 8px;")
            dlg = QDialog(self)
            dlg.setWindowTitle(f"Result: {filepath.name}")
            dlg.setGeometry(200, 200, 800, 600)
            layout = QVBoxLayout(dlg)
            layout.addWidget(viewer)
            dlg.exec()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open result: {e}")

    def _create_exam(self):
        title = self.ct_title.text() or "Untitled"
        subject = self.ct_subject.text() or "General"
        duration = self.ct_duration.value()
        mcq = self.ct_mcq.value()
        prog = self.ct_prog.value()
        short = self.ct_short.value()

        exam = {
            "title": title,
            "subject": subject,
            "duration_minutes": duration,
            "encryption_key": "eduos-exam-default-key",
            "instructions": "Read each question carefully. Manage your time wisely.",
            "questions": []
        }

        import random
        mcq_templates = [
            ("What is the capital of France?", ["London", "Paris", "Berlin", "Madrid"], "Paris"),
            ("Which planet is known as the Red Planet?", ["Venus", "Mars", "Jupiter", "Saturn"], "Mars"),
            ("What is 2 + 2?", ["3", "4", "5", "6"], "4"),
            ("Which language is used for web development?", ["Python", "HTML", "C++", "Java"], "HTML"),
            ("What does CPU stand for?", ["Central Processing Unit", "Computer Personal Unit", "Central Program Unit", "None"], "Central Processing Unit"),
            ("Which is an operating system?", ["Windows", "Mouse", "Keyboard", "Monitor"], "Windows"),
            ("What is the square root of 64?", ["6", "7", "8", "9"], "8"),
            ("Which protocol is used for email?", ["HTTP", "FTP", "SMTP", "TCP"], "SMTP"),
            ("What is the chemical symbol for water?", ["H2O", "CO2", "NaCl", "O2"], "H2O"),
            ("Which year did World War II end?", ["1943", "1944", "1945", "1946"], "1945"),
        ]

        for i in range(mcq):
            if i < len(mcq_templates):
                q, opts, correct = mcq_templates[i]
            else:
                q = f"Sample MCQ Question {i+1}?"
                opts = [f"Option A", f"Option B", f"Option C", f"Option D"]
                correct = "Option A"
            exam["questions"].append({
                "type": "mcq",
                "question": q,
                "options": opts,
                "correct": correct
            })

        for i in range(prog):
            exam["questions"].append({
                "type": "programming",
                "question": f"Programming Question {i+1}: Write a function to solve the given problem.",
                "language": "Python",
                "starter_code": f"def solution_{i+1}():\n    # Your implementation here\n    pass"
            })

        for i in range(short):
            exam["questions"].append({
                "type": "short_answer",
                "question": f"Short Answer Question {i+1}: Explain the concept briefly."
            })

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"exam_{timestamp}.json"
        filepath = EXAMS_DIR / filename
        with open(filepath, "w") as f:
            json.dump(exam, f, indent=2)

        QMessageBox.information(self, "Success", f"Exam '{title}' created successfully!\n\nSaved to: {filepath}")

    def _send_announcement(self):
        msg = self.broadcast_msg.toPlainText().strip()
        if msg:
            QMessageBox.information(self, "Sent", f"Announcement sent to all lab machines.\n\nMessage: {msg}")
            self.broadcast_msg.clear()


def main():
    app = QApplication(sys.argv)
    window = ExamAdminWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
