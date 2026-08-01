"""
EduOS Institution Manager — AI Education Assistant (Mock)
Placeholder AI assistant for concept explanation, note generation, practice questions,
coding help, and cybersecurity learning.
"""

import sys
from pathlib import Path
_DIR = Path(__file__).parent
if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTextEdit, QLineEdit, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from styles import *
from ui_components import Card, SectionTitle, btn_primary, btn_outline

MOCK_RESPONSES = {
    "explain": [
        "**Concept Explanation:**\n\n{query} is a fundamental concept in computer science.\n\n**Definition:**\nIt refers to the process of breaking down complex problems into smaller, manageable components.\n\n**Key Points:**\n1. Enables systematic problem-solving\n2. Forms the basis of algorithmic thinking\n3. Used extensively in software design patterns\n\n**Example:**\n```\n# Simple illustration\nresult = solve(problem)\nprint(f'Solution: {result}')\n```\n\nWould you like me to elaborate on any specific aspect?"
    ],
    "notes": [
        "## Study Notes: {query}\n\n### Overview\n- Topic: {query}\n- Difficulty: Intermediate\n- Estimated study time: 45 minutes\n\n### Key Concepts\n1. **Fundamental Principles**\n   - Core theory and applications\n   - Historical context and evolution\n   - Current industry relevance\n\n2. **Practical Applications**\n   - Real-world use cases\n   - Implementation strategies\n   - Best practices and patterns\n\n### Summary Points\n✓ Understand the core concepts\n✓ Practice with hands-on examples\n✓ Review related topics for deeper understanding\n\n### Practice Questions\n1. What are the main components of {query}?\n2. How does {query} apply to modern systems?\n3. Compare and contrast {query} with related approaches."
    ],
    "practice": [
        "## Practice Questions: {query}\n\n### Basic Level\n1. Define {query} in your own words.\n2. List three key characteristics of {query}.\n3. What problems does {query} solve?\n\n### Intermediate Level\n4. Explain how {query} integrates with other systems.\n5. Write a simple implementation demonstrating {query}.\n6. What are the trade-offs when using {query}?\n\n### Advanced Level\n7. Design a system architecture incorporating {query}.\n8. Analyze the performance implications of {query}.\n9. Compare {query} with alternative approaches.\n\n---\n*Answers are not provided to encourage active learning. Would you like hints for any question?*"
    ],
    "coding": [
        "## Coding Help: {query}\n\n### Approach\nHere's a structured approach to solve this problem:\n\n### Solution Template\n```python\ndef solution(input_data):\n    # Step 1: Understand the problem\n    # Step 2: Design the algorithm\n    # Step 3: Implement\n    # Step 4: Test\n    \n    # Your implementation here\n    result = process(input_data)\n    return result\n\n# Test cases\ntest_input = \"sample\"\nexpected_output = \"expected\"\nprint(solution(test_input))\n```\n\n### Complexity Analysis\n- Time Complexity: O(n) where n is input size\n- Space Complexity: O(1) for optimal solution\n\n### Tips\n- Consider edge cases (empty input, large inputs)\n- Use descriptive variable names\n- Add comments for complex logic"
    ],
    "cyber": [
        "## Cybersecurity Learning: {query}\n\n### Topic Overview\n{query} is an important concept in cybersecurity.\n\n### Key Learning Objectives\n1. Understand the fundamental principles\n2. Identify common vulnerabilities\n3. Implement defensive measures\n4. Follow ethical guidelines\n\n### Security Best Practices\n✅ Always work in isolated environments\n✅ Obtain proper authorization before testing\n✅ Document findings thoroughly\n✅ Follow responsible disclosure\n\n### Hands-On Exercise\nTry this in EduOS Cyber Lab (containerized environment):\n```bash\n# Example command for practice\necho \"Exploring {query} in safe environment\"\n```\n\n⚠ **Important:** Always practice cybersecurity skills in authorized environments only."
    ]
}


class AIAssistantTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_w = QWidget()
        scroll.setWidget(scroll_w)
        content = QVBoxLayout(scroll_w)
        content.setSpacing(16)

        # Header
        header = QWidget()
        header.setStyleSheet(f"background: linear-gradient(135deg, #7c3aed, #4f46e5); border-radius: 16px; padding: 20px;")
        hl = QHBoxLayout(header)
        ht = QVBoxLayout()
        ti = QLabel("🤖 EduOS AI Education Assistant")
        ti.setStyleSheet("font-size: 22px; font-weight: 700; color: white;")
        ht.addWidget(ti)
        su = QLabel("AI-powered learning assistant. Explain concepts, generate notes, practice questions, coding help, and cybersecurity guidance.")
        su.setStyleSheet("font-size: 13px; color: rgba(255,255,255,0.75);")
        su.setWordWrap(True)
        ht.addWidget(su)
        hl.addLayout(ht, 1)
        hl.addWidget(QLabel("🧠"), alignment=Qt.AlignmentFlag.AlignRight)
        hl.itemAt(1).widget().setStyleSheet("font-size: 40px;")
        content.addWidget(header)

        # Capability buttons
        caps_title = SectionTitle("Select Capability")
        content.addWidget(caps_title)

        caps = QHBoxLayout()
        caps.setSpacing(8)
        capabilities = [
            ("📖 Explain Concepts", "explain"),
            ("📝 Generate Notes", "notes"),
            ("❓ Practice Questions", "practice"),
            ("💻 Coding Help", "coding"),
            ("🛡️ Cyber Security", "cyber"),
        ]
        self._mode_buttons = {}
        for label, mode in capabilities:
            btn = QPushButton(label)
            btn.setStyleSheet(self._btn_style(False))
            btn.clicked.connect(lambda checked, m=mode: self._set_mode(m))
            caps.addWidget(btn)
            self._mode_buttons[mode] = btn
        caps.addStretch()
        content.addLayout(caps)

        self._current_mode = "explain"
        self._mode_buttons["explain"].setStyleSheet(self._btn_style(True))

        # Input area
        input_card = QFrame()
        input_card.setStyleSheet(card_style())
        input_layout = QVBoxLayout(input_card)

        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Ask me anything... e.g., 'Explain recursion' or 'Generate notes on machine learning'")
        self.query_input.setStyleSheet("font-size: 14px; padding: 12px; border: 2px solid #e2e8f0; border-radius: 8px;")
        self.query_input.returnPressed.connect(self._generate)
        input_layout.addWidget(self.query_input)

        gen_btn = QPushButton("✨ Generate Response")
        gen_btn.setStyleSheet(btn_primary())
        gen_btn.clicked.connect(self._generate)
        input_layout.addWidget(gen_btn)

        content.addWidget(input_card)

        # Response area
        response_card = QFrame()
        response_card.setStyleSheet(card_style())
        response_layout = QVBoxLayout(response_card)

        rt = QLabel("💬 Response")
        rt.setStyleSheet(f"font-size: 15px; font-weight: 600; color: {TEXT_PRIMARY};")
        response_layout.addWidget(rt)

        self.response_area = QTextEdit()
        self.response_area.setReadOnly(True)
        self.response_area.setStyleSheet("""
            QTextEdit {
                font-size: 13px; padding: 12px; border: 1px solid #e2e8f0;
                border-radius: 8px; background: #f8fafc; color: #1e293b;
                font-family: 'Inter', system-ui, sans-serif;
            }
        """)
        self.response_area.setMinimumHeight(200)
        self.response_area.setPlaceholderText("Your AI-generated response will appear here...")
        self.response_area.setHtml("""
            <div style="color: #94a3b8; text-align: center; padding: 40px;">
                <p style="font-size: 18px;">🤖 AI Assistant Ready</p>
                <p style="font-size: 13px;">Type a question above and select a capability to get started.</p>
                <p style="font-size: 12px; margin-top: 20px;">Try: "Explain recursion" or "Generate notes on machine learning"</p>
            </div>
        """)
        response_layout.addWidget(self.response_area)

        content.addWidget(response_card)

        # Info footer
        info = QLabel("⚡ No external APIs required. Responses are generated locally for demonstration purposes.")
        info.setStyleSheet(f"font-size: 11px; color: {TEXT_MUTED};")
        content.addWidget(info)

        content.addStretch()
        layout.addWidget(scroll)

    def _btn_style(self, active):
        if active:
            return f"background: #7c3aed; color: white; padding: 8px 16px; font-size: 12px; font-weight: 600; border: none; border-radius: 8px;"
        return f"background: white; color: {TEXT_PRIMARY}; border: 1px solid {BORDER}; padding: 8px 16px; font-size: 12px; font-weight: 500; border-radius: 8px;"

    def _set_mode(self, mode):
        self._current_mode = mode
        for m, btn in self._mode_buttons.items():
            btn.setStyleSheet(self._btn_style(m == mode))

    def _generate(self):
        query = self.query_input.text().strip()
        if not query:
            QMessageBox.information(self, "Input Needed", "Please enter a question or topic.")
            return

        self.response_area.setHtml("""
            <div style="text-align: center; padding: 20px;">
                <p style="color: #64748b;">🤔 Generating response...</p>
            </div>
        """)

        mock_key = self._current_mode
        responses = MOCK_RESPONSES.get(mock_key, MOCK_RESPONSES["explain"])
        response = responses[0].replace("{query}", query)

        from PyQt6.QtCore import QTimer
        QTimer.singleShot(300, lambda: self._display_response(query, response))

    def _display_response(self, query, response):
        html = f"""
        <div style="font-family: 'Inter', system-ui, sans-serif;">
            <div style="background: #ede9fe; padding: 8px 12px; border-radius: 8px; margin-bottom: 12px;">
                <p style="font-size: 12px; color: #6d28d9; font-weight: 600;">You asked: {query}</p>
            </div>
            <div style="font-size: 13px; line-height: 1.6;">
                {self._md_to_html(response)}
            </div>
        </div>
        """
        self.response_area.setHtml(html)

    def _md_to_html(self, md):
        import re
        html = md
        html = re.sub(r'### (.+)', r'<h3 style="color: #1e293b; margin-top: 12px;">\1</h3>', html)
        html = re.sub(r'## (.+)', r'<h2 style="color: #1e293b; margin-top: 16px;">\1</h2>', html)
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'`(.+?)`', r'<code style="background: #1e1e2e; color: #cdd6f4; padding: 2px 6px; border-radius: 3px; font-size: 12px;">\1</code>', html)
        html = re.sub(r'```\n?([\s\S]*?)```', r'<pre style="background: #1e1e2e; color: #cdd6f4; padding: 12px; border-radius: 8px; font-size: 12px; overflow-x: auto;"><code>\1</code></pre>', html)
        html = html.replace('\n', '<br>')
        html = re.sub(r'^- (.+)', r'<li style="margin-left: 16px;">\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'✓ (.+)', r'<span style="color: #16a34a;">✓</span> \1', html)
        html = re.sub(r'⚠ (.+)', r'<span style="color: #dc2626;">⚠</span> \1', html)
        return html
