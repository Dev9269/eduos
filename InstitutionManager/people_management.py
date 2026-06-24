"""
EduOS Institution Manager — Student & Faculty Management Tabs
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget,
    QMessageBox, QFrame, QLineEdit, QScrollArea
)
from PyQt6.QtCore import Qt

from styles import *
from ui_components import Card, SectionTitle, TableWidget, ActionBar, StatusBadge, btn_primary, btn_outline
from config import load_json, save_json, PATHS, log_activity


class PeopleManagementTab(QWidget):
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

        tabs.addTab(self._build_students(), "👨‍🎓 Students")
        tabs.addTab(self._build_faculty(), "👨‍🏫 Faculty")

        layout.addWidget(tabs)

    def _build_students(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 8, 0, 0)

        bar = ActionBar("Student Management")
        bar.add_button("Add Student", "➕", self._show_student_count)
        bar.add_button("Export", "📤", self._show_student_count, btn_outline())
        layout.addWidget(bar)

        # Search bar
        search_bar = QHBoxLayout()
        self.student_search = QLineEdit()
        self.student_search.setPlaceholderText("🔍 Search by name, ID, or department...")
        self.student_search.textChanged.connect(self._filter_students)
        search_bar.addWidget(self.student_search)
        layout.addLayout(search_bar)

        students = load_json(PATHS["students"], [])
        self.student_table = TableWidget(["ID", "Name", "Gender", "Department", "Year", "CGPA", "Attendance", "Status"])
        for s in students:
            status_type = "active" if s["status"] == "Active" else "warning" if s["status"] == "Graduated" else "inactive"
            self.student_table.add_row([
                s["id"], s["name"], s["gender"], s["department"],
                f"Year {s['year']}", f"{s['cgpa']}", f"{s['attendance_pct']}%",
                ""
            ])
            row = self.student_table.rowCount() - 1
            badge = StatusBadge(s["status"], status_type)
            self.student_table.setCellWidget(row, 7, badge)

        self._all_students = students
        layout.addWidget(self.student_table)

        return tab

    def _filter_students(self):
        query = self.student_search.text().lower()
        for row in range(self.student_table.rowCount()):
            match = False
            for col in range(min(3, self.student_table.columnCount())):
                item = self.student_table.item(row, col)
                if item and query in item.text().lower():
                    match = True
                    break
            self.student_table.setRowHidden(row, not match)

    def _build_faculty(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 8, 0, 0)

        bar = ActionBar("Faculty Management")
        bar.add_button("Add Faculty", "➕", self._show_faculty_count)
        bar.add_button("Export", "📤", self._show_faculty_count, btn_outline())
        layout.addWidget(bar)

        faculty = load_json(PATHS["faculty"], [])
        table = TableWidget(["ID", "Name", "Department", "Designation", "Qualification", "Specialization", "Experience", "Status"])
        for f in faculty:
            status_type = "active" if f["status"] == "Active" else "warning"
            table.add_row([
                f["id"], f["name"], f["department"], f["designation"],
                f["qualification"], f["specialization"], f"{f['experience_years']} yrs", ""
            ])
            row = table.rowCount() - 1
            badge = StatusBadge(f["status"], status_type)
            table.setCellWidget(row, 7, badge)
        layout.addWidget(table)

        return tab

    def _show_student_count(self):
        students = load_json(PATHS["students"], [])
        QMessageBox.information(self, "Student Records", f"Total students enrolled: {len(students)}")

    def _show_faculty_count(self):
        faculty = load_json(PATHS["faculty"], [])
        QMessageBox.information(self, "Faculty Records", f"Total faculty members: {len(faculty)}")
