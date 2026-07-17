import sys
import json
import os
import time
import threading
from urllib.request import Request, urlopen
from urllib.error import URLError

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
    QMessageBox,
    QTextEdit,
    QRadioButton,
    QButtonGroup,
    QGroupBox,
    QProgressBar,
    QStatusBar,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QKeySequence

from mcq_engine import MCQEngine
from coding_engine import CodingEngine
from exam_engine import ExamEngine
from exam_lockdown import ExamLockdown

CONFIG_PATH = "/etc/edos/exam-config.json"

DARK_STYLE = """
QMainWindow, QWidget { background-color: #1a1a2e; color: #e0e0e0; }
QPushButton {
    background-color: #0d7377; color: #ffffff; border: none;
    padding: 10px 20px; border-radius: 6px; font-size: 14px;
}
QPushButton:hover { background-color: #14a3a8; }
QPushButton:pressed { background-color: #095557; }
QPushButton#submitBtn {
    background-color: #c0392b;
}
QPushButton#submitBtn:hover { background-color: #e74c3c; }
QListWidget {
    background-color: #16213e; color: #e0e0e0; border: 1px solid #0f3460;
    border-radius: 6px; padding: 5px; font-size: 13px;
}
QListWidget::item:selected { background-color: #0d7377; }
QLabel { color: #e0e0e0; }
QGroupBox {
    border: 1px solid #0f3460; border-radius: 8px; margin-top: 10px;
    padding-top: 10px; color: #00d4ff; font-weight: bold;
}
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
QRadioButton { color: #e0e0e0; spacing: 8px; font-size: 14px; }
QTextEdit {
    background-color: #16213e; color: #e0e0e0; border: 1px solid #0f3460;
    border-radius: 6px; padding: 8px; font-family: "Consolas","Courier New",monospace;
    font-size: 13px;
}
QProgressBar {
    border: 1px solid #0f3460; border-radius: 6px; text-align: center;
    background-color: #16213e; color: #e0e0e0; height: 22px;
}
QProgressBar::chunk { background-color: #0d7377; border-radius: 6px; }
QStatusBar { background-color: #0f3460; color: #e0e0e0; }
QProgressBar#timerBar { height: 18px; }
QProgressBar#timerBar::chunk { background-color: #27ae60; }
QProgressBar#timerBar::chunk:critical { background-color: #c0392b; }
"""


class MCQWidget(QWidget):
    def __init__(self, qid, text, options):
        super().__init__()
        self.qid = qid
        layout = QVBoxLayout(self)
        qlabel = QLabel(text)
        qlabel.setWordWrap(True)
        qlabel.setStyleSheet("font-size: 16px; padding: 10px;")
        self.group = QButtonGroup(self)
        self.buttons = []
        for i, opt in enumerate(options):
            rb = QRadioButton(opt)
            self.group.addButton(rb, i)
            self.buttons.append(rb)
            layout.addWidget(rb)
        layout.addStretch()

    def get_answer(self):
        btn = self.group.checkedButton()
        return self.buttons.index(btn) if btn else -1

    def set_answer(self, answer):
        if isinstance(answer, int) and 0 <= answer < len(self.buttons):
            self.buttons[answer].setChecked(True)


class CodingWidget(QWidget):
    def __init__(self, qid, title, description):
        super().__init__()
        self.qid = qid
        layout = QVBoxLayout(self)
        tlabel = QLabel(title)
        tlabel.setStyleSheet("font-size: 16px; padding: 10px;")
        dlabel = QLabel(description)
        dlabel.setWordWrap(True)
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Write your code here...")
        layout.addWidget(tlabel)
        layout.addWidget(dlabel)
        layout.addWidget(QLabel("Solution:"))
        layout.addWidget(self.editor)

    def get_answer(self):
        return self.editor.toPlainText()

    def set_answer(self, answer):
        if isinstance(answer, str):
            self.editor.setPlainText(answer)


class ExamWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.server_url = config.get("server_url", "http://localhost:8000")
        self.exam_id = config.get("exam_id", 1)
        self.auth_token = config.get("auth_token", "")

        self.exam_engine = ExamEngine()
        self.mcq_engine = MCQEngine()
        self.coding_engine = CodingEngine()
        self.lockdown = ExamLockdown()

        self.questions = []
        self.question_widgets = []
        self.current_q = -1
        self.results = {}
        self.exam_data = None
        self.remaining_seconds = 0
        self.start_time = None

        self.setWindowTitle("EduOS Secure Exam")
        self.resize(1100, 750)
        self.setStyleSheet(DARK_STYLE)
        self.init_ui()
        self.load_exam()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        header_layout = QHBoxLayout()
        self.header = QLabel("EduOS Secure Exam")
        self.header.setStyleSheet("font-size: 26px; padding: 10px; color: #00d4ff;")
        self.timer_label = QLabel("--:--")
        self.timer_label.setStyleSheet(
            "font-size: 20px; padding: 10px; color: #e0e0e0;"
        )
        self.timer_label.setAlignment(Qt.AlignRight)
        header_layout.addWidget(self.header)
        header_layout.addStretch()
        header_layout.addWidget(self.timer_label)

        self.progress = QProgressBar()
        self.progress.setTextVisible(True)

        self.timer_bar = QProgressBar()
        self.timer_bar.setObjectName("timerBar")
        self.timer_bar.setTextVisible(False)
        self.timer_bar.setMaximumHeight(10)

        self.question_list = QListWidget()
        self.question_list.setMaximumWidth(200)
        self.question_list.currentRowChanged.connect(self.on_question_select)

        self.stack = QStackedWidget()

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.question_list)
        top_layout.addWidget(self.stack)

        btn_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.prev_question)
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.next_question)
        self.submit_btn = QPushButton("Submit Exam")
        self.submit_btn.setObjectName("submitBtn")
        self.submit_btn.clicked.connect(self.submit_exam)

        btn_layout.addWidget(self.prev_btn)
        btn_layout.addWidget(self.next_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.submit_btn)

        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.timer_bar)
        main_layout.addWidget(self.progress)
        main_layout.addLayout(top_layout)
        main_layout.addLayout(btn_layout)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)

        self.lockdown_check = QTimer(self)
        self.lockdown_check.timeout.connect(self.check_lockdown)

    def load_exam(self):
        data = self._fetch_exam()
        if data is None:
            self.status.showMessage(
                "Failed to load exam from server, using local fallback"
            )
            data = self._fallback_exam()

        self.exam_data = data
        self.exam_engine.load_exam(data)
        self.exam_engine.start_exam(data.get("id", self.exam_id))
        questions = data.get("questions", [])

        self.questions = questions
        self.progress.setMaximum(len(questions) - 1)

        for i, q in enumerate(questions):
            qtype = q.get("type", "mcq")
            if qtype == "mcq":
                w = MCQWidget(i, q["text"], q.get("options", []))
                self.mcq_engine.add_question(
                    q["text"], q.get("options", []), q.get("answer")
                )
            else:
                w = CodingWidget(i, q.get("title", ""), q.get("text", ""))
            self.question_widgets.append(w)
            self.stack.addWidget(w)
            self.question_list.addItem(f"Q{i + 1}")

        duration = data.get("duration_min", 60)
        self.remaining_seconds = duration * 60
        self.timer_bar.setMaximum(self.remaining_seconds)
        self.timer_bar.setValue(self.remaining_seconds)
        self.start_time = time.time()
        self.timer.start(1000)
        self.update_timer_display()

        self.lockdown.activate()
        self.lockdown_check.start(30000)

        self.showFullScreen()
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.show()

        self.current_q = -1
        self.next_question()
        self.status.showMessage("Exam started. Lockdown mode active.")

    def _fetch_exam(self):
        url = f"{self.server_url}/api/exams/{self.exam_id}"
        req = Request(url)
        if self.auth_token:
            req.add_header("Authorization", f"Bearer {self.auth_token}")
        try:
            resp = urlopen(req, timeout=10)
            return json.loads(resp.read().decode())
        except Exception:
            return None

    def _fallback_exam(self):
        return {
            "id": 0,
            "name": "Practice Exam",
            "duration_min": 30,
            "questions": [
                {
                    "id": 0,
                    "type": "mcq",
                    "text": "What is 2+2?",
                    "options": ["3", "4", "5", "6"],
                    "answer": 1,
                },
                {
                    "id": 1,
                    "type": "mcq",
                    "text": "Which planet is known as Red Planet?",
                    "options": ["Venus", "Mars", "Jupiter", "Saturn"],
                    "answer": 1,
                },
                {
                    "id": 2,
                    "type": "coding",
                    "title": "Hello World",
                    "text": "Write a Python program that prints 'Hello, World!'",
                },
                {
                    "id": 3,
                    "type": "mcq",
                    "text": "What is the capital of France?",
                    "options": ["London", "Berlin", "Paris", "Madrid"],
                    "answer": 2,
                },
                {
                    "id": 4,
                    "type": "coding",
                    "title": "Factorial",
                    "text": "Write a function to calculate factorial of a number.",
                },
            ],
        }

    def tick(self):
        self.remaining_seconds -= 1
        self.update_timer_display()
        self.timer_bar.setValue(self.remaining_seconds)
        if self.remaining_seconds <= 300:
            self.timer_bar.setStyleSheet(
                "QProgressBar::chunk { background-color: #e67e22; }"
            )
        if self.remaining_seconds <= 60:
            self.timer_bar.setStyleSheet(
                "QProgressBar::chunk { background-color: #c0392b; }"
            )
        if self.remaining_seconds <= 0:
            self.timer.stop()
            QMessageBox.warning(
                self,
                "Time Up",
                "Your time is up! The exam will be submitted automatically.",
            )
            self.submit_exam(auto=True)

    def update_timer_display(self):
        m, s = divmod(self.remaining_seconds, 60)
        self.timer_label.setText(f"{m:02d}:{s:02d}")

    def check_lockdown(self):
        checks = self.lockdown.check_environment()
        issues = []
        if not checks.get("no_browser"):
            issues.append("browser detected")
        if not checks.get("no_terminal"):
            issues.append("terminal detected")
        if not checks.get("no_devtools"):
            issues.append("dev tools detected")
        if issues:
            self.status.showMessage(f"WARNING: {' and '.join(issues)}")
        else:
            self.status.showMessage("Lockdown OK")

    def keyPressEvent(self, event):
        key = event.key()
        mods = event.modifiers()
        if mods & Qt.AltModifier and key in (Qt.Key_F4, Qt.Key_Tab, Qt.Key_Escape):
            event.ignore()
            return
        if mods & Qt.ControlModifier and key == Qt.Key_W:
            event.ignore()
            return
        super().keyPressEvent(event)

    def changeEvent(self, event):
        if event.type() == event.ActivationChange and not self.isActiveWindow():
            self.status.showMessage("WARNING: Exam window lost focus!")
            self.raise_()
            self.activateWindow()
        super().changeEvent(event)

    def closeEvent(self, event):
        if self.lockdown.active:
            reply = QMessageBox.warning(
                self,
                "Exit Exam",
                "Are you sure you want to exit? The exam will be submitted.",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self.submit_exam(auto=True)
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def on_question_select(self, index):
        if index >= 0 and self.current_q != index:
            self.save_current()
            self.current_q = index
            self.stack.setCurrentIndex(index)
            self.progress.setValue(index)
            self.status.showMessage(f"Question {index + 1} of {len(self.questions)}")

    def next_question(self):
        if self.current_q < len(self.questions) - 1:
            idx = self.current_q + 1
            self.save_current()
            self.current_q = idx
            self.stack.setCurrentIndex(idx)
            self.question_list.setCurrentRow(idx)
            self.progress.setValue(idx)
            self.status.showMessage(f"Question {idx + 1} of {len(self.questions)}")

    def prev_question(self):
        if self.current_q > 0:
            idx = self.current_q - 1
            self.save_current()
            self.current_q = idx
            self.stack.setCurrentIndex(idx)
            self.question_list.setCurrentRow(idx)
            self.progress.setValue(idx)
            self.status.showMessage(f"Question {idx + 1} of {len(self.questions)}")

    def save_current(self):
        if 0 <= self.current_q < len(self.question_widgets):
            w = self.question_widgets[self.current_q]
            if hasattr(w, "get_answer"):
                answer = w.get_answer()
                self.results[self.current_q] = answer
                self.exam_engine.submit_answer(self.current_q, answer)

    def submit_exam(self, auto=False):
        self.save_current()
        if not auto:
            reply = QMessageBox.question(
                self,
                "Submit Exam",
                "Are you sure you want to submit your exam?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return

        self.timer.stop()
        self.lockdown.deactivate()

        correct = 0
        total = 0
        details = {}
        for i, q in enumerate(self.questions):
            qtype = q.get("type", "mcq")
            if qtype == "mcq":
                correct_answer = q.get("answer")
                given = self.results.get(i, -1)
                is_correct = correct_answer == given
                if is_correct:
                    correct += 1
                total += 1
                details[i] = {
                    "given": given,
                    "correct": correct_answer,
                    "passed": is_correct,
                }
            elif qtype == "coding":
                given = self.results.get(i, "")
                result = self.coding_engine.run_code(given)
                details[i] = {
                    "given": len(given),
                    "output": result.get("output", ""),
                    "error": result.get("error", ""),
                }

        score = correct
        total_mcq = total
        pct = (score / total_mcq * 100) if total_mcq > 0 else 0

        self._submit_to_server(score, total_mcq, details)

        self.status.showMessage(
            f"Exam submitted! Score: {score}/{total_mcq} ({pct:.0f}%)"
        )
        QMessageBox.information(
            self,
            "Exam Submitted",
            f"Your exam has been submitted.\n\nScore: {score}/{total_mcq} ({pct:.0f}%)\n\n"
            + ("Auto-submitted due to time limit." if auto else ""),
        )

        self.submit_btn.setEnabled(False)
        self.prev_btn.setEnabled(False)
        self.next_btn.setEnabled(False)

    def _submit_to_server(self, score, total, details):
        url = f"{self.server_url}/api/submissions"
        payload = json.dumps(
            {
                "exam_id": self.exam_id,
                "user_id": self.config.get("user_id", 1),
                "answers": {"score": score, "total": total, "details": details},
            }
        ).encode()
        req = Request(url, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        if self.auth_token:
            req.add_header("Authorization", f"Bearer {self.auth_token}")
        try:
            urlopen(req, timeout=10)
        except Exception:
            pass


def load_config():
    config = {
        "server_url": "http://localhost:8000",
        "exam_id": 1,
        "auth_token": "",
        "user_id": 1,
    }
    try:
        with open(CONFIG_PATH) as f:
            user_config = json.load(f)
            config.update(user_config)
    except Exception:
        pass
    return config


if __name__ == "__main__":
    config = load_config()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ExamWindow(config)
    sys.exit(app.exec_())
