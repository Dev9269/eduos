#!/usr/bin/env python3
"""
EduOS Demo Examination Application
A fully functional demo exam environment for presentations and faculty demonstrations.
Built with PyQt6 for native KDE integration.

Screens:
  1. Login         — Student authentication with demo credentials
  2. Instructions  — Exam brief and rules
  3. MCQ Section   — 10 questions with navigation palette and timer
  4. Coding        — Built-in editor with syntax highlighting
  5. Review        — Overview before final submission
  6. Results       — Score, JSON export, PDF export
"""

import sys
import os
import json
import subprocess
import tempfile
import signal
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QRadioButton, QButtonGroup, QTextEdit,
    QStackedWidget, QFrame, QMessageBox, QProgressBar,
    QComboBox, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QEvent
from PyQt6.QtGui import (
    QColor, QFont, QTextCharFormat, QSyntaxHighlighter
)

from demo_exam_config import (
    DEMO_CREDENTIALS, EXAM_CONFIG, MCQ_QUESTIONS, CODING_CHALLENGE
)


RESULTS_DIR = Path.home() / "EduOS" / "ExamMode" / "DemoResults"
SECURITY_LOG = RESULTS_DIR / "security_log.txt"
AUTO_SAVE_INTERVAL_MS = 30000


STYLESHEET = """
QMainWindow, QDialog { background: #111827; }
QLabel {
    color: #f1f5f9; font-family: 'Inter', 'Segoe UI', 'Noto Sans', sans-serif;
    font-size: 14px;
}
QPushButton {
    background: rgba(255, 255, 255, 0.12); color: white; border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px; padding: 10px 24px; font-size: 14px; font-weight: 600;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
QPushButton:hover { background: rgba(255, 255, 255, 0.2); border-color: rgba(255, 255, 255, 0.25); }
QPushButton:pressed { background: rgba(255, 255, 255, 0.08); }
QPushButton:disabled { background: rgba(255, 255, 255, 0.04); color: rgba(255, 255, 255, 0.3); border-color: rgba(255, 255, 255, 0.05); }
QPushButton#secondary {
    background: transparent; border: 2px solid rgba(255, 255, 255, 0.3); color: rgba(255, 255, 255, 0.9);
}
QPushButton#secondary:hover { background: rgba(255, 255, 255, 0.08); }
QPushButton#danger {
    background: rgba(220, 53, 69, 0.3); border-color: rgba(220, 53, 69, 0.4);
}
QPushButton#danger:hover { background: rgba(220, 53, 69, 0.5); }
QPushButton#success {
    background: rgba(255, 255, 255, 0.15); border-color: rgba(255, 255, 255, 0.2);
}
QPushButton#success:hover { background: rgba(255, 255, 255, 0.25); }
QPushButton#nav {
    background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 8px 12px; font-size: 13px; min-width: 40px; color: rgba(255, 255, 255, 0.8);
}
QPushButton#nav:hover { background: rgba(255, 255, 255, 0.12); }
QPushButton#nav:checked, QPushButton#nav[current="true"] {
    background: rgba(200, 145, 62, 0.5); border-color: rgba(200, 145, 62, 0.6); color: white;
}
QRadioButton {
    color: #f1f5f9; font-size: 15px; padding: 10px 14px;
    background: rgba(255, 255, 255, 0.06); border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
QRadioButton:hover { border-color: rgba(255, 255, 255, 0.3); background: rgba(255, 255, 255, 0.1); }
QRadioButton:checked { border-color: rgba(200, 145, 62, 0.6); background: rgba(200, 145, 62, 0.12); }
QRadioButton::indicator {
    width: 18px; height: 18px; border-radius: 9px;
    border: 2px solid rgba(255, 255, 255, 0.3); margin-right: 10px;
}
QRadioButton::indicator:checked {
    background: #c8913e; border-color: #c8913e;
}
QTextEdit, QPlainTextEdit {
    background: rgba(0, 0, 0, 0.25); color: #e2e8f0; border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px; padding: 12px; font-size: 14px;
    font-family: 'Fira Code', 'Cascadia Code', monospace;
}
QComboBox {
    background: rgba(255, 255, 255, 0.08); color: white; border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 6px; padding: 6px 12px; font-size: 13px;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
QComboBox:hover { border-color: rgba(255, 255, 255, 0.25); }
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView {
    background: #1e1e2e; color: white; selection-background-color: rgba(200, 145, 62, 0.5);
    selection-color: white;
}
QProgressBar {
    background: rgba(255, 255, 255, 0.08); border: none; border-radius: 4px; height: 8px;
    text-align: center; font-size: 11px; color: rgba(255, 255, 255, 0.4);
}
QProgressBar::chunk { background: #c8913e; border-radius: 4px; }
QScrollBar:vertical {
    background: transparent; width: 8px; margin: 0;
}
QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.15); border-radius: 4px; min-height: 30px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._rules = []

        keyword_fmt = QTextCharFormat()
        keyword_fmt.setForeground(QColor("#c678dd"))
        keyword_fmt.setFontWeight(QFont.Weight.Bold)
        keywords = [
            "def", "class", "return", "if", "else", "elif", "for", "while",
            "import", "from", "as", "try", "except", "finally", "with",
            "pass", "break", "continue", "and", "or", "not", "in", "is",
            "True", "False", "None", "lambda", "yield", "raise", "assert",
            "global", "nonlocal"
        ]
        for kw in keywords:
            self._rules.append((rf'\b{kw}\b', keyword_fmt))

        string_fmt = QTextCharFormat()
        string_fmt.setForeground(QColor("#98c379"))
        self._rules.append((r'"[^"]*"', string_fmt))
        self._rules.append((r"'[^']*'", string_fmt))

        comment_fmt = QTextCharFormat()
        comment_fmt.setForeground(QColor("#5c6370"))
        self._rules.append((r'#.*', comment_fmt))

        decorator_fmt = QTextCharFormat()
        decorator_fmt.setForeground(QColor("#61afef"))
        self._rules.append((r'@\w+', decorator_fmt))

        number_fmt = QTextCharFormat()
        number_fmt.setForeground(QColor("#d19a66"))
        self._rules.append((r'\b[0-9]+\b', number_fmt))

        builtin_fmt = QTextCharFormat()
        builtin_fmt.setForeground(QColor("#56b6c2"))
        builtins = ["print", "range", "len", "str", "int", "float", "list",
                    "dict", "set", "tuple", "bool", "type", "input", "open",
                    "isinstance", "enumerate", "zip", "map", "filter", "sorted",
                    "reversed", "any", "all"]
        for b in builtins:
            self._rules.append((rf'\b{b}\b', builtin_fmt))

    def highlightBlock(self, text):
        import re
        for pattern, fmt in self._rules:
            for match in re.finditer(pattern, text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)


class CppHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._rules = []

        keyword_fmt = QTextCharFormat()
        keyword_fmt.setForeground(QColor("#c678dd"))
        keyword_fmt.setFontWeight(QFont.Weight.Bold)
        keywords = [
            "auto", "break", "case", "const", "continue", "default", "do",
            "else", "enum", "extern", "for", "goto", "if", "register",
            "return", "signed", "sizeof", "static", "struct", "switch",
            "typedef", "union", "unsigned", "volatile", "while", "class",
            "public", "private", "protected", "virtual", "override", "final",
            "template", "typename", "namespace", "using", "include", "define",
            "int", "float", "double", "char", "void", "bool", "string",
            "true", "false", "nullptr", "this", "new", "delete", "try",
            "catch", "throw", "friend", "inline", "explicit", "mutable"
        ]
        for kw in keywords:
            self._rules.append((rf'\b{kw}\b', keyword_fmt))

        string_fmt = QTextCharFormat()
        string_fmt.setForeground(QColor("#98c379"))
        self._rules.append((r'"[^"]*"', string_fmt))
        self._rules.append((r"'[^']*'", string_fmt))

        comment_fmt = QTextCharFormat()
        comment_fmt.setForeground(QColor("#5c6370"))
        self._rules.append((r'//.*', comment_fmt))
        self._rules.append((r'/\*.*?\*/', comment_fmt))

        preprocessor_fmt = QTextCharFormat()
        preprocessor_fmt.setForeground(QColor("#61afef"))
        self._rules.append((r'#\s*\w+', preprocessor_fmt))

        number_fmt = QTextCharFormat()
        number_fmt.setForeground(QColor("#d19a66"))
        self._rules.append((r'\b[0-9]+\b', number_fmt))

    def highlightBlock(self, text):
        import re
        for pattern, fmt in self._rules:
            for match in re.finditer(pattern, text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)


class JavaHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._rules = []

        keyword_fmt = QTextCharFormat()
        keyword_fmt.setForeground(QColor("#c678dd"))
        keyword_fmt.setFontWeight(QFont.Weight.Bold)
        keywords = [
            "abstract", "assert", "boolean", "break", "byte", "case", "catch",
            "char", "class", "const", "continue", "default", "do", "double",
            "else", "enum", "extends", "final", "finally", "float", "for",
            "goto", "if", "implements", "import", "instanceof", "int",
            "interface", "long", "native", "new", "package", "private",
            "protected", "public", "return", "short", "static", "strictfp",
            "super", "switch", "synchronized", "this", "throw", "throws",
            "transient", "try", "void", "volatile", "while", "true", "false",
            "null", "String", "System", "out", "println"
        ]
        for kw in keywords:
            self._rules.append((rf'\b{kw}\b', keyword_fmt))

        string_fmt = QTextCharFormat()
        string_fmt.setForeground(QColor("#98c379"))
        self._rules.append((r'"[^"]*"', string_fmt))
        self._rules.append((r"'[^']*'", string_fmt))

        comment_fmt = QTextCharFormat()
        comment_fmt.setForeground(QColor("#5c6370"))
        self._rules.append((r'//.*', comment_fmt))
        self._rules.append((r'/\*.*?\*/', comment_fmt))

        annotation_fmt = QTextCharFormat()
        annotation_fmt.setForeground(QColor("#61afef"))
        self._rules.append((r'@\w+', annotation_fmt))

        number_fmt = QTextCharFormat()
        number_fmt.setForeground(QColor("#d19a66"))
        self._rules.append((r'\b[0-9]+\b', number_fmt))

    def highlightBlock(self, text):
        import re
        for pattern, fmt in self._rules:
            for match in re.finditer(pattern, text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)


class SecurityLogger:
    """Logs restricted-action attempts to a file."""

    def __init__(self):
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    def log(self, action: str, details: str = ""):
        try:
            with open(SECURITY_LOG, "a") as f:
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{ts}] {action}")
                if details:
                    f.write(f" | {details}")
                f.write("\n")
        except Exception:
            pass


class LoginScreen(QWidget):
    login_successful = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.06);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 40px;
                max-width: 440px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(16)

        title = QLabel("EduOS")
        title.setStyleSheet("font-size: 36px; font-weight: bold; color: rgba(255, 255, 255, 0.9); letter-spacing: -0.5px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)

        subtitle = QLabel("Demo Examination Portal")
        subtitle.setStyleSheet("font-size: 15px; color: rgba(255, 255, 255, 0.5);")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(subtitle)

        card_layout.addSpacing(12)

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Student ID")
        self.id_input.setFixedHeight(42)
        self.id_input.setStyleSheet(
            "background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 8px; "
            "padding: 10px; font-size: 15px; color: white; selection-background-color: rgba(200, 145, 62, 0.4);"
        )
        self.id_input.returnPressed.connect(lambda: self.name_input.setFocus())
        card_layout.addWidget(self.id_input)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full Name")
        self.name_input.setFixedHeight(42)
        self.name_input.setStyleSheet(
            "background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 8px; "
            "padding: 10px; font-size: 15px; color: white; selection-background-color: rgba(200, 145, 62, 0.4);"
        )
        self.name_input.returnPressed.connect(lambda: self.key_input.setFocus())
        card_layout.addWidget(self.name_input)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Exam Key")
        self.key_input.setFixedHeight(42)
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setStyleSheet(
            "background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 8px; "
            "padding: 10px; font-size: 15px; color: white; selection-background-color: rgba(200, 145, 62, 0.4);"
        )
        self.key_input.returnPressed.connect(self._handle_login)
        card_layout.addWidget(self.key_input)

        demo_hint = QLabel("Demo: DEMO001 / EDUOS2026")
        demo_hint.setStyleSheet("font-size: 12px; color: rgba(255, 255, 255, 0.35);")
        demo_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(demo_hint)

        card_layout.addSpacing(4)

        self.login_btn = QPushButton("Start Demo Exam")
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: rgba(200, 145, 62, 0.5); color: white;
                border: 1px solid rgba(200, 145, 62, 0.4); border-radius: 8px;
                padding: 14px; font-size: 15px; font-weight: 600;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
            QPushButton:hover { background: rgba(200, 145, 62, 0.65); }
        """)
        self.login_btn.clicked.connect(self._handle_login)
        card_layout.addWidget(self.login_btn)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #ef4444; font-size: 13px;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.error_label)

        layout.addWidget(card)

    def _handle_login(self):
        sid = self.id_input.text().strip()
        name = self.name_input.text().strip()
        key = self.key_input.text().strip()

        if not sid or not name or not key:
            self.error_label.setText("Please fill in all fields.")
            return

        if sid == DEMO_CREDENTIALS["student_id"] and key == DEMO_CREDENTIALS["exam_key"]:
            self.login_successful.emit(sid, name)
        else:
            self.error_label.setText("Invalid credentials. Use DEMO001 / EDUOS2026")


