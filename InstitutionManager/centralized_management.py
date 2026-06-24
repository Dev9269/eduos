"""
EduOS Institution Manager — Centralized Management Prototype
Illustrates the EduOS Central Platform → Institution Server → Student Devices architecture.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QMessageBox, QScrollArea, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer

from styles import *
from ui_components import Card, SectionTitle, StatCard, StatusBadge, btn_primary, btn_outline
from config import load_json, save_json, PATHS, log_activity


class CentralizedManagementTab(QWidget):
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

        # Architecture Diagram
        arch_card = QFrame()
        arch_card.setStyleSheet(card_style())
        arch_layout = QVBoxLayout(arch_card)

        arch_title = QLabel("🏗 EduOS Centralized Architecture")
        arch_title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {TEXT_PRIMARY};")
        arch_layout.addWidget(arch_title)

        arch_sub = QLabel("Central Platform → Institution Server → Student Devices")
        arch_sub.setStyleSheet(f"font-size: 13px; color: {TEXT_SECONDARY};")
        arch_layout.addWidget(arch_sub)

        arch_layout.addSpacing(12)

        # Visual architecture flow
        flow = QHBoxLayout()
        flow.setSpacing(0)

        layers = [
            ("☁️ EduOS\nCentral Platform", PRIMARY, "Global management\nUpdate distribution\nAnalytics & monitoring\nSecurity management"),
            ("🏛 Institution\nServer", PRIMARY_DARK, "Local deployment\nStudent management\nExam distribution\nContent caching"),
            ("💻 Student\nDevices", "#1e40af", "EduOS client\nExam interface\nLearn Hub\nDevelopment tools"),
        ]

        for i, (name, color, desc) in enumerate(layers):
            layer_box = QFrame()
            layer_box.setStyleSheet(f"background: {color}; border-radius: 12px; padding: 16px;")
            ll = QVBoxLayout(layer_box)
            ll.setAlignment(Qt.AlignmentFlag.AlignCenter)
            n = QLabel(name)
            n.setStyleSheet("font-size: 14px; font-weight: 700; color: white;")
            n.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ll.addWidget(n)
            ll.addSpacing(8)
            for line in desc.split("\n"):
                d = QLabel(f"• {line}")
                d.setStyleSheet("font-size: 11px; color: rgba(255,255,255,0.8);")
                d.setAlignment(Qt.AlignmentFlag.AlignCenter)
                ll.addWidget(d)
            flow.addWidget(layer_box, 1)

            if i < len(layers) - 1:
                arrow = QLabel("  →  ")
                arrow.setStyleSheet(f"font-size: 24px; color: {TEXT_MUTED}; font-weight: 700; padding: 0 8px;")
                flow.addWidget(arrow)

        arch_layout.addLayout(flow)
        content.addWidget(arch_card)

        # Central Management Dashboard
        dash_card = QFrame()
        dash_card.setStyleSheet(card_style())
        dash_layout = QVBoxLayout(dash_card)

        dt = QLabel("📊 Central Platform Dashboard (Simulation)")
        dt.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {TEXT_PRIMARY};")
        dash_layout.addWidget(dt)

        # KPIs row
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(12)

        central_kpis = [
            ("12,847", "Managed Devices", "💻", PRIMARY),
            ("342", "Active Institutions", "🏛", SUCCESS),
            ("98.2%", "Uptime", "📈", ACCENT),
            ("24/7", "Support Status", "🛡️", INFO),
        ]
        for val, label, icon, color in central_kpis:
            card = StatCard(val, label, icon, "", True, color)
            kpi_row.addWidget(card)
        dash_layout.addLayout(kpi_row)
        content.addWidget(dash_card)

        # Management Features Grid
        features_title = SectionTitle("🛠 Centralized Management Features")
        content.addWidget(features_title)

        features_grid = QHBoxLayout()
        features_grid.setSpacing(12)

        features = [
            ("📦 Update Distribution", "Push OS and module updates to all institutional servers and student devices from a central repository."),
            ("🔒 Security Patches", "Deploy critical security patches instantly across the entire EduOS ecosystem with one-click."),
            ("📡 Device Monitoring", "Real-time monitoring of all connected devices: status, health, compliance, and activity."),
            ("📝 Exam Distribution", "Securely distribute examination papers to institution servers and collect encrypted results."),
            ("📊 System Analytics", "Comprehensive analytics dashboard showing deployment status, usage patterns, and performance metrics."),
        ]

        for title, desc in features:
            card = QFrame()
            card.setStyleSheet(f"background: white; border: 1px solid {BORDER}; border-radius: 12px; padding: 16px;")
            cl = QVBoxLayout(card)
            t = QLabel(title)
            t.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {TEXT_PRIMARY};")
            cl.addWidget(t)
            d = QLabel(desc)
            d.setStyleSheet(f"font-size: 12px; color: {TEXT_SECONDARY};")
            d.setWordWrap(True)
            cl.addWidget(d)

            sim_btn = QPushButton("▶ Simulate")
            sim_btn.setStyleSheet(btn_small())
            sim_btn.clicked.connect(lambda checked, t=title: self._simulate(t))
            cl.addWidget(sim_btn)

            features_grid.addWidget(card)

        content.addLayout(features_grid)

        # Data Flow Simulation
        flow_card = QFrame()
        flow_card.setStyleSheet(card_style())
        flow_layout = QVBoxLayout(flow_card)

        ft = QLabel("🔄 Data Flow Simulation")
        ft.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {TEXT_PRIMARY};")
        flow_layout.addWidget(ft)

        self.flow_status = QLabel("Ready. Click 'Simulate Data Flow' to demonstrate the architecture.")
        self.flow_status.setStyleSheet(f"font-size: 13px; color: {TEXT_SECONDARY}; padding: 8px 0;")
        self.flow_status.setWordWrap(True)
        flow_layout.addWidget(self.flow_status)

        self.flow_progress = QProgressBar()
        self.flow_progress.setVisible(False)
        self.flow_progress.setStyleSheet("QProgressBar { background: #e2e8f0; border: none; border-radius: 6px; height: 10px; text-align: center; font-size: 11px; } QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #16a34a); border-radius: 6px; }")
        flow_layout.addWidget(self.flow_progress)

        btn_row = QHBoxLayout()
        sim_flow_btn = QPushButton("▶ Simulate Data Flow")
        sim_flow_btn.setStyleSheet(btn_primary())
        sim_flow_btn.clicked.connect(self._simulate_flow)
        btn_row.addWidget(sim_flow_btn)

        btn_row.addStretch()
        flow_layout.addLayout(btn_row)

        content.addWidget(flow_card)

        content.addStretch()
        layout.addWidget(scroll)

    def _simulate(self, feature):
        QMessageBox.information(self, feature,
            f"[SIMULATION] {feature}\n\n"
            f"This demonstrates the centralized management capability.\n\n"
            f"In a real deployment:\n"
            f"1. Central Platform → Institution Server: Command sent\n"
            f"2. Institution Server → Student Devices: Distribution queued\n"
            f"3. Status: Completed (simulated)\n\n"
            f"EduOS Central Platform makes institution-wide management possible from a single interface."
        )
        log_activity("Central Management Simulated", f"Feature: {feature}")

    def _simulate_flow(self):
        self.flow_status.setText("⏳ Simulating Central Platform → Institution Server → Student Devices data flow...")
        self.flow_progress.setVisible(True)
        self.flow_progress.setValue(0)

        self._flow_step = 0
        self._flow_timer = QTimer()
        self._flow_timer.timeout.connect(self._flow_tick)
        self._flow_timer.start(400)

    def _flow_tick(self):
        self._flow_step += 1
        self.flow_progress.setValue(self._flow_step * 10)

        steps = [
            "☁️ Central Platform: Preparing update package...",
            "☁️ Central Platform: Encrypting payload...",
            "☁️ Central Platform: Signing with institutional key...",
            "📡 Transmitting to Institution Server...",
            "📡 Institution Server: Verifying signature...",
            "📡 Institution Server: Decrypting payload...",
            "🏛 Institution Server: Queuing for distribution...",
            "🏛 Institution Server: Distributing to 847 devices...",
            "💻 Student Devices: Receiving update (85% complete)...",
            "✅ All devices updated. Confirmation sent to Central Platform.",
        ]

        if self._flow_step <= len(steps):
            self.flow_status.setText(steps[self._flow_step - 1])

        if self._flow_step >= 10:
            self._flow_timer.stop()
            self.flow_status.setText("✅ Data flow simulation complete. Architecture validated: Central Platform → Institution Server → Student Devices.")
            log_activity("Data Flow Simulated", "Centralized architecture demonstration completed")
