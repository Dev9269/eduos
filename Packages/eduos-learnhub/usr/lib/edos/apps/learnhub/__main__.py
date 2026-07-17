import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                             QListWidget, QTextEdit, QTabWidget, QSplitter,
                             QStatusBar, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

DARK_STYLE = """
QMainWindow, QWidget { background-color: #1a1a2e; color: #e0e0e0; }
QPushButton {
    background-color: #0d7377; color: #ffffff; border: none;
    padding: 8px 16px; border-radius: 6px; font-size: 13px;
}
QPushButton:hover { background-color: #14a3a8; }
QListWidget {
    background-color: #16213e; color: #e0e0e0; border: 1px solid #0f3460;
    border-radius: 6px; padding: 5px; font-size: 14px;
}
QListWidget::item:selected { background-color: #0d7377; }
QLabel { color: #e0e0e0; }
QTextEdit {
    background-color: #16213e; color: #e0e0e0; border: 1px solid #0f3460;
    border-radius: 6px; padding: 8px; font-size: 14px;
}
QTabWidget::pane { border: 1px solid #0f3460; border-radius: 6px; background-color: #16213e; }
QTabBar::tab {
    background-color: #0f3460; color: #e0e0e0; padding: 8px 16px;
    border-top-left-radius: 6px; border-top-right-radius: 6px;
}
QTabBar::tab:selected { background-color: #0d7377; }
QStatusBar { background-color: #0f3460; color: #e0e0e0; }
QSplitter::handle { background-color: #0f3460; width: 2px; }
"""

class LearnHubWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EduOS Learn Hub")
        self.resize(1100, 750)
        self.setStyleSheet(DARK_STYLE)
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        header = QLabel("EduOS Learn Hub")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 28px; padding: 15px; color: #00d4ff;")

        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_courses_tab(), "Courses")
        self.tabs.addTab(self.create_notes_tab(), "Notes")
        self.tabs.addTab(self.create_assignments_tab(), "Assignments")

        main_layout.addWidget(header)
        main_layout.addWidget(self.tabs)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Learn Hub ready")

    def create_courses_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)

        self.course_list = QListWidget()
        self.course_list.addItems(["Mathematics 101", "Physics", "Computer Science",
                                    "English Literature", "History"])
        self.course_list.currentRowChanged.connect(self.on_course_select)

        self.course_content = QTextEdit()
        self.course_content.setReadOnly(True)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.course_list)
        splitter.addWidget(self.course_content)
        splitter.setSizes([200, 600])

        layout.addWidget(splitter)
        return tab

    def on_course_select(self, index):
        courses = {
            0: "Mathematics 101 - Introduction to algebra, geometry, and calculus.",
            1: "Physics - Study of mechanics, thermodynamics, and electromagnetism.",
            2: "Computer Science - Programming fundamentals and data structures.",
            3: "English Literature - Analysis of classic and modern literature.",
            4: "History - Overview of world history from ancient to modern times.",
        }
        self.course_content.setPlainText(courses.get(index, "Select a course"))
        self.status.showMessage(f"Viewing: {courses.get(index, '').split(' - ')[0]}")

    def create_notes_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        toolbar = QHBoxLayout()
        self.note_title = QTextEdit()
        self.note_title.setMaximumHeight(40)
        self.note_title.setPlaceholderText("Note title...")
        save_btn = QPushButton("Save Note")
        save_btn.clicked.connect(self.save_note)
        new_btn = QPushButton("New Note")
        new_btn.clicked.connect(self.new_note)
        toolbar.addWidget(self.note_title)
        toolbar.addWidget(new_btn)
        toolbar.addWidget(save_btn)

        self.note_content = QTextEdit()
        self.note_content.setPlaceholderText("Write your notes here...")

        layout.addLayout(toolbar)
        layout.addWidget(QLabel("Notes:"))
        layout.addWidget(self.note_content)
        return tab

    def save_note(self):
        title = self.note_title.toPlainText().strip()
        if title:
            self.status.showMessage(f"Note '{title}' saved")
            QMessageBox.information(self, "Saved", f"Note '{title}' has been saved.")
        else:
            self.status.showMessage("Please enter a note title")

    def new_note(self):
        self.note_title.clear()
        self.note_content.clear()
        self.status.showMessage("New note created")

    def create_assignments_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.assignment_list = QListWidget()
        self.assignment_list.addItems([
            "Math Homework - Due Friday",
            "Physics Lab Report - Due Monday",
            "CS Programming Project - Due Next Month",
            "English Essay - Due Wednesday",
        ])
        self.assignment_list.currentRowChanged.connect(self.on_assignment_select)

        self.assignment_detail = QTextEdit()
        self.assignment_detail.setReadOnly(True)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.assignment_list)
        splitter.addWidget(self.assignment_detail)

        layout.addWidget(splitter)
        return tab

    def on_assignment_select(self, index):
        details = {
            0: "Math Homework\nComplete problems 1-20 from Chapter 5.\nDue: Friday 5:00 PM",
            1: "Physics Lab Report\nWrite a full lab report for the pendulum experiment.\nDue: Monday 9:00 AM",
            2: "CS Programming Project\nBuild a CRUD application in Python.\nDue: End of month",
            3: "English Essay\n500-word essay on Shakespeare's Hamlet.\nDue: Wednesday 5:00 PM",
        }
        self.assignment_detail.setPlainText(details.get(index, ""))
        self.status.showMessage("Viewing assignment details")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = LearnHubWindow()
    window.show()
    sys.exit(app.exec_())