class InstructionsScreen(QWidget):
    proceed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setStyleSheet("background: rgba(255, 255, 255, 0.06); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); padding: 40px; max-width: 600px;")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)

        title = QLabel("Examination Instructions")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: rgba(255, 255, 255, 0.9);")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #dee2e6; max-height: 1px;")
        card_layout.addWidget(sep)

        duration = QLabel(
            f"Duration: {EXAM_CONFIG['total_duration_minutes']} minutes "
            f"(MCQ: {EXAM_CONFIG['mcq_duration_minutes']} min, "
            f"Coding: {EXAM_CONFIG['coding_duration_minutes']} min)"
        )
        duration.setStyleSheet("font-size: 14px; font-weight: 600; color: rgba(255, 255, 255, 0.7); padding: 10px 14px; background: rgba(255, 255, 255, 0.06); border-radius: 8px;")
        duration.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(duration)

        for instr in EXAM_CONFIG["instructions"]:
            item = QLabel(instr)
            item.setStyleSheet("font-size: 14px; color: rgba(255, 255, 255, 0.65); padding: 3px 0; line-height: 1.5;")
            item.setWordWrap(True)
            card_layout.addWidget(item)

        card_layout.addSpacing(12)

        self.start_btn = QPushButton("Begin Examination")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background: rgba(200, 145, 62, 0.5); color: white;
                border: 1px solid rgba(200, 145, 62, 0.4); border-radius: 8px;
                padding: 14px; font-size: 15px; font-weight: 600;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
            QPushButton:hover { background: rgba(200, 145, 62, 0.65); }
        """)
        self.start_btn.clicked.connect(self.proceed.emit)
        self.start_btn.setDefault(True)
        card_layout.addWidget(self.start_btn)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.start_btn.setFocus()

        layout.addWidget(card)


class MCQSectionWidget(QWidget):
    section_complete = pyqtSignal(dict)

    def __init__(self, student_id, student_name):
        super().__init__()
        self.student_id = student_id
        self.student_name = student_name
        self.answers = {}
        self.time_remaining = EXAM_CONFIG["mcq_duration_minutes"] * 60
        self.current_question = 0
        self._setup_ui()
        self._load_question(0)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 20, 32, 20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setStyleSheet("background: rgba(255, 255, 255, 0.06); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); padding: 32px; max-width: 700px;")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(16)

        # Timer + progress row
        info_row = QHBoxLayout()
        self.timer_label = QLabel(self._format_time(self.time_remaining))
        self.timer_label.setStyleSheet("font-size: 20px; font-weight: bold; color: rgba(255, 255, 255, 0.9);")
        info_row.addWidget(self.timer_label)
        info_row.addStretch()
        self.progress_label = QLabel(f"Q 1 / {len(MCQ_QUESTIONS)}")
        self.progress_label.setStyleSheet("font-size: 14px; color: rgba(255, 255, 255, 0.5);")
        info_row.addWidget(self.progress_label)
        card_layout.addLayout(info_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #dee2e6; max-height: 1px;")
        card_layout.addWidget(sep)

        # Question
        self.topic_label = QLabel("Topic")
        self.topic_label.setStyleSheet("font-size: 11px; color: rgba(255, 255, 255, 0.5); padding: 3px 10px; background: rgba(255, 255, 255, 0.06); border-radius: 4px; max-width: 200px;")
        self.topic_label.setFixedHeight(24)
        card_layout.addWidget(self.topic_label)

        self.question_label = QLabel("Question text")
        self.question_label.setStyleSheet("font-size: 17px; color: rgba(255, 255, 255, 0.9); padding: 6px 0; line-height: 1.6;")
        self.question_label.setWordWrap(True)
        card_layout.addWidget(self.question_label)

        card_layout.addSpacing(4)

        # Options
        self.option_group = QButtonGroup(self)
        self.option_widgets = []
        for i in range(4):
            radio = QRadioButton(f"Option {i + 1}")
            radio.setStyleSheet("""
                QRadioButton {
                    font-size: 15px; color: rgba(255, 255, 255, 0.8); padding: 10px 14px;
                    background: rgba(255, 255, 255, 0.04); border-radius: 8px;
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    spacing: 10px;
                }
                QRadioButton:hover { border-color: rgba(255, 255, 255, 0.25); background: rgba(255, 255, 255, 0.08); }
                QRadioButton:checked { border-color: rgba(200, 145, 62, 0.6); background: rgba(200, 145, 62, 0.12); }
                QRadioButton::indicator { width: 18px; height: 18px; border-radius: 9px; border: 2px solid rgba(255, 255, 255, 0.25); }
                QRadioButton::indicator:checked { border-color: #c8913e; background: #c8913e; }
            """)
            radio.toggled.connect(self._on_option_toggled)
            card_layout.addWidget(radio)
            self.option_widgets.append(radio)
            self.option_group.addButton(radio, i)

        card_layout.addStretch()

        # Navigation buttons
        nav_row = QHBoxLayout()
        self.prev_btn = QPushButton("Back")
        self.prev_btn.setStyleSheet("""
            QPushButton { background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.8); border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px; padding: 10px 24px; font-size: 14px; font-weight: 600; }
            QPushButton:hover { background: rgba(255,255,255,0.15); }
            QPushButton:disabled { background: rgba(255,255,255,0.03); color: rgba(255,255,255,0.2); border-color: rgba(255,255,255,0.05); }
        """)
        self.prev_btn.clicked.connect(self._go_prev)
        nav_row.addWidget(self.prev_btn)

        nav_row.addStretch()

        self.next_btn = QPushButton("Next")
        self.next_btn.setStyleSheet("""
            QPushButton { background: rgba(200,145,62,0.5); color: white; border: 1px solid rgba(200,145,62,0.4);
            border-radius: 8px; padding: 10px 24px; font-size: 14px; font-weight: 600; }
            QPushButton:hover { background: rgba(200,145,62,0.65); }
        """)
        self.next_btn.clicked.connect(self._go_next)
        nav_row.addWidget(self.next_btn)
        card_layout.addLayout(nav_row)

        # Submit button
        self.submit_mcq_btn = QPushButton("Submit & Continue")
        self.submit_mcq_btn.setStyleSheet("""
            QPushButton { background: rgba(200,145,62,0.5); color: white; border: 1px solid rgba(200,145,62,0.4);
            border-radius: 8px; padding: 12px; font-size: 15px; font-weight: 600; }
            QPushButton:hover { background: rgba(200,145,62,0.65); }
        """)
        self.submit_mcq_btn.clicked.connect(self._submit_mcq)
        card_layout.addWidget(self.submit_mcq_btn)

        main_layout.addWidget(card)

        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)

        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self._auto_save)
        self.auto_save_timer.start(AUTO_SAVE_INTERVAL_MS)

    def _format_time(self, seconds):
        m = seconds // 60
        s = seconds % 60
        return f"{m:02d}:{s:02d}"

    def _tick(self):
        self.time_remaining -= 1
        self.timer_label.setText(self._format_time(self.time_remaining))
        if self.time_remaining <= 120:
            self.timer_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #dc3545;")
        if self.time_remaining <= 0:
            self._submit_mcq()

    def _load_question(self, index):
        if index < 0 or index >= len(MCQ_QUESTIONS):
            return
        self.current_question = index
        q = MCQ_QUESTIONS[index]

        self.topic_label.setText(f"📌 {q['topic']}  |  {q['difficulty']}")
        self.question_label.setText(f"Q{index + 1}. {q['question']}")

        # Block signals while updating
        self.option_group.blockSignals(True)
        for i, opt in enumerate(q["options"]):
            self.option_widgets[i].setText(opt)
            self.option_widgets[i].setChecked(False)
        self.option_group.blockSignals(False)

        # Restore saved answer
        if index in self.answers:
            self.option_widgets[self.answers[index]].setChecked(True)

        self._update_progress()

    def _update_progress(self):
        answered = len(self.answers)
        self.progress_label.setText(f"Q {self.current_question + 1} / {len(MCQ_QUESTIONS)}  •  Answered {answered} / {len(MCQ_QUESTIONS)}")
        self.prev_btn.setEnabled(self.current_question > 0)
        self.next_btn.setEnabled(self.current_question < len(MCQ_QUESTIONS) - 1)

    def _on_option_toggled(self):
        radio = self.sender()
        if radio and radio.isChecked():
            idx = self.option_group.id(radio)
            if idx >= 0:
                self.answers[self.current_question] = idx
                self._update_progress()

    def _go_prev(self):
        if self.current_question > 0:
            self._load_question(self.current_question - 1)

    def _go_next(self):
        if self.current_question < len(MCQ_QUESTIONS) - 1:
            self._load_question(self.current_question + 1)

    def _auto_save(self):
        self._update_progress()

    def _submit_mcq(self):
        self.timer.stop()
        self.auto_save_timer.stop()

        # Calculate score
        correct = 0
        for q in MCQ_QUESTIONS:
            ans = self.answers.get(q["id"] - 1, -1)
            if ans == q["correct"]:
                correct += 1

        total = len(MCQ_QUESTIONS)
        score_pct = round((correct / total) * 100, 1)

        mcq_result = {
            "correct": correct,
            "total": total,
            "percentage": score_pct,
            "answers": {q["id"]: self.answers.get(i, -1) for i, q in enumerate(MCQ_QUESTIONS)},
            "time_spent_seconds": (EXAM_CONFIG["mcq_duration_minutes"] * 60) - self.time_remaining
        }

        self.section_complete.emit(mcq_result)


class CodingSectionWidget(QWidget):
    section_complete = pyqtSignal(dict)

    def __init__(self, student_id, student_name):
        super().__init__()
        self.student_id = student_id
        self.student_name = student_name
        self.time_remaining = EXAM_CONFIG["coding_duration_minutes"] * 60
        self.code = ""
        self.language = "Python"
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 20, 32, 20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setStyleSheet("background: rgba(255, 255, 255, 0.06); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); padding: 28px; max-width: 800px;")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)

        # Top bar
        top_bar = QHBoxLayout()
        self.coding_timer_label = QLabel(self._format_time(self.time_remaining))
        self.coding_timer_label.setStyleSheet("font-size: 20px; font-weight: bold; color: rgba(255, 255, 255, 0.9);")
        top_bar.addWidget(self.coding_timer_label)
        top_bar.addStretch()
        top_bar.addWidget(QLabel("Language:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Python", "C", "C++", "Java"])
        self.lang_combo.currentTextChanged.connect(self._change_language)
        top_bar.addWidget(self.lang_combo)
        card_layout.addLayout(top_bar)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #dee2e6; max-height: 1px;")
        card_layout.addWidget(sep)

        # Description
        desc_layout = QVBoxLayout()
        challenge_title = QLabel(CODING_CHALLENGE['title'])
        challenge_title.setStyleSheet("font-size: 17px; font-weight: bold; color: rgba(255, 255, 255, 0.9);")
        desc_layout.addWidget(challenge_title)
        desc_text = QLabel(CODING_CHALLENGE["description"])
        desc_text.setStyleSheet("font-size: 14px; color: rgba(255, 255, 255, 0.65); line-height: 1.6;")
        desc_text.setWordWrap(True)
        desc_layout.addWidget(desc_text)
        card_layout.addLayout(desc_layout)

        # Code editor (keep dark for IDE feel)
        self.code_editor = QTextEdit()
        self.code_editor.setStyleSheet("""
            QTextEdit {
                background: #1e1e1e; color: #d4d4d4; border: 1px solid #3c3c3c;
                border-radius: 6px; padding: 14px; font-size: 14px;
                font-family: 'Fira Code', 'Cascadia Code', monospace; line-height: 1.5;
            }
        """)
        self.code_editor.setMinimumHeight(180)
        self._change_language("Python")
        card_layout.addWidget(self.code_editor)

        # Action buttons
        action_bar = QHBoxLayout()
        run_btn = QPushButton("Run Code")
        run_btn.setStyleSheet("""
            QPushButton { background: rgba(255,255,255,0.1); color: white; border: 1px solid rgba(255,255,255,0.15);
            border-radius: 8px; padding: 10px 20px; font-size: 14px; font-weight: 600; }
            QPushButton:hover { background: rgba(255,255,255,0.18); }
        """)
        run_btn.clicked.connect(self._run_code)
        action_bar.addWidget(run_btn)

        save_draft_btn = QPushButton("Save Draft")
        save_draft_btn.setStyleSheet("""
            QPushButton { background: rgba(255,255,255,0.06); color: rgba(255,255,255,0.7); border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px; padding: 10px 20px; font-size: 14px; }
            QPushButton:hover { background: rgba(255,255,255,0.12); }
        """)
        save_draft_btn.clicked.connect(self._save_draft)
        action_bar.addWidget(save_draft_btn)

        action_bar.addStretch()

        self.submit_coding_btn = QPushButton("Submit & Finish Exam")
        self.submit_coding_btn.setStyleSheet("""
            QPushButton { background: rgba(200,145,62,0.5); color: white; border: 1px solid rgba(200,145,62,0.4);
            border-radius: 8px; padding: 10px 20px; font-size: 14px; font-weight: 600; }
            QPushButton:hover { background: rgba(200,145,62,0.65); }
        """)
        self.submit_coding_btn.clicked.connect(self._submit_coding)
        action_bar.addWidget(self.submit_coding_btn)

        card_layout.addLayout(action_bar)

        # Output area
        output_header = QLabel("Output")
        output_header.setStyleSheet("font-size: 12px; color: rgba(255, 255, 255, 0.4); padding: 2px 4px;")
        card_layout.addWidget(output_header)
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setStyleSheet("background: #1e1e1e; color: #d4d4d4; border: 1px solid #3c3c3c; border-radius: 6px; padding: 10px; font-family: 'Fira Code', monospace; font-size: 13px;")
        self.output_area.setMaximumHeight(140)
        card_layout.addWidget(self.output_area)

        main_layout.addWidget(card)

        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)

    def _format_time(self, seconds):
        m = seconds // 60
        s = seconds % 60
        return f"{m:02d}:{s:02d}"

    def _tick(self):
        self.time_remaining -= 1
        self.coding_timer_label.setText(self._format_time(self.time_remaining))
        if self.time_remaining <= 120:
            self.coding_timer_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #dc3545;")
        if self.time_remaining <= 0:
            self._submit_coding()

    def _change_language(self, lang):
        self.language = lang
        self.code = CODING_CHALLENGE["starter_code"][lang]
        self.code_editor.setPlainText(self.code)

        # Set highlighter
        if hasattr(self, '_highlighter'):
            del self._highlighter
        if lang == "Python":
            self._highlighter = PythonHighlighter(self.code_editor.document())
        elif lang in ("C", "C++"):
            self._highlighter = CppHighlighter(self.code_editor.document())
        elif lang == "Java":
            self._highlighter = JavaHighlighter(self.code_editor.document())

    def _run_code(self):
        code = self.code_editor.toPlainText()
        lang = self.lang_combo.currentText()
        self.output_area.clear()
        self.output_area.append(f"$ Running {lang} code...\n")

        try:
            if lang == "Python":
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write(code)
                    fname = f.name
                result = subprocess.run(
                    ["python3", fname], capture_output=True, text=True, timeout=10
                )
                os.unlink(fname)

            elif lang == "C":
                with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
                    f.write(code)
                    src = f.name
                out = src + ".out"
                comp = subprocess.run(["gcc", src, "-o", out], capture_output=True, text=True, timeout=15)
                if comp.returncode == 0:
                    result = subprocess.run([out], capture_output=True, text=True, timeout=10)
                    os.unlink(src)
                    os.unlink(out)
                else:
                    self.output_area.append(comp.stderr)
                    return

            elif lang == "C++":
                with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
                    f.write(code)
                    src = f.name
                out = src + ".out"
                comp = subprocess.run(["g++", src, "-o", out], capture_output=True, text=True, timeout=15)
                if comp.returncode == 0:
                    result = subprocess.run([out], capture_output=True, text=True, timeout=10)
                    os.unlink(src)
                    os.unlink(out)
                else:
                    self.output_area.append(comp.stderr)
                    return

            elif lang == "Java":
                with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as f:
                    f.write(code)
                    src = f.name
                comp = subprocess.run(["javac", src], capture_output=True, text=True, timeout=15)
                if comp.returncode == 0:
                    class_name = "Solution"
                    result = subprocess.run(["java", "-cp", os.path.dirname(src), class_name],
                                            capture_output=True, text=True, timeout=10)
                    os.unlink(src)
                    class_file = os.path.join(os.path.dirname(src), f"{class_name}.class")
                    if os.path.exists(class_file):
                        os.unlink(class_file)
                else:
                    self.output_area.append(comp.stderr)
                    return

            if 'result' in locals() and result.stdout:
                self.output_area.append(result.stdout)
            if 'result' in locals() and result.stderr:
                self.output_area.append(f"⚠ {result.stderr}")
            self.output_area.append("\n✅ Execution complete.")

        except subprocess.TimeoutExpired:
            self.output_area.append("⏱ Execution timed out (10s limit).")
        except FileNotFoundError as e:
            self.output_area.append(f"❌ Compiler not found: {e}")
        except Exception as e:
            self.output_area.append(f"❌ Error: {e}")

    def _save_draft(self):
        try:
            draft_path = RESULTS_DIR / f"coding_draft_{self.student_id}.txt"
            with open(draft_path, "w") as f:
                f.write(f"Language: {self.lang_combo.currentText()}\n")
                f.write(f"Saved: {datetime.now().isoformat()}\n")
                f.write("-" * 40 + "\n")
                f.write(self.code_editor.toPlainText())
            self.output_area.append(f"💾 Draft saved to {draft_path.name}")
        except Exception as e:
            self.output_area.append(f"❌ Save failed: {e}")

    def _submit_coding(self):
        self.timer.stop()
        code = self.code_editor.toPlainText()
        lang = self.lang_combo.currentText()

        coding_result = {
            "language": lang,
            "code": code,
            "time_spent_seconds": (EXAM_CONFIG["coding_duration_minutes"] * 60) - self.time_remaining,
            "status": "submitted"
        }
        self.section_complete.emit(coding_result)


class ReviewScreen(QWidget):
    confirmed = pyqtSignal()
    back_requested = pyqtSignal()

    def __init__(self, student_id, student_name, mcq_result, coding_result):
        super().__init__()
        self.student_id = student_id
        self.student_name = student_name
        self.mcq_result = mcq_result
        self.coding_result = coding_result
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setStyleSheet("background: rgba(255, 255, 255, 0.06); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); padding: 36px; max-width: 560px;")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(14)

        title = QLabel("Review Before Submission")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: rgba(255, 255, 255, 0.9);")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #dee2e6; max-height: 1px;")
        card_layout.addWidget(sep)

        # MCQ Summary
        mcq_frame = QFrame()
        mcq_frame.setStyleSheet("background: rgba(255, 255, 255, 0.04); border-radius: 10px; padding: 16px;")
        mcq_l = QVBoxLayout(mcq_frame)
        mcq_l.setSpacing(4)
        mcq_l.addWidget(QLabel("MCQ Section"))
        mcq_l.addWidget(QLabel(f"  Correct Answers: {self.mcq_result['correct']} / {self.mcq_result['total']}"))
        mcq_l.addWidget(QLabel(f"  Score: {self.mcq_result['percentage']}%"))
        card_layout.addWidget(mcq_frame)

        # Coding Summary
        coding_frame = QFrame()
        coding_frame.setStyleSheet("background: rgba(255, 255, 255, 0.04); border-radius: 10px; padding: 16px;")
        coding_l = QVBoxLayout(coding_frame)
        coding_l.setSpacing(4)
        status_text = "Submitted" if self.coding_result.get('status') == 'submitted' else 'Draft'
        coding_l.addWidget(QLabel("Coding Section"))
        coding_l.addWidget(QLabel(f"  Language: {self.coding_result['language']}"))
        coding_l.addWidget(QLabel(f"  Status: {status_text}"))
        card_layout.addWidget(coding_frame)

        card_layout.addSpacing(8)

        confirm_btn = QPushButton("Confirm & Submit Final Exam")
        confirm_btn.setStyleSheet("""
            QPushButton {
                background: rgba(200, 145, 62, 0.5); color: white;
                border: 1px solid rgba(200, 145, 62, 0.4); border-radius: 8px;
                padding: 12px; font-size: 15px; font-weight: 600;
            }
            QPushButton:hover { background: rgba(200, 145, 62, 0.65); }
        """)
        confirm_btn.clicked.connect(self.confirmed.emit)
        card_layout.addWidget(confirm_btn)

        cancel_btn = QPushButton("Go Back")
        cancel_btn.setObjectName("secondary")
        cancel_btn.clicked.connect(self.back_requested.emit)
        card_layout.addWidget(cancel_btn)

        layout.addWidget(card)


class ResultsScreen(QWidget):
    def __init__(self, student_id, student_name, mcq_result, coding_result, exam_data):
        super().__init__()
        self.student_id = student_id
        self.student_name = student_name
        self.mcq_result = mcq_result
        self.coding_result = coding_result
        self.exam_data = exam_data
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setStyleSheet("background: rgba(255, 255, 255, 0.06); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); padding: 40px; max-width: 520px;")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(14)

        passed = self.mcq_result["percentage"] >= EXAM_CONFIG["passing_percentage"]
        status_text = "Passed" if passed else "Completed"

        title = QLabel(status_text)
        title.setStyleSheet(f"font-size: 26px; font-weight: bold; color: rgba(255, 255, 255, 0.9);")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #dee2e6; max-height: 1px;")
        card_layout.addWidget(sep)

        # Student info
        info = QLabel(f"{self.student_name} ({self.student_id})")
        info.setStyleSheet("font-size: 15px; color: rgba(255, 255, 255, 0.6);")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(info)

        ts = QLabel(f"Submitted: {self.exam_data['timestamp']}")
        ts.setStyleSheet("font-size: 12px; color: rgba(255, 255, 255, 0.35);")
        ts.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(ts)

        card_layout.addSpacing(8)

        # Score
        score_frame = QFrame()
        score_frame.setStyleSheet("background: rgba(255, 255, 255, 0.04); border-radius: 10px; padding: 20px;")
        score_layout = QVBoxLayout(score_frame)

        score_pct = self.mcq_result["percentage"]
        score_label = QLabel(f"{score_pct}%")
        score_label.setStyleSheet(f"font-size: 44px; font-weight: bold; color: rgba(255, 255, 255, 0.9);")
        score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_layout.addWidget(score_label)

        detail = QLabel(f"MCQ: {self.mcq_result['correct']}/{self.mcq_result['total']} correct  |  Coding: {self.coding_result['language']} submitted")
        detail.setStyleSheet("font-size: 14px; color: rgba(255, 255, 255, 0.5);")
        detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_layout.addWidget(detail)

        card_layout.addWidget(score_frame)

        # Export buttons
        export_layout = QHBoxLayout()

        json_btn = QPushButton("Export JSON")
        json_btn.clicked.connect(self._export_json)
        export_layout.addWidget(json_btn)

        pdf_btn = QPushButton("Export PDF")
        pdf_btn.clicked.connect(self._export_pdf)
        export_layout.addWidget(pdf_btn)

        card_layout.addLayout(export_layout)

        # Exit button
        exit_btn = QPushButton("Exit Demo Exam")
        exit_btn.setObjectName("danger")
        exit_btn.clicked.connect(self._exit_app)
        card_layout.addWidget(exit_btn)

        layout.addWidget(card)

    def _build_result_data(self):
        return {
            "student": {
                "id": self.student_id,
                "name": self.student_name
            },
            "exam": {
                "title": EXAM_CONFIG["title"],
                "timestamp": self.exam_data["timestamp"],
                "status": "completed"
            },
            "mcq_section": {
                "correct": self.mcq_result["correct"],
                "total": self.mcq_result["total"],
                "percentage": self.mcq_result["percentage"],
                "time_spent_seconds": self.mcq_result.get("time_spent_seconds", 0)
            },
            "coding_section": {
                "language": self.coding_result["language"],
                "status": self.coding_result.get("status", "submitted"),
                "time_spent_seconds": self.coding_result.get("time_spent_seconds", 0)
            },
            "overall": {
                "percentage": self.mcq_result["percentage"],
                "passed": self.mcq_result["percentage"] >= EXAM_CONFIG["passing_percentage"]
            }
        }

    def _export_json(self):
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        data = self._build_result_data()
        fname = RESULTS_DIR / f"result_{self.student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(fname, "w") as f:
            json.dump(data, f, indent=2)
        QMessageBox.information(self, "Exported", f"Results saved to:\n{fname}")

    def _export_pdf(self):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors

            RESULTS_DIR.mkdir(parents=True, exist_ok=True)
            fname = RESULTS_DIR / f"result_{self.student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            doc = SimpleDocTemplate(str(fname), pagesize=A4)
            styles = getSampleStyleSheet()
            elements = []

            elements.append(Paragraph("EduOS Demo Examination Report", styles["Title"]))
            elements.append(Spacer(1, 20))

            elements.append(Paragraph(f"<b>Student:</b> {self.student_name} ({self.student_id})", styles["Normal"]))
            elements.append(Paragraph(f"<b>Date:</b> {self.exam_data['timestamp']}", styles["Normal"]))
            elements.append(Spacer(1, 12))

            passed = self.mcq_result["percentage"] >= EXAM_CONFIG["passing_percentage"]
            status = "PASSED" if passed else "COMPLETED"
            elements.append(Paragraph(f"<b>Status:</b> {status}", styles["Normal"]))
            elements.append(Spacer(1, 20))

            data = [
                ["Section", "Score", "Status"],
                ["MCQ Questions", f"{self.mcq_result['correct']}/{self.mcq_result['total']} ({self.mcq_result['percentage']}%)", "Completed"],
                ["Coding Challenge", self.coding_result["language"], self.coding_result.get("status", "submitted").title()],
                ["Overall", f"{self.mcq_result['percentage']}%", status]
            ]
            t = Table(data, colWidths=[200, 200, 150])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#1e293b")),
                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("PADDING", (0, 0), (-1, -1), 10),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 30))
            elements.append(Paragraph("EduOS — Engineering Education Edition", styles["Normal"]))
            elements.append(Paragraph("Developed by Jainam H. Maru", styles["Normal"]))

            doc.build(elements)
            QMessageBox.information(self, "Exported", f"PDF saved to:\n{fname}")

        except ImportError:
            QMessageBox.warning(self, "Export Error", "reportlab not installed. Install with: pip install reportlab")
        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"PDF export failed: {e}")

    def _exit_app(self):
        QApplication.quit()


class DemoExamWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.student_id = ""
        self.student_name = ""
        self.mcq_result = None
        self.coding_result = None
        self.exam_start_time = None
        self.security_logger = SecurityLogger()

        self.setWindowTitle("EduOS Demo Examination")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
        )
        self.setStyleSheet(STYLESHEET)

        screen = QApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.availableGeometry())
        else:
            self.setGeometry(0, 0, 1280, 800)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.login_screen = LoginScreen()
        self.login_screen.login_successful.connect(self._on_login)
        self.stack.addWidget(self.login_screen)

        self._install_anti_cheat()

        self.showFullScreen()

    def _install_anti_cheat(self):
        # Install global event filter to block restricted keys
        self._anti_cheat_filter = AntiCheatFilter(self.security_logger)
        QApplication.instance().installEventFilter(self._anti_cheat_filter)

    def _log_security(self, action, details=""):
        self.security_logger.log(action, details)

    def _on_login(self, sid, name):
        self.student_id = sid
        self.student_name = name
        self.exam_start_time = datetime.now()

        self._log_security("LOGIN", f"Student {sid} ({name}) logged in")

        # Show instructions
        self.instructions_screen = InstructionsScreen()
        self.instructions_screen.proceed.connect(self._start_mcq)
        self.stack.addWidget(self.instructions_screen)
        self.stack.setCurrentWidget(self.instructions_screen)

    def _start_mcq(self):
        self.mcq_section = MCQSectionWidget(self.student_id, self.student_name)
        self.mcq_section.section_complete.connect(self._on_mcq_complete)
        self.stack.addWidget(self.mcq_section)
        self.stack.setCurrentWidget(self.mcq_section)
        self._log_security("SECTION_START", "MCQ section started")

    def _on_mcq_complete(self, mcq_result):
        self.mcq_result = mcq_result
        self._log_security("SECTION_COMPLETE", f"MCQ: {mcq_result['correct']}/{mcq_result['total']}")

        # Start coding section
        self.coding_section = CodingSectionWidget(self.student_id, self.student_name)
        self.coding_section.section_complete.connect(self._on_coding_complete)
        self.stack.addWidget(self.coding_section)
        self.stack.setCurrentWidget(self.coding_section)
        self._log_security("SECTION_START", "Coding section started")

    def _on_coding_complete(self, coding_result):
        self.coding_result = coding_result
        self._log_security("SECTION_COMPLETE", f"Coding: {coding_result['language']}")

        # Show review
        self.review_screen = ReviewScreen(
            self.student_id, self.student_name, self.mcq_result, self.coding_result
        )
        self.review_screen.confirmed.connect(self._submit_exam)
        self.review_screen.back_requested.connect(lambda: self.stack.setCurrentWidget(self.coding_section))
        self.stack.addWidget(self.review_screen)
        self.stack.setCurrentWidget(self.review_screen)

    def _submit_exam(self):
        exam_data = {
            "student_id": self.student_id,
            "student_name": self.student_name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "completed"
        }

        self._log_security("EXAM_SUBMIT", f"Final submission by {self.student_id}")

        self.results_screen = ResultsScreen(
            self.student_id, self.student_name,
            self.mcq_result, self.coding_result, exam_data
        )
        self.stack.addWidget(self.results_screen)
        self.stack.setCurrentWidget(self.results_screen)

    def keyPressEvent(self, event):
        key = event.key()

        # Block Alt+Tab, Alt+F4, Escape (with warning), Super
        if event.modifiers() == Qt.KeyboardModifier.AltModifier and key in (
            Qt.Key.Key_Tab, Qt.Key.Key_F4, Qt.Key.Key_Left, Qt.Key.Key_Right
        ):
            self._log_security("BLOCKED_KEY", f"Alt+{event.text()}")
            event.ignore()
            return

        if key == Qt.Key.Key_Escape:
            self._log_security("BLOCKED_KEY", "Escape pressed")
            self._show_exit_warning()
            event.ignore()
            return

        if key == Qt.Key.Key_Super_L or key == Qt.Key.Key_Super_R:
            self._log_security("BLOCKED_KEY", "Super/Windows key")
            event.ignore()
            return

        if key == Qt.Key.Key_F11:
            event.ignore()
            return

        super().keyPressEvent(event)

    def _show_exit_warning(self):
        reply = QMessageBox.warning(
            self,
            "⚠ Exit Warning",
            "You are attempting to exit the examination environment.\n\n"
            "This action will be logged. Are you sure you want to exit?\n\n"
            "Note: Your progress has been auto-saved.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._log_security("EXIT_ATTEMPT", "User confirmed exit")
            QApplication.quit()

    def closeEvent(self, event):
        self._log_security("CLOSE_ATTEMPT", "Window close attempted")
        reply = QMessageBox.warning(
            self,
            "⚠ Exit Warning",
            "You are attempting to exit the examination environment.\n\n"
            "This action will be logged. Are you sure you want to exit?\n\n"
            "Note: Your progress has been auto-saved.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._log_security("EXIT_ATTEMPT", "User confirmed exit")
            event.accept()
        else:
            event.ignore()


class AntiCheatFilter(QWidget):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            mods = event.modifiers()

            # Allow Ctrl+C/V/X/A in text editors (coding section)
            if isinstance(obj, QTextEdit) and mods == Qt.KeyboardModifier.ControlModifier:
                return super().eventFilter(obj, event)

            # Block copy/paste shortcuts elsewhere
            if mods == Qt.KeyboardModifier.ControlModifier and key in (
                Qt.Key.Key_C, Qt.Key.Key_V, Qt.Key.Key_X, Qt.Key.Key_A
            ):
                self.logger.log("BLOCKED_SHORTCUT", f"Ctrl+{chr(key).upper()}")
                return True

            # Block Alt+Tab system-wide
            if mods == Qt.KeyboardModifier.AltModifier and key == Qt.Key.Key_Tab:
                self.logger.log("BLOCKED_SHORTCUT", "Alt+Tab")
                return True

            # Block Alt+F4
            if mods == Qt.KeyboardModifier.AltModifier and key == Qt.Key.Key_F4:
                self.logger.log("BLOCKED_SHORTCUT", "Alt+F4")
                return True

            # Block Print Screen
            if key == Qt.Key.Key_Print:
                self.logger.log("BLOCKED_SHORTCUT", "Print Screen")
                return True

        return super().eventFilter(obj, event)


def main():
    # Ensure results directory
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    app = QApplication(sys.argv)
    app.setApplicationName("EduOS Demo Exam")
    app.setOrganizationName("EduOS")

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    window = DemoExamWindow()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
