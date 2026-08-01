"""
EduOS Institution Manager — Demo Mode
Guided demonstration of the complete EduOS ecosystem for startup interviews and presentations.
"""

import sys
from pathlib import Path
_DIR = Path(__file__).parent
if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))

import json
import os
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTextEdit, QScrollArea, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap

from styles import *
from ui_components import Card, SectionTitle, StatCard, StatusBadge, btn_primary, btn_outline
from config import load_json, save_json, PATHS, log_activity, BASE_DIR, EXPORTS_DIR, SCREENSHOTS_DIR


DEMO_STEPS = [
    {
        "id": "overview",
        "title": "🏗 Platform Overview",
        "description": "EduOS has evolved from an operating system into a complete educational infrastructure platform. This demo showcases the modular, scalable architecture.",
        "duration": 30
    },
    {
        "id": "architecture",
        "title": "🏛 Modular Architecture",
        "description": "EduOS uses a modular plugin system. Each module (Learn Hub, Exam Hub, Dev Suite, Cyber Lab, etc.) can be independently enabled, disabled, installed, and removed. The Module Registry manages dependencies and configurations centrally.",
        "duration": 45
    },
    {
        "id": "institution",
        "title": "🏫 Institution Management",
        "description": "Educational institutions can manage their entire deployment from the Institution Manager. Departments, courses, students, faculty, labs, exams, and devices are all managed through a single dashboard.",
        "duration": 60
    },
    {
        "id": "branding",
        "title": "🎨 Institutional Branding",
        "description": "Institutions can customize their EduOS experience with their own logo, name, colors, and welcome messages — without modifying the underlying operating system. A university becomes 'Parul University EduOS'.",
        "duration": 30
    },
    {
        "id": "central",
        "title": "☁️ Centralized Management",
        "description": "EduOS Central Platform manages updates, security patches, device monitoring, exam distribution, and analytics across all connected institutions and devices from a single interface.",
        "duration": 45
    },
    {
        "id": "ai",
        "title": "🤖 AI Education Assistant",
        "description": "Built-in AI assistant helps students with concept explanations, note generation, practice questions, coding help, and cybersecurity learning — all without external API dependencies.",
        "duration": 30
    },
    {
        "id": "exam",
        "title": "📝 Secure Examination Platform",
        "description": "EduOS Exam Hub provides end-to-end encrypted examination delivery, from creation to distribution to auto-grading. Anti-cheating measures and secure local storage ensure integrity.",
        "duration": 45
    },
    {
        "id": "cyber",
        "title": "🛡️ Cybersecurity Training",
        "description": "EduOS Cyber Lab provides isolated container-based environments for safe cybersecurity practice. Students learn network scanning, web security, forensics, and more in a controlled environment.",
        "duration": 30
    },
    {
        "id": "scalability",
        "title": "📈 Scalability & Startup Value",
        "description": "EduOS is designed for scale: from a single classroom to a university with 50,000+ devices. Centralized management, modular architecture, and institutional branding make it a complete educational infrastructure platform.",
        "duration": 45
    },
]


class DemoModeTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_step = 0
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

        # Demo Header
        header = QWidget()
        header.setStyleSheet(f"background: linear-gradient(135deg, {SECONDARY}, #1e293b); border-radius: 16px; padding: 24px;")
        hl = QHBoxLayout(header)
        ht = QVBoxLayout()
        ti = QLabel("🎬 EduOS Platform Demo")
        ti.setStyleSheet("font-size: 26px; font-weight: 700; color: white;")
        ht.addWidget(ti)
        su = QLabel("A guided tour demonstrating the complete EduOS educational infrastructure platform — modular architecture, institution management, centralized control, and enterprise readiness.")
        su.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.75);")
        su.setWordWrap(True)
        ht.addWidget(su)
        hl.addLayout(ht, 1)

        # Status in header
        status_frame = QFrame()
        status_frame.setStyleSheet("background: rgba(255,255,255,0.1); border-radius: 10px; padding: 12px 16px;")
        sl = QVBoxLayout(status_frame)
        self.demo_status = QLabel("Ready to Start")
        self.demo_status.setStyleSheet("font-size: 14px; font-weight: 600; color: #4ade80;")
        sl.addWidget(self.demo_status)
        self.demo_progress = QProgressBar()
        self.demo_progress.setMaximum(100)
        self.demo_progress.setValue(0)
        self.demo_progress.setStyleSheet("QProgressBar { background: rgba(255,255,255,0.15); border: none; border-radius: 4px; height: 6px; } QProgressBar::chunk { background: #4ade80; border-radius: 4px; }")
        sl.addWidget(self.demo_progress)
        hl.addWidget(status_frame)
        content.addWidget(header)

        # Demo controls
        controls = QHBoxLayout()
        controls.setSpacing(8)

        self.start_btn = QPushButton("▶ Start Guided Demo")
        self.start_btn.setStyleSheet(f"QPushButton {{ background: {SUCCESS}; color: white; padding: 12px 24px; font-size: 14px; font-weight: 600; border: none; border-radius: 8px; }} QPushButton:hover {{ background: #15803d; }} QPushButton:pressed {{ padding: 13px 23px 11px 25px; }}")
        self.start_btn.clicked.connect(self._start_demo)
        controls.addWidget(self.start_btn)

        self.next_btn = QPushButton("Next Step →")
        self.next_btn.setStyleSheet(btn_primary())
        self.next_btn.setEnabled(False)
        self.next_btn.clicked.connect(self._next_step)
        controls.addWidget(self.next_btn)

        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.setStyleSheet(btn_outline())
        self.prev_btn.setEnabled(False)
        self.prev_btn.clicked.connect(self._prev_step)
        controls.addWidget(self.prev_btn)

        controls.addStretch()

        gen_doc_btn = QPushButton("📄 Generate Documentation")
        gen_doc_btn.setStyleSheet(btn_outline())
        gen_doc_btn.clicked.connect(self._generate_documentation)
        controls.addWidget(gen_doc_btn)

        gen_screenshot_btn = QPushButton("📸 Generate Screenshots")
        gen_screenshot_btn.setStyleSheet(btn_outline())
        gen_screenshot_btn.clicked.connect(self._generate_screenshots)
        controls.addWidget(gen_screenshot_btn)

        content.addLayout(controls)

        # Demo step display
        self.step_card = QFrame()
        self.step_card.setStyleSheet(card_style())
        self.step_layout = QVBoxLayout(self.step_card)
        self.step_layout.setSpacing(16)

        # Current step content
        self.step_title = QLabel("Select a demo step to begin.")
        self.step_title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {TEXT_PRIMARY};")
        self.step_layout.addWidget(self.step_title)

        self.step_desc = QLabel("Click 'Start Guided Demo' to walk through each capability of the EduOS platform. Each step explains a key feature of the ecosystem.")
        self.step_desc.setStyleSheet(f"font-size: 14px; color: {TEXT_SECONDARY}; line-height: 1.6;")
        self.step_desc.setWordWrap(True)
        self.step_layout.addWidget(self.step_desc)

        # Step navigation dots
        dots = QHBoxLayout()
        self._dots = []
        for i, step in enumerate(DEMO_STEPS):
            dot = QPushButton(f"  {i+1}  ")
            dot.setStyleSheet(f"""
                QPushButton {{ background: {'#2563eb' if i == 0 else '#e2e8f0'}; color: {'white' if i == 0 else '#64748b'};
                font-size: 11px; font-weight: 600; border: none; border-radius: 12px; padding: 4px 8px; min-width: 28px; }}
                QPushButton:hover {{ background: {'#1d4ed8' if i == 0 else '#cbd5e1'}; }}
            """)
            dot.clicked.connect(lambda checked, idx=i: self._jump_to(idx))
            dots.addWidget(dot)
            self._dots.append(dot)
        dots.addStretch()
        self._dots_layout = dots
        self.step_layout.addLayout(dots)

        # Step details area
        self.step_details = QTextEdit()
        self.step_details.setReadOnly(True)
        self.step_details.setStyleSheet(f"""
            QTextEdit {{ font-size: 13px; padding: 12px; border: 1px solid {BORDER};
            border-radius: 8px; background: {BG_SECTION}; color: {TEXT_PRIMARY}; line-height: 1.6; }}
        """)
        self.step_details.setMinimumHeight(120)
        self.step_details.setMaximumHeight(200)
        self.step_layout.addWidget(self.step_details)

        content.addWidget(self.step_card)

        # Value proposition
        value_card = QFrame()
        value_card.setStyleSheet(card_style())
        value_layout = QVBoxLayout(value_card)
        vt = QLabel("💡 Startup Value Proposition")
        vt.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {TEXT_PRIMARY};")
        value_layout.addWidget(vt)

        values = [
            ("📐 Modular Architecture", "Plugin-based system enables institutions to customize their EduOS deployment. Modules can be independently developed, tested, and distributed."),
            ("📈 Scalability", "From a single classroom to a university of 50,000+ students. Centralized management makes institution-wide administration possible."),
            ("🎨 Institutional Branding", "Every institution can brand EduOS as their own — changing logos, colors, names, and messages without OS-level modifications."),
            ("🔒 Security & Compliance", "End-to-end encrypted exam delivery, isolated cybersecurity labs, and centralized security patch management."),
            ("🤖 AI-Enhanced Learning", "Built-in AI assistant for concept explanation, note generation, and practice — no external API dependencies."),
        ]
        for title, desc in values:
            v_item = QFrame()
            v_item.setStyleSheet(f"border-bottom: 1px solid {BORDER}; padding: 8px 0;")
            vl = QVBoxLayout(v_item)
            vl.setContentsMargins(0, 4, 0, 4)
            t = QLabel(title)
            t.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {TEXT_PRIMARY};")
            vl.addWidget(t)
            d = QLabel(desc)
            d.setStyleSheet(f"font-size: 12px; color: {TEXT_SECONDARY};")
            d.setWordWrap(True)
            vl.addWidget(d)
            value_layout.addWidget(v_item)

        content.addWidget(value_card)

        content.addStretch()
        layout.addWidget(scroll)

        self._update_step(0)

    def _start_demo(self):
        self._current_step = 0
        self.next_btn.setEnabled(True)
        self.prev_btn.setEnabled(False)
        self.start_btn.setEnabled(False)
        self.demo_status.setText("▶ Demo in progress...")
        self.demo_status.setStyleSheet("font-size: 14px; font-weight: 600; color: #facc15;")
        self._update_step(0)
        log_activity("Demo Started", "Guided platform demonstration initiated")

    def _next_step(self):
        if self._current_step < len(DEMO_STEPS) - 1:
            self._current_step += 1
            self._update_step(self._current_step)
            self.prev_btn.setEnabled(True)
            if self._current_step >= len(DEMO_STEPS) - 1:
                self.next_btn.setEnabled(False)
                self.demo_status.setText("✅ Demo Complete!")
                self.demo_status.setStyleSheet("font-size: 14px; font-weight: 600; color: #4ade80;")
                log_activity("Demo Completed", "Guided platform demonstration finished")
        self.start_btn.setEnabled(False)

    def _prev_step(self):
        if self._current_step > 0:
            self._current_step -= 1
            self._update_step(self._current_step)
            self.next_btn.setEnabled(True)
            if self._current_step <= 0:
                self.prev_btn.setEnabled(False)
            self.demo_status.setText("▶ Demo in progress...")
            self.demo_status.setStyleSheet("font-size: 14px; font-weight: 600; color: #facc15;")

    def _jump_to(self, idx):
        if 0 <= idx < len(DEMO_STEPS):
            self._current_step = idx
            self._update_step(idx)
            self.next_btn.setEnabled(idx < len(DEMO_STEPS) - 1)
            self.prev_btn.setEnabled(idx > 0)
            self.start_btn.setEnabled(False)
            self.demo_status.setText("▶ Demo in progress...")

    def _update_step(self, idx):
        step = DEMO_STEPS[idx]
        self.step_title.setText(step["title"])
        self.step_desc.setText(step["description"])

        details_html = f"""
        <div style="font-family: 'Inter', system-ui, sans-serif;">
            <h3 style="color: #1e293b; margin-bottom: 8px;">{step['title']}</h3>
            <p style="color: #475569; line-height: 1.7;">{step['description']}</p>
            <p style="color: #94a3b8; font-size: 12px; margin-top: 12px;">
                ⏱ Estimated demo time: {step['duration']} seconds | Step {idx + 1} of {len(DEMO_STEPS)}
            </p>
        </div>
        """
        self.step_details.setHtml(details_html)

        # Update dots
        for i, dot in enumerate(self._dots):
            if i == idx:
                dot.setStyleSheet(f"background: {PRIMARY}; color: white; font-size: 11px; font-weight: 600; border: none; border-radius: 12px; padding: 4px 8px; min-width: 28px;")
            elif i < idx:
                dot.setStyleSheet(f"background: {SUCCESS}; color: white; font-size: 11px; font-weight: 600; border: none; border-radius: 12px; padding: 4px 8px; min-width: 28px;")
            else:
                dot.setStyleSheet(f"background: {BORDER}; color: {TEXT_MUTED}; font-size: 11px; font-weight: 600; border: none; border-radius: 12px; padding: 4px 8px; min-width: 28px;")

        self.demo_progress.setValue(int((idx + 1) / len(DEMO_STEPS) * 100))

    def _generate_documentation(self):
        doc_path = EXPORTS_DIR / "eduos_platform_documentation.html"
        sections = []
        for i, step in enumerate(DEMO_STEPS):
            sections.append(f"""
            <div style="margin-bottom: 24px; padding: 16px; background: #f8fafc; border-radius: 8px; border-left: 4px solid #2563eb;">
                <h2 style="color: #1e293b; margin: 0 0 8px 0;">{step['title']}</h2>
                <p style="color: #475569; line-height: 1.6;">{step['description']}</p>
            </div>
            """)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>EduOS Platform Documentation</title>
