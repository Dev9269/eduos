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
    QTextEdit,
    QTabWidget,
    QSplitter,
    QStatusBar,
    QComboBox,
    QMessageBox,
    QTreeWidget,
    QTreeWidgetItem,
)
from PyQt5.QtCore import Qt

DARK_STYLE = """
QMainWindow, QWidget { background-color: #1a1a2e; color: #e0e0e0; }
QPushButton {
    background-color: #0d7377; color: #ffffff; border: none;
    padding: 8px 16px; border-radius: 6px; font-size: 13px;
}
QPushButton:hover { background-color: #14a3a8; }
QPushButton.run { background-color: #27ae60; }
QPushButton.run:hover { background-color: #2ecc71; }
QListWidget, QTreeWidget {
    background-color: #16213e; color: #e0e0e0; border: 1px solid #0f3460;
    border-radius: 6px; padding: 5px; font-size: 13px;
}
QListWidget::item:selected, QTreeWidget::item:selected { background-color: #0d7377; }
QLabel { color: #e0e0e0; }
QTextEdit {
    background-color: #1a1a2e; color: #e0e0e0; border: 1px solid #0f3460;
    border-radius: 6px; padding: 8px; font-family: "Consolas", "Courier New", monospace;
    font-size: 13px;
}
QTabWidget::pane { border: 1px solid #0f3460; border-radius: 6px; background-color: #16213e; }
QTabBar::tab {
    background-color: #0f3460; color: #e0e0e0; padding: 8px 16px;
    border-top-left-radius: 6px; border-top-right-radius: 6px;
}
QTabBar::tab:selected { background-color: #0d7377; }
QComboBox {
    background-color: #16213e; color: #e0e0e0; border: 1px solid #0f3460;
    border-radius: 6px; padding: 6px;
}
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView {
    background-color: #16213e; color: #e0e0e0; selection-background-color: #0d7377;
}
QStatusBar { background-color: #0f3460; color: #e0e0e0; }
QSplitter::handle { background-color: #0f3460; width: 2px; }
"""


class DevSuiteWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EduOS Developer Suite")
        self.resize(1200, 800)
        self.setStyleSheet(DARK_STYLE)
        self.current_file = None
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        header = QLabel("EduOS Developer Suite")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 28px; padding: 15px; color: #00d4ff;")

        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_editor_tab(), "Code Editor")
        self.tabs.addTab(self.create_docker_tab(), "Docker")
        self.tabs.addTab(self.create_languages_tab(), "Languages")

        main_layout.addWidget(header)
        main_layout.addWidget(self.tabs)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Dev Suite ready")

    def create_editor_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        toolbar = QHBoxLayout()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Python 3", "JavaScript", "C++", "Java", "HTML/CSS"])
        self.lang_combo.currentTextChanged.connect(
            lambda l: self.status.showMessage(f"Language: {l}")
        )
        run_btn = QPushButton("Run Code")
        run_btn.setStyleSheet("background-color: #27ae60;")
        run_btn.clicked.connect(self.run_code)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(lambda: self.editor.clear())
        toolbar.addWidget(QLabel("Language:"))
        toolbar.addWidget(self.lang_combo)
        toolbar.addStretch()
        toolbar.addWidget(clear_btn)
        toolbar.addWidget(run_btn)

        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabel("Project Files")
        self.file_tree.setMaximumWidth(200)
        root = QTreeWidgetItem(self.file_tree, ["project"])
        QTreeWidgetItem(root, ["main.py"])
        QTreeWidgetItem(root, ["utils.py"])
        QTreeWidgetItem(root, ["README.md"])
        self.file_tree.itemClicked.connect(
            lambda item, col: self.status.showMessage(f"Opened: {item.text(0)}")
        )

        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Write your code here...")
        self.editor.setPlainText(
            "# Welcome to EduOS Developer Suite\nprint('Hello, World!')\n"
        )

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setMaximumHeight(150)
        self.output.setPlaceholderText("Output will appear here...")

        editor_layout = QVBoxLayout()
        editor_layout.addWidget(self.editor)
        editor_layout.addWidget(QLabel("Output:"))
        editor_layout.addWidget(self.output)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.file_tree)
        editor_widget = QWidget()
        editor_widget.setLayout(editor_layout)
        splitter.addWidget(editor_widget)
        splitter.setSizes([200, 800])

        layout.addLayout(toolbar)
        layout.addWidget(splitter)
        return tab

    def run_code(self):
        code = self.editor.toPlainText()
        if not code.strip():
            self.output.setPlainText("No code to run")
            return
        lang = self.lang_combo.currentText()
        self.output.setPlainText(f"Running {lang} code...\n")
        if lang == "Python 3":
            import subprocess, tempfile, os

            try:
                with tempfile.NamedTemporaryFile(
                    suffix=".py", mode="w", delete=False
                ) as f:
                    f.write(code)
                    fpath = f.name
                result = subprocess.run(
                    [sys.executable, fpath], capture_output=True, text=True, timeout=10
                )
                os.unlink(fpath)
                out = result.stdout or ""
                err = result.stderr or ""
                self.output.setPlainText(out + ("\nErrors:\n" + err if err else ""))
            except subprocess.TimeoutExpired:
                self.output.setPlainText("Execution timed out")
            except Exception as e:
                self.output.setPlainText(f"Error: {e}")
        else:
            self.output.setPlainText(
                f"{lang} execution not yet implemented in this preview"
            )

    def create_docker_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Docker Container Management"))
        containers = QListWidget()
        containers.addItems(
            ["edos-python-dev", "edos-postgres", "edos-redis", "edos-nginx"]
        )
        containers.setMaximumHeight(150)
        layout.addWidget(containers)

        btn_layout = QHBoxLayout()
        start_btn = QPushButton("Start Container")
        start_btn.clicked.connect(
            lambda: self.status.showMessage("Starting container...")
        )
        stop_btn = QPushButton("Stop Container")
        stop_btn.clicked.connect(
            lambda: self.status.showMessage("Stopping container...")
        )
        build_btn = QPushButton("Build Image")
        build_btn.clicked.connect(lambda: self.status.showMessage("Building image..."))
        btn_layout.addWidget(start_btn)
        btn_layout.addWidget(stop_btn)
        btn_layout.addWidget(build_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        status_text = QTextEdit()
        status_text.setReadOnly(True)
        status_text.setPlainText("Containers: 4 running\nImages: 12\nDisk usage: 2.3GB")
        layout.addWidget(status_text)
        return tab

    def create_languages_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Language Runtimes"))
        runtimes = QTreeWidget()
        runtimes.setHeaderLabels(["Language", "Version", "Status"])
        runtimes.addTopLevelItem(QTreeWidgetItem(["Python 3", "3.12", "Installed"]))
        runtimes.addTopLevelItem(QTreeWidgetItem(["Node.js", "20.x", "Installed"]))
        runtimes.addTopLevelItem(QTreeWidgetItem(["GCC/G++", "13.2", "Installed"]))
        runtimes.addTopLevelItem(QTreeWidgetItem(["Java", "21", "Installed"]))
        runtimes.addTopLevelItem(QTreeWidgetItem(["Rust", "1.75", "Not Installed"]))
        runtimes.addTopLevelItem(QTreeWidgetItem(["Go", "1.22", "Not Installed"]))
        layout.addWidget(runtimes)
        install_btn = QPushButton("Install Selected")
        install_btn.clicked.connect(
            lambda: self.status.showMessage("Installing runtime...")
        )
        layout.addWidget(install_btn)
        layout.addStretch()
        return tab


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = DevSuiteWindow()
    window.show()
    sys.exit(app.exec_())
