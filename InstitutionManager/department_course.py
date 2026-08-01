"""
EduOS Institution Manager — Department & Course Management Tabs
"""

import sys
from pathlib import Path
_DIR = Path(__file__).parent
if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget,
    QFormLayout, QLineEdit, QSpinBox, QComboBox, QMessageBox, QFrame,
    QScrollArea, QGroupBox, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt

from styles import *
from ui_components import Card, SectionTitle, TableWidget, ActionBar, StatusBadge, btn_primary, btn_outline, btn_small
from config import load_json, save_json, PATHS, log_activity


class DepartmentCourseTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)

        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: transparent; padding-top: 8px; }
            QTabBar::tab { padding: 10px 24px; font-size: 13px; font-weight: 500; color: #64748b; background: transparent; border: none; border-bottom: 2px solid transparent; }
            QTabBar::tab:selected { color: #2563eb; border-bottom: 2px solid #2563eb; }
            QTabBar::tab:hover { color: #1e293b; }
        """)

        tabs.addTab(self._build_departments(), "🏛 Departments")
        tabs.addTab(self._build_courses(), "📚 Courses")

        layout.addWidget(tabs)

    def _build_departments(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 8, 0, 0)

        bar = ActionBar("Department Management")
        bar.add_button("Add Department", "➕", self._add_department)
        layout.addWidget(bar)

        depts = load_json(PATHS["departments"], [])
        table = TableWidget(["ID", "Department Name", "Head of Department", "Established", "Students", "Faculty", "Labs"])
        for d in depts:
            table.add_row([d["id"], d["name"], d["hod"], str(d["estd"]), str(d["students"]), str(d["faculty"]), str(d["labs"])])
        layout.addWidget(table)

        return tab

    def _build_courses(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 8, 0, 0)

        bar = ActionBar("Course Management")
        bar.add_button("Add Course", "➕", self._add_course)
        layout.addWidget(bar)

        courses = load_json(PATHS["courses"], [])
        table = TableWidget(["Code", "Course Name", "Department", "Credits", "Semester", "Type", "Students", "Duration"])
        for c in courses:
            table.add_row([c["id"], c["name"], c["department"], str(c["credits"]), str(c["semester"]), c["type"], str(c["students_enrolled"]), f"{c['duration_weeks']} weeks"])
        layout.addWidget(table)

        return tab

    def _add_department(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Add Department")
        dlg.setFixedSize(450, 350)
        layout = QVBoxLayout(dlg)
        form = QFormLayout()

        id_edit = QLineEdit()
        id_edit.setPlaceholderText("e.g. AI")
        form.addRow("Department ID:", id_edit)
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("e.g. Artificial Intelligence")
        form.addRow("Department Name:", name_edit)
        hod_edit = QLineEdit()
        hod_edit.setPlaceholderText("e.g. Dr. Name")
        form.addRow("Head of Department:", hod_edit)
        estd_spin = QSpinBox()
        estd_spin.setRange(1990, 2030)
        estd_spin.setValue(2024)
        form.addRow("Established:", estd_spin)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        layout.addWidget(buttons)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            depts = load_json(PATHS["departments"], [])
            depts.append({
                "id": id_edit.text(), "name": name_edit.text(), "hod": hod_edit.text(),
                "estd": estd_spin.value(), "students": 0, "faculty": 0, "labs": 0
            })
            save_json(PATHS["departments"], depts)
            log_activity("Department Added", f"{name_edit.text()} department created")
            self._rebuild()
            QMessageBox.information(dlg, "Success", f"Department '{name_edit.text()}' added.")

    def _add_course(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Add Course")
        dlg.setFixedSize(500, 400)
        layout = QVBoxLayout(dlg)
        form = QFormLayout()

        code_edit = QLineEdit()
        code_edit.setPlaceholderText("e.g. CS301")
        form.addRow("Course Code:", code_edit)
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("e.g. Machine Learning")
        form.addRow("Course Name:", name_edit)

        depts = load_json(PATHS["departments"], [])
        dept_combo = QComboBox()
        for d in depts:
            dept_combo.addItem(f"{d['id']} - {d['name']}", d["id"])
        form.addRow("Department:", dept_combo)

        credits_spin = QSpinBox()
        credits_spin.setRange(1, 6)
        credits_spin.setValue(3)
        form.addRow("Credits:", credits_spin)

        sem_spin = QSpinBox()
        sem_spin.setRange(1, 8)
        sem_spin.setValue(1)
        form.addRow("Semester:", sem_spin)

        type_combo = QComboBox()
        type_combo.addItems(["Core", "Elective", "Lab", "Project"])
        form.addRow("Type:", type_combo)

        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        layout.addWidget(buttons)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            courses = load_json(PATHS["courses"], [])
            courses.append({
                "id": code_edit.text(), "name": name_edit.text(),
                "department": dept_combo.currentData(),
                "credits": credits_spin.value(), "semester": sem_spin.value(),
                "type": type_combo.currentText(),
                "students_enrolled": 0, "duration_weeks": 16,
                "description": ""
            })
            save_json(PATHS["courses"], courses)
            log_activity("Course Added", f"{name_edit.text()} course created")
            QMessageBox.information(dlg, "Success", f"Course '{name_edit.text()}' added.")

    def _rebuild(self):
        parent = self.parent()
        if parent:
            idx = parent.indexOf(self)
            if idx >= 0:
                parent.removeTab(idx)
                new_tab = DepartmentCourseTab(parent)
                parent.insertTab(idx, new_tab, "🏛 Departments / 📚 Courses")
                parent.setCurrentIndex(idx)