<style>
body {{ font-family: 'Inter', system-ui, sans-serif; max-width: 900px; margin: 0 auto; padding: 40px 20px; background: #f1f5f9; color: #1e293b; }}
.header {{ background: linear-gradient(135deg, #0f172a, #1e293b); color: white; padding: 32px; border-radius: 16px; margin-bottom: 32px; }}
.header h1 {{ margin: 0; font-size: 28px; }}
.header p {{ color: rgba(255,255,255,0.7); font-size: 14px; }}
h2 {{ font-size: 18px; }}
.footer {{ margin-top: 32px; padding: 16px; background: #e2e8f0; border-radius: 8px; font-size: 12px; color: #64748b; text-align: center; }}
</style></head>
<body>
<div class="header">
    <h1>📚 EduOS Platform Documentation</h1>
    <p>Complete educational infrastructure platform — Modular Architecture, Institution Management, Centralized Control</p>
    <p style="font-size: 12px; color: rgba(255,255,255,0.5);">Generated: {datetime.now().strftime('%B %d, %Y %H:%M')}</p>
</div>
{"".join(sections)}
<div class="footer">
    <p><strong>EduOS Platform</strong> — From operating system to educational infrastructure.</p>
    <p>Scalable | Modular | Secure | AI-Enhanced | Enterprise-Ready</p>
    <p>Generated by EduOS Institution Manager Demo Mode</p>
</div>
</body></html>"""

        with open(doc_path, "w") as f:
            f.write(html)
        log_activity("Documentation Generated", f"Platform documentation saved to {doc_path}")
        QMessageBox.information(self, "Documentation Generated",
            f"Platform documentation saved to:\n{doc_path}\n\nOpen in any web browser to view.")

    def _generate_screenshots(self):
        # Generate textual screenshots for documentation
        screenshots = []
        for i, step in enumerate(DEMO_STEPS):
            ss = f"""
========================================
  EduOS Platform Demo — Screenshot {i+1}
========================================
  {step['title']}
========================================
  {step['description']}
----------------------------------------
  [EduOS Institution Manager v2.0]
  [Demo Mode Active]
========================================
"""
            ss_path = SCREENSHOTS_DIR / f"demo_step_{i+1}_{step['id']}.txt"
            with open(ss_path, "w") as f:
                f.write(ss)
            screenshots.append(ss_path)

        QMessageBox.information(self, "Screenshots Generated",
            f"Generated {len(screenshots)} screenshot documents in:\n{SCREENSHOTS_DIR}\n\nThese describe each demo step for presentation materials.")
