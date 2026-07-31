#!/usr/bin/env python3
"""
EduOS Exam Mode - Secure Examination Application
Full-screen PyQt6 exam environment with timer, auto-save, auto-submit,
security key authentication, and encrypted local storage.
"""

import sys
import os
import json
import base64
import hashlib
import signal
import stat
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QRadioButton,
    QButtonGroup,
    QMessageBox,
    QProgressBar,
    QScrollArea,
    QFrame,
    QStackedWidget,
    QCheckBox,
    QGroupBox,
    QGridLayout,
    QFileDialog,
    QDialog,
    QDialogButtonBox,
    QListWidget,
    QListWidgetItem,
    QTabWidget,
    QSplitter,
    QComboBox,
    QSpinBox,
    QTimeEdit,
)
from PyQt6.QtCore import Qt, QTimer, QObject, QEvent, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import (
    QFont,
    QPalette,
    QColor,
    QIcon,
    QAction,
    QKeySequence,
    QPixmap,
    QShortcut,
)
from design_system import (
    EduOSColors as C,
    apply_glass_theme,
    glass_card_style,
    glass_button_style,
    accent_glow_style,
    glass_success_button_style,
    glass_danger_button_style,
    glass_warning_button_style,
    status_badge_style,
    StatusBadge,
    SectionTitle,
    glass_stat_card_style,
    glass_banner_style,
)
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


EXAM_DATA_DIR = Path.home() / ".eduos" / "exam"
EXAM_DATA_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_FILE = EXAM_DATA_DIR / "config.json"
EXAMS_DIR = EXAM_DATA_DIR / "exams"
EXAMS_DIR.mkdir(exist_ok=True)
RESULTS_DIR = EXAM_DATA_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)
try:
    # Vulnerability 4 — restrict to owner only: no group/other access
    RESULTS_DIR.chmod(stat.S_IRWXU)
except OSError:
    pass
KEYS_DIR = EXAM_DATA_DIR / "keys"
KEYS_DIR.mkdir(exist_ok=True)


def get_fernet_from_password(password: str, salt: bytes = None) -> tuple:
    if salt is None:
        salt = os.urandom(16)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480000)
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return Fernet(key), salt


class ExamKeyFilter(QObject):
    """Global key filter — consumes blocked keys before any widget sees them."""

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            blocked = [
                Qt.Key.Key_Super_L,
                Qt.Key.Key_Super_R,
                Qt.Key.Key_Tab,
                Qt.Key.Key_Escape,
                Qt.Key.Key_F1,
                Qt.Key.Key_F2,
                Qt.Key.Key_F3,
                Qt.Key.Key_F4,
                Qt.Key.Key_F11,
                Qt.Key.Key_Print,
                Qt.Key.Key_SysReq,
            ]
            if event.key() in blocked:
                return True
        return False


class SecurityKeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("EduOS Exam - Security Key")
        self.setFixedSize(450, 300)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        title = QLabel("🔐 Exam Security Authentication")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {C.ACCENT_PRIMARY};"
        )
        layout.addWidget(title)

        desc = QLabel(
            "Enter your exam security key to begin the examination.\nContact your invigilator if you don't have a key."
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet(f"font-size: 13px; color: {C.TEXT_SECONDARY};")
        layout.addWidget(desc)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Enter security key (e.g. EXAM-XXXX-XXXX)")
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 12px; font-size: 16px; border: 2px solid {C.ACCENT_PRIMARY};
                border-radius: 8px; letter-spacing: 3px;
                background: {C.GLASS_CARD}; color: {C.TEXT_PRIMARY};
            }}
        """)
        layout.addWidget(self.key_input)

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Your Full Name")
        self.student_name.setStyleSheet(
            f"padding: 10px; font-size: 14px; border: 1px solid {C.GLASS_BORDER}; border-radius: 6px; background: {C.GLASS_CARD}; color: {C.TEXT_PRIMARY};"
        )
        layout.addWidget(self.student_name)

        self.student_id = QLineEdit()
        self.student_id.setPlaceholderText("Student ID / Roll Number")
        self.student_id.setStyleSheet(
            f"padding: 10px; font-size: 14px; border: 1px solid {C.GLASS_BORDER}; border-radius: 6px; background: {C.GLASS_CARD}; color: {C.TEXT_PRIMARY};"
        )
        layout.addWidget(self.student_id)

        btn_layout = QHBoxLayout()
        self.auth_btn = QPushButton("🔑 Authenticate & Start Exam")
        self.auth_btn.setStyleSheet(accent_glow_style())
        self.auth_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.auth_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(glass_button_style())
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.key_input.returnPressed.connect(self.auth_btn.click)
        self.student_name.returnPressed.connect(self.auth_btn.click)

    def get_credentials(self):
        return {
            "key": self.key_input.text().strip(),
            "name": self.student_name.text().strip(),
            "student_id": self.student_id.text().strip(),
        }


class QuestionWidget(QWidget):
    answer_changed = pyqtSignal()

    def __init__(self, question_data: dict, question_number: int):
        super().__init__()
        self.question_data = question_data
        self.question_number = question_number
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        q_label = QLabel(f"Q{self.question_number}. {self.question_data['question']}")
        q_label.setWordWrap(True)
        q_label.setStyleSheet(
            f"font-size: 16px; font-weight: bold; padding: 10px; background: {C.GLASS_CARD}; border-radius: 8px; color: {C.TEXT_PRIMARY};"
        )
        layout.addWidget(q_label)

        qtype = self.question_data.get("type", "mcq")

        if qtype == "mcq":
            self.answer_group = QButtonGroup(self)
            options = self.question_data.get("options", [])
            for i, opt in enumerate(options):
                rb = QRadioButton(opt)
                rb.setStyleSheet(f"""
                    QRadioButton {{
                        padding: 10px 15px; font-size: 14px; border: 1px solid {C.GLASS_BORDER};
                        border-radius: 6px; margin: 4px 0; color: {C.TEXT_PRIMARY};
                        background: {C.GLASS_CARD};
                    }}
                    QRadioButton:hover {{ background: rgba(108, 99, 255, 0.1); border-color: {C.ACCENT_PRIMARY}; }}
                    QRadioButton::indicator {{ width: 18px; height: 18px; }}
                """)
                self.answer_group.addButton(rb, i)
                self.answer_group.buttonClicked.connect(
                    lambda: self.answer_changed.emit()
                )
                layout.addWidget(rb)
        elif qtype == "multiple_select":
            self.checkboxes = []
            for i, opt in enumerate(self.question_data.get("options", [])):
                cb = QCheckBox(opt)
                cb.setStyleSheet(f"""
                    QCheckBox {{
                        padding: 10px 15px; font-size: 14px; border: 1px solid {C.GLASS_BORDER};
                        border-radius: 6px; margin: 4px 0; color: {C.TEXT_PRIMARY};
                        background: {C.GLASS_CARD};
                    }}
                    QCheckBox:hover {{ background: rgba(108, 99, 255, 0.1); border-color: {C.ACCENT_PRIMARY}; }}
                    QCheckBox::indicator {{ width: 18px; height: 18px; }}
                """)
                cb.stateChanged.connect(lambda: self.answer_changed.emit())
                self.checkboxes.append(cb)
                layout.addWidget(cb)
        elif qtype == "programming":
            self.code_edit = QTextEdit()
            self.code_edit.setPlaceholderText("Write your code here...")
            self.code_edit.setStyleSheet(f"""
                QTextEdit {{
                    font-family: 'Fira Code', 'Consolas', monospace;
                    font-size: 13px; padding: 10px;
                    border: 1px solid {C.GLASS_BORDER}; border-radius: 6px;
                    background: #1e1e2e; color: #cdd6f4;
                }}
            """)
            self.code_edit.setMinimumHeight(250)
            self.code_edit.textChanged.connect(lambda: self.answer_changed.emit())
            layout.addWidget(self.code_edit)

            if self.question_data.get("language"):
                lang_label = QLabel(f"Language: {self.question_data['language']}")
                lang_label.setStyleSheet(
                    f"font-size: 12px; color: {C.TEXT_SECONDARY}; padding: 4px 0;"
                )
                layout.addWidget(lang_label)

            if self.question_data.get("starter_code"):
                starter = QLabel("Starter Code:")
                starter.setStyleSheet("font-weight: bold; color: #555;")
                layout.addWidget(starter)
                starter_edit = QTextEdit()
                starter_edit.setPlainText(self.question_data["starter_code"])
                starter_edit.setReadOnly(True)
                starter_edit.setMaximumHeight(150)
                starter_edit.setStyleSheet(
                    f"font-family: monospace; font-size: 12px; background: {C.GLASS_CARD}; border: 1px solid {C.GLASS_BORDER}; border-radius: 4px; padding: 8px; color: {C.TEXT_PRIMARY};"
                )
                layout.addWidget(starter_edit)
        elif qtype == "practical":
            self.practical_edit = QTextEdit()
            self.practical_edit.setPlaceholderText(
                "Describe your approach and solution..."
            )
            self.practical_edit.setStyleSheet(f"""
                QTextEdit {{
                    font-size: 14px; padding: 10px;
                    border: 1px solid {C.GLASS_BORDER}; border-radius: 6px;
                    background: {C.GLASS_CARD}; color: {C.TEXT_PRIMARY};
                }}
            """)
            self.practical_edit.setMinimumHeight(200)
            self.practical_edit.textChanged.connect(lambda: self.answer_changed.emit())
            layout.addWidget(self.practical_edit)
        elif qtype == "short_answer":
            self.short_answer = QTextEdit()
            self.short_answer.setPlaceholderText("Type your answer here...")
            self.short_answer.setMaximumHeight(120)
            self.short_answer.setStyleSheet(
                f"font-size: 14px; padding: 10px; border: 1px solid {C.GLASS_BORDER}; border-radius: 6px; background: {C.GLASS_CARD}; color: {C.TEXT_PRIMARY};"
            )
            self.short_answer.textChanged.connect(lambda: self.answer_changed.emit())
            layout.addWidget(self.short_answer)

        layout.addStretch()
        self.setStyleSheet(
            f"background: {C.GLASS_CARD}; border-radius: 10px; padding: 10px;"
        )

    def get_answer(self):
        qtype = self.question_data.get("type", "mcq")
        if qtype == "mcq":
            btn = self.answer_group.checkedButton()
            return btn.text() if btn else ""
        elif qtype == "multiple_select":
            return [cb.text() for cb in self.checkboxes if cb.isChecked()]
        elif qtype == "programming":
            return self.code_edit.toPlainText()
        elif qtype == "practical":
            return self.practical_edit.toPlainText()
        elif qtype == "short_answer":
            return self.short_answer.toPlainText()
        return ""

    def set_answer(self, answer):
        qtype = self.question_data.get("type", "mcq")
        if qtype == "mcq":
            for i, opt in enumerate(self.question_data.get("options", [])):
                if opt == answer:
                    btn = self.answer_group.button(i)
                    if btn:
                        btn.setChecked(True)
                    break
        elif qtype == "multiple_select" and isinstance(answer, list):
            for cb in self.checkboxes:
                if cb.text() in answer:
                    cb.setChecked(True)
        elif qtype == "programming" and hasattr(self, "code_edit"):
            self.code_edit.setPlainText(answer)
        elif qtype == "practical" and hasattr(self, "practical_edit"):
            self.practical_edit.setPlainText(answer)
        elif qtype == "short_answer" and hasattr(self, "short_answer"):
            self.short_answer.setPlainText(answer)


class ExamTimer(QWidget):
    timeout = pyqtSignal()
    tick = pyqtSignal(int)

    def __init__(self, duration_minutes: int):
        super().__init__()
        self.total_seconds = duration_minutes * 60
        self.remaining_seconds = self.total_seconds
        self.running = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.time_label = QLabel(self._format_time())
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet(f"""
            font-size: 28px; font-weight: bold; font-family: monospace;
            padding: 8px 16px; border-radius: 8px;
            background: {C.BG_MID}; color: {C.ACCENT_SECONDARY};
        """)
        layout.addWidget(self.time_label)

        self.progress = QProgressBar()
        self.progress.setMaximum(self.total_seconds)
        self.progress.setValue(self.total_seconds)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
        self.progress.setStyleSheet(f"""
            QProgressBar {{ background: rgba(255,255,255,0.06); border: none; border-radius: 3px; }}
            QProgressBar::chunk {{ background: {C.ACCENT_PRIMARY}; border-radius: 3px; }}
        """)
        layout.addWidget(self.progress)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)

    def _format_time(self):
        m, s = divmod(self.remaining_seconds, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

    def _tick(self):
        self.remaining_seconds -= 1
        self.time_label.setText(self._format_time())
        self.progress.setValue(self.remaining_seconds)
        self.tick.emit(self.remaining_seconds)

        if self.remaining_seconds <= 300:
            self.time_label.setStyleSheet(f"""
                font-size: 28px; font-weight: bold; font-family: monospace;
                padding: 8px 16px; border-radius: 8px;
                background: {C.BG_MID}; color: {C.ACCENT_RED};
            """)

        if self.remaining_seconds <= 0:
            self.stop()
            self.timeout.emit()

    def start(self):
        self.running = True
        self.timer.start(1000)

    def stop(self):
        self.running = False
        self.timer.stop()

    def get_elapsed(self):
        return self.total_seconds - self.remaining_seconds

    def get_remaining(self):
        return self.remaining_seconds


class ExamWindow(QMainWindow):
    def __init__(self, exam_config: dict, credentials: dict):
        super().__init__()
        self.exam_config = exam_config
        self.credentials = credentials
        self.answers = {}
        self.question_widgets = []
        self.is_submitted = False
        self._setup_restrictions()
        self._setup_ui()

    def _setup_restrictions(self):
        # Vulnerability 1 — block kill signals during exam.
        # Note: SIGKILL (kill -9) cannot be blocked — handled by systemd
        # exam lock service (eduos-exam-lock).
        signal.signal(signal.SIGTERM, lambda s, f: None)
        signal.signal(signal.SIGHUP, lambda s, f: None)

        # Vulnerability 2 — global keyboard filter blocks Alt+Tab,
        # Super, Escape, F1-F4 (Alt+F4), Print, etc.
        self.key_filter = ExamKeyFilter()
        QApplication.instance().installEventFilter(self.key_filter)

        # Vulnerability 3 — clear and keep clearing the clipboard
        # so students cannot paste answers.
        self.clipboard_timer = QTimer(self)
        self.clipboard_timer.timeout.connect(
            lambda: QApplication.clipboard().clear()
        )
        QApplication.clipboard().clear()
        self.clipboard_timer.start(5000)

        try:
            subprocess.run(
                ["xdotool", "key", "--clearmodifiers", "Super_L"], capture_output=True
            )
            for key in ["Print", "Alt+Print", "Shift+Print"]:
                shortcut = QShortcut(QKeySequence(key), self)
                shortcut.activated.connect(lambda: None)
        except Exception:
            pass

        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.showFullScreen()
        self.setCursor(Qt.CursorShape.BlankCursor)

        # Vulnerability 5 — isolate network during exam (LAN kept for
        # submission). Best-effort: requires root/ufw on the student PC.
        self.enable_exam_network_isolation()

    def enable_exam_network_isolation(self):
        """Block internet but keep LAN for submission."""
        try:
            subprocess.run(
                [
                    "ufw", "deny", "out", "to", "any",
                    "port", "80,443", "proto", "tcp",
                ],
                check=True, capture_output=True, timeout=10,
            )
        except Exception as e:
            print(f"Network isolation failed: {e}")

    def _setup_ui(self):
        self.setWindowTitle("EduOS Exam Mode - Secure Assessment")
        self.setStyleSheet(f"background: {C.BG_DARK};")

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 10, 20, 10)
        main_layout.setSpacing(10)

        header = QWidget()
        header.setStyleSheet(
            f"background: {C.BG_MID}; border-radius: 12px; padding: 8px;"
        )
        header_layout = QHBoxLayout(header)

        info = QLabel(f"📝 {self.exam_config.get('title', 'Examination')}")
        info.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {C.TEXT_PRIMARY};"
        )
        header_layout.addWidget(info)

        header_layout.addStretch()

        student_info = QLabel(
            f"{self.credentials.get('name', 'Student')} | {self.credentials.get('student_id', '')}"
        )
        student_info.setStyleSheet(f"font-size: 13px; color: {C.TEXT_MUTED};")
        header_layout.addWidget(student_info)

        header_layout.addSpacing(20)

        duration = self.exam_config.get("duration_minutes", 60)
        self.timer_widget = ExamTimer(duration)
        header_layout.addWidget(self.timer_widget)
        self.timer_widget.timeout.connect(self.auto_submit)
        self.timer_widget.tick.connect(self.auto_save)

        main_layout.addWidget(header)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 5, 0, 0)

        self.question_list = QListWidget()
        self.question_list.setFixedWidth(200)
        self.question_list.setStyleSheet(f"""
            QListWidget {{
                background: {C.BG_MID}; border: none; border-radius: 8px;
                padding: 8px; font-size: 13px; color: {C.TEXT_PRIMARY};
            }}
            QListWidget::item {{
                padding: 10px; border-radius: 6px; margin: 2px 0;
            }}
            QListWidget::item:selected {{
                background: {C.ACCENT_PRIMARY}; color: white;
            }}
            QListWidget::item:hover {{
                background: {C.BG_LIGHT};
            }}
        """)
        self.question_list.currentRowChanged.connect(self._show_question)
        content_layout.addWidget(self.question_list)

        self.question_stack = QStackedWidget()
        self.question_stack.setStyleSheet("background: transparent;")
        content_layout.addWidget(self.question_stack, 1)

        main_layout.addWidget(content, 1)

        footer = QWidget()
        footer.setStyleSheet(
            f"background: {C.BG_MID}; border-radius: 12px; padding: 8px;"
        )
        footer_layout = QHBoxLayout(footer)

        self.save_status = QLabel("💾 Auto-save enabled")
        self.save_status.setStyleSheet(f"font-size: 13px; color: {C.TEXT_MUTED};")
        footer_layout.addWidget(self.save_status)

        footer_layout.addStretch()

        questions_count = len(self.exam_config.get("questions", []))
        self.progress_label = QLabel(f"Progress: 0 / {questions_count}")
        self.progress_label.setStyleSheet(f"font-size: 13px; color: {C.TEXT_MUTED};")
        footer_layout.addWidget(self.progress_label)

        footer_layout.addSpacing(20)

        self.submit_btn = QPushButton("📤 Submit Exam")
        self.submit_btn.setStyleSheet(glass_danger_button_style())
        self.submit_btn.clicked.connect(self.confirm_submit)
        footer_layout.addWidget(self.submit_btn)

        main_layout.addWidget(footer)

        self._load_questions()

    def _load_questions(self):
        questions = self.exam_config.get("questions", [])
        self.question_stack.clear()
        self.question_list.clear()

        for i, qdata in enumerate(questions, 1):
            qw = QuestionWidget(qdata, i)
            self.question_widgets.append(qw)
            self.question_stack.addWidget(qw)

            item = QListWidgetItem(f"  Question {i}")
            if qdata.get("type") == "programming":
                item.setText(f"  💻 Q{i}")
            elif qdata.get("type") == "practical":
                item.setText(f"  🔬 Q{i}")
            elif qdata.get("type") == "multiple_select":
                item.setText(f"  ☑ Q{i}")
            self.question_list.addItem(item)

            qw.answer_changed.connect(self._update_progress)

        if self.question_widgets:
            self.question_list.setCurrentRow(0)

        self._update_progress()

    def _show_question(self, index: int):
        if 0 <= index < self.question_stack.count():
            self.question_stack.setCurrentIndex(index)

    def _update_progress(self):
        answered = sum(1 for qw in self.question_widgets if qw.get_answer())
        total = len(self.question_widgets)
        self.progress_label.setText(f"Answered: {answered} / {total}")

    def auto_save(self, remaining_seconds: int):
        if remaining_seconds % 30 == 0:
            self._save_answers_backup()

    def _save_answers_backup(self):
        backup = {}
        for i, qw in enumerate(self.question_widgets):
            answer = qw.get_answer()
            if answer:
                backup[f"q{i}"] = answer

        if backup:
            backup_path = (
                EXAM_DATA_DIR / f"autosave_{self.credentials['student_id']}.json"
            )
            try:
                with open(backup_path, "w") as f:
                    json.dump(backup, f)
                self.save_status.setText("💾 Auto-saved")
            except Exception:
                self.save_status.setText("⚠ Save failed")

    def _collect_answers(self) -> dict:
        answers = {}
        for i, qw in enumerate(self.question_widgets):
            answers[f"question_{i + 1}"] = {
                "question": qw.question_data["question"],
                "answer": qw.get_answer(),
                "type": qw.question_data.get("type", "mcq"),
            }
        return answers

    def confirm_submit(self):
        unanswered = sum(1 for qw in self.question_widgets if not qw.get_answer())
        msg = "Are you sure you want to submit your exam?"
        if unanswered > 0:
            msg = f"⚠ {unanswered} question(s) unanswered. {msg}"

        reply = QMessageBox.question(
            self,
            "Submit Exam",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.final_submit()

    def auto_submit(self):
        self.is_submitted = True
        QMessageBox.information(
            self,
            "Time Up",
            "Your time is up! The exam will be submitted automatically.",
        )
        self.final_submit()

    def final_submit(self):
        if self.is_submitted:
            return
        self.is_submitted = True
        self.timer_widget.stop()
        self.submit_btn.setEnabled(False)

        answers = self._collect_answers()
        self._encrypt_and_save(answers)
        self._generate_result(answers)
        self._show_completion()

    def _encrypt_and_save(self, answers: dict):
        password = self.exam_config.get(
            "encryption_key", os.environ.get("EDUOS_EXAM_KEY", "eduos-exam-default-key")
        )
        fernet, salt = get_fernet_from_password(password)

        data = {
            "exam": self.exam_config.get("title", "Exam"),
            "student": self.credentials,
            "answers": answers,
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": self.timer_widget.get_elapsed(),
        }

        encrypted = fernet.encrypt(json.dumps(data).encode())

        filename = f"{self.credentials['student_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.enc"
        filepath = RESULTS_DIR / filename
        with open(filepath, "wb") as f:
            f.write(salt + encrypted)

        self.save_status.setText(f"✅ Encrypted submission saved: {filename}")

    def _generate_result(self, answers: dict):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import (
                SimpleDocTemplate,
                Paragraph,
                Spacer,
                Table,
                TableStyle,
            )
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.units import inch

            filename = f"{self.credentials['student_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_result.pdf"
            filepath = RESULTS_DIR / filename

            doc = SimpleDocTemplate(str(filepath), pagesize=A4)
            styles = getSampleStyleSheet()
            elements = []

            elements.append(Paragraph(f"EduOS Examination Result", styles["Title"]))
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(
                Paragraph(
                    f"Student: {self.credentials.get('name', 'N/A')}", styles["Normal"]
                )
            )
            elements.append(
                Paragraph(
                    f"ID: {self.credentials.get('student_id', 'N/A')}", styles["Normal"]
                )
            )
            elements.append(
                Paragraph(
                    f"Exam: {self.exam_config.get('title', 'N/A')}", styles["Normal"]
                )
            )
            elements.append(
                Paragraph(
                    f"Date: {datetime.now().strftime('%B %d, %Y %H:%M')}",
                    styles["Normal"],
                )
            )
            elements.append(Spacer(1, 0.3 * inch))

            for q_key, q_data in answers.items():
                q_text = q_data.get("question", "")
                q_answer = q_data.get("answer", "")
                if isinstance(q_answer, list):
                    q_answer = ", ".join(q_answer)
                elements.append(
                    Paragraph(f"<b>{q_key}:</b> {q_text}", styles["Normal"])
                )
                elements.append(
                    Paragraph(f"<i>Answer:</i> {q_answer}", styles["Normal"])
                )
                elements.append(Spacer(1, 0.1 * inch))

            doc.build(elements)
        except ImportError:
            with open(
                RESULTS_DIR / f"{self.credentials['student_id']}_result.txt", "w"
            ) as f:
                f.write(f"Exam Result\n{'=' * 40}\n")
                f.write(f"Student: {self.credentials.get('name', 'N/A')}\n")
                f.write(f"ID: {self.credentials.get('student_id', 'N/A')}\n")
                f.write(f"Date: {datetime.now().isoformat()}\n\n")
                for q_key, q_data in answers.items():
                    f.write(f"{q_key}: {q_data.get('question', '')}\n")
                    f.write(f"Answer: {q_data.get('answer', '')}\n\n")

    def _show_completion(self):
        QMessageBox.information(
            self,
            "Exam Submitted",
            "Your exam has been submitted successfully.\n\n"
            "You may now close this window and return to the desktop.\n"
            "Your answers have been encrypted and saved locally.",
        )

    def keyPressEvent(self, event):
        if event.key() in [
            Qt.Key.Key_Escape,
            Qt.Key.Key_Super_L,
            Qt.Key.Key_Super_R,
            Qt.Key.Key_Alt,
            Qt.Key.Key_Tab,
            Qt.Key.Key_F11,
            Qt.Key.Key_Print,
            Qt.Key.Key_SysReq,
        ]:
            event.ignore()
            return
        super().keyPressEvent(event)

    def closeEvent(self, event):
        self.timer_widget.stop()
        if hasattr(self, "clipboard_timer"):
            self.clipboard_timer.stop()
        event.accept()


def load_exam_config(exam_file: str) -> dict:
    path = Path(exam_file)
    if not path.exists():
        raise FileNotFoundError(f"Exam file not found: {exam_file}")

    if path.suffix == ".json":
        with open(path) as f:
            return json.load(f)
    elif path.suffix == ".enc":
        password = os.environ.get("EDUOS_EXAM_KEY", "eduos-exam-default-key")
        with open(path, "rb") as f:
            salt = f.read(16)
            encrypted = f.read()
        fernet, _ = get_fernet_from_password(password, salt)
        decrypted = fernet.decrypt(encrypted)
        return json.loads(decrypted)
    raise ValueError(f"Unknown exam file format: {path.suffix}")


def create_sample_exam():
    exam = {
        "title": "Sample Mid-Term Examination",
        "subject": "Computer Science Fundamentals",
        "duration_minutes": 30,
        "encryption_key": os.environ.get("EDUOS_EXAM_KEY", "eduos-exam-default-key"),
        "instructions": "Answer all questions. Each question carries equal marks.",
        "questions": [
            {
                "type": "mcq",
                "question": "What is the time complexity of binary search?",
                "options": ["O(n)", "O(log n)", "O(n²)", "O(1)"],
                "correct": "O(log n)",
            },
            {
                "type": "mcq",
                "question": "Which data structure uses LIFO principle?",
                "options": ["Queue", "Stack", "Tree", "Graph"],
                "correct": "Stack",
            },
            {
                "type": "multiple_select",
                "question": "Which of the following are programming paradigms?",
                "options": ["Object-Oriented", "Functional", "Procedural", "Linear"],
            },
            {
                "type": "programming",
                "question": "Write a Python function to check if a string is a palindrome.",
                "language": "Python",
                "starter_code": "def is_palindrome(s):\n    # Your code here\n    pass",
            },
            {
                "type": "short_answer",
                "question": "What is the difference between TCP and UDP?",
            },
            {
                "type": "practical",
                "question": "Design a simple REST API endpoint for a library management system. Describe the endpoint, HTTP methods, request/response format, and authentication approach.",
            },
        ],
    }

    sample_path = EXAMS_DIR / "sample_exam.json"
    with open(sample_path, "w") as f:
        json.dump(exam, f, indent=2)
    return str(sample_path)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    apply_glass_theme(app)

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(C.BG_DARK))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(C.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Base, QColor(C.BG_MID))
    palette.setColor(QPalette.ColorRole.Text, QColor(C.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Button, QColor(C.BG_MID))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(C.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(C.ACCENT_PRIMARY))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)

    auth = SecurityKeyDialog()
    if auth.exec() != QDialog.DialogCode.Accepted:
        sys.exit(0)

    credentials = auth.get_credentials()
    if not credentials["key"] or not credentials["name"]:
        QMessageBox.critical(
            None, "Error", "Security key and student name are required."
        )
        sys.exit(1)

    key_hash = hashlib.sha256(credentials["key"].encode()).hexdigest()

    exam_file = EXAMS_DIR / "sample_exam.json"
    if not exam_file.exists():
        create_sample_exam()

    try:
        exam_config = load_exam_config(str(exam_file))
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to load exam: {e}")
        sys.exit(1)

    window = ExamWindow(exam_config, credentials)
    window.show()
    window.timer_widget.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
