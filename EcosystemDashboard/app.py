#!/usr/bin/env python3
"""
EduOS Ecosystem Dashboard — Liquid Glass Design Language
Premium educational infrastructure platform with frosted glass aesthetic.
"""

import sys, json, os, random
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QFrame, QTextEdit, QLineEdit,
    QProgressBar, QScrollArea, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QGridLayout, QComboBox, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

from data_gen import generate_all, DATA_DIR

from design_system import (
    EduOSColors as C, EduOSTypography as T,
    LIQUID_GLASS_STYLESHEET,
    GlassCard, GlassStatCard, GlassBanner, GlassTable, SectionTitle, StatusBadge,
    glass_card_style, glass_stat_card_style, glass_banner_style,
    accent_glow_style, glass_button_style, glass_success_button_style,
    glass_danger_button_style, glass_warning_button_style,
    status_badge_style, apply_glass_theme
)


# ─── Helpers ─────────────────────────────────────────────────

def load_data():
    path = DATA_DIR / "ecosystem_data.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return generate_all()


def _label(text, style):
    l = QLabel(text)
    l.setStyleSheet(style)
    return l


def _stat_row(label, value):
    w = QWidget()
    w.setStyleSheet(f"border-bottom: 1px solid {C.GLASS_BORDER}; padding: 4px 0;")
    l = QHBoxLayout(w)
    l.setContentsMargins(0, 4, 0, 4)
    l.addWidget(QLabel(label))
    l.itemAt(0).widget().setStyleSheet(f"font-size: 12px; color: {C.TEXT_SECONDARY}; font-family: {T.FAMILY};")
    l.addStretch()
    l.addWidget(QLabel(value))
    l.itemAt(2).widget().setStyleSheet(f"font-size: 13px; font-weight: 600; color: {C.TEXT_PRIMARY}; font-family: {T.FAMILY};")
    return w


# ═══════════════════════════════════════════════════════════════
#  PHASE 1 — ECOSYSTEM DASHBOARD
# ═══════════════════════════════════════════════════════════════

class EcosystemDashboard(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        sw = QWidget()
        scroll.setWidget(sw)
        content = QVBoxLayout(sw)
        content.setSpacing(16)

        # Welcome banner
        banner = GlassBanner("🏫 EduOS Ecosystem Dashboard",
            "Complete educational infrastructure platform — Live monitoring across all connected systems.")
        content.addWidget(banner)

        # KPI row
        inst = self.data["institution"]
        kpis = QHBoxLayout()
        kpis.setSpacing(12)
        for val, label, icon in [
            (f"{inst['students']:,}", "Active Students", "🎓"),
            (f"{inst['faculty']:,}", "Faculty Members", "👨‍🏫"),
            (f"{inst['departments']}", "Departments", "🏛"),
            (f"{inst['total_devices']:,}", "Connected Devices", "💻"),
            (f"{inst['online_devices']:,}", "Online Now", "📡"),
        ]:
            kpis.addWidget(GlassStatCard(val, label, icon))
        content.addLayout(kpis)

        # Middle section
        mid = QHBoxLayout()
        mid.setSpacing(16)

        # Device status
        dev_card = GlassCard()
        dl = QVBoxLayout(dev_card)
        dl.addWidget(SectionTitle("💻 Device Status Overview"))
        tl = self.data.get("timeline", [])
        latest = tl[-1] if tl else {}
        health = self.data.get("health", {})
        for label, val, color in [
            ("System Health", f"{health.get('system_health', latest.get('system_health', 98))}%", C.ACCENT_GREEN),
            ("Online Devices", f"{inst['online_devices']:,} / {inst['total_devices']:,}", C.ACCENT_GREEN),
            ("CPU Usage", f"{health.get('cpu_usage', 42)}%", C.ACCENT_PRIMARY),
            ("RAM Usage", f"{health.get('ram_usage', 62)}%", C.ACCENT_TERTIARY),
            ("Disk Usage", f"{health.get('disk_usage', 71)}%", C.ACCENT_AMBER),
            ("Security Score", f"{health.get('security_score', 96)}/100", C.ACCENT_GREEN),
        ]:
            row = QHBoxLayout()
            row.addWidget(_label(label, f"font-size: 12px; color: {C.TEXT_SECONDARY}; font-family: {T.FAMILY};"))
            row.addStretch()
            row.addWidget(_label(val, f"font-size: 14px; font-weight: 700; color: {color}; font-family: {T.FAMILY};"))
            dl.addLayout(row)
        mid.addWidget(dev_card, 2)

        # Active courses + exams
        course_card = GlassCard()
        cl = QVBoxLayout(course_card)
        cl.addWidget(SectionTitle("📚 Active Courses & Exams"))
        courses = self.data.get("courses", [])
        active_courses = [c for c in courses if c.get("active")]
        exams = self.data.get("exams", [])
        ongoing_exams = [e for e in exams if e["status"] == "Ongoing"]
        cl.addWidget(_label(f"Active Courses: {len(active_courses)}",
            f"font-size: 22px; font-weight: 700; color: {C.ACCENT_PRIMARY}; font-family: {T.FAMILY};"))
        cl.addWidget(_label(f"Ongoing Exams: {len(ongoing_exams)}",
            f"font-size: 13px; color: {C.TEXT_SECONDARY}; font-family: {T.FAMILY};"))
        cl.addSpacing(8)
        for c in active_courses[:5]:
            row = QHBoxLayout()
            row.addWidget(_label(f"  {c['name']}", f"font-size: 12px; color: {C.TEXT_PRIMARY}; font-family: {T.FAMILY};"))
            row.addStretch()
            p = QProgressBar()
            p.setMaximum(100)
            p.setValue(c.get("progress", 50))
            p.setFixedWidth(120)
            p.setFormat(f"{c['progress']}%")
            row.addWidget(p)
            cl.addLayout(row)
        mid.addWidget(course_card, 3)
        content.addLayout(mid)

        # Activity feed
        act_card = GlassCard()
        al = QVBoxLayout(act_card)
        al.addWidget(SectionTitle("⏱ Live Activity Feed"))
        activity = self.data.get("activity", [])
        for entry in activity[:10]:
            row = QHBoxLayout()
            row.setContentsMargins(0, 2, 0, 2)
            dot = QLabel("●")
            dot.setStyleSheet(f"font-size: 8px; color: {C.ACCENT_PRIMARY};")
            row.addWidget(dot)
            ts = entry.get("timestamp", "")[11:16] if "T" in entry.get("timestamp", "") else ""
            row.addWidget(_label(ts, f"font-size: 11px; color: {C.TEXT_MUTED}; font-family: {T.FAMILY};"))
            row.addWidget(_label(entry.get("action", ""),
                f"font-size: 12px; color: {C.TEXT_PRIMARY}; font-weight: 500; font-family: {T.FAMILY};"))
            row.addStretch()
            al.addLayout(row)
        content.addWidget(act_card)

        # Updates
        upd_card = GlassCard()
        ul = QVBoxLayout(upd_card)
        updates = self.data.get("updates", [])
        ul.addWidget(SectionTitle(f"🔄 Updates Available ({len(updates)})"))
        for u in updates:
            row = QHBoxLayout()
            icon = "🔴" if u.get("critical") else "🔵"
            row.addWidget(_label(f"{icon} {u['package']} v{u['version']}",
                f"font-size: 13px; font-weight: 500; font-family: {T.FAMILY}; color: {C.TEXT_PRIMARY};"))
            row.addWidget(StatusBadge(u["type"], "danger" if u.get("critical") else "info"))
            row.addWidget(_label(f"{u['size_mb']} MB",
                f"font-size: 11px; color: {C.TEXT_MUTED}; font-family: {T.FAMILY};"))
            row.addStretch()
            ul.addLayout(row)
        content.addWidget(upd_card)

        content.addStretch()
        layout.addWidget(scroll)


# ═══════════════════════════════════════════════════════════════
#  PHASE 2 — CENTRAL SERVER SIMULATION
# ═══════════════════════════════════════════════════════════════

class CentralServerSimulation(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        sw = QWidget()
        scroll.setWidget(sw)
        content = QVBoxLayout(sw)
        content.setSpacing(16)

        # Architecture banner
        banner = GlassBanner("☁️ Central Platform  →  🏛 Institution Server  →  💻 Student Devices",
            "End-to-end encrypted infrastructure with live device management and update orchestration.")
        content.addWidget(banner)

        # Architecture diagram
        diag = QHBoxLayout()
        diag.setSpacing(4)
        layers = [
            ("☁️ EduOS\nCentral\nPlatform",
             ["Global Management", "Update Distribution", "Security Management", "Analytics Hub", "Multi-Institution"]),
            ("🏛 Institution\nServer",
             ["Local Deployment", "Student Sync", "Exam Distribution", "Content Cache", "Device Mgmt"]),
            ("💻 Student\nDevices",
             ["EduOS Client", "Exam Interface", "Learn Portal", "Dev Tools", "Cyber Lab"]),
        ]
        for name, items in layers:
            box = QFrame()
            box.setStyleSheet(f"""
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(108,99,255,0.12), stop:1 rgba(79,195,247,0.06));
                border: 1px solid {C.GLASS_BORDER};
                border-radius: 14px; padding: 16px;
            """)
            bl = QVBoxLayout(box)
            bl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            bl.addWidget(_label(name, f"font-size: 13px; font-weight: 700; color: {C.TEXT_PRIMARY}; font-family: {T.FAMILY};"))
            bl.addSpacing(6)
            for item in items:
                bl.addWidget(_label(f"• {item}", f"font-size: 10px; color: {C.TEXT_SECONDARY}; font-family: {T.FAMILY};"))
            diag.addWidget(box, 1)
            if layers.index((name, items)) < len(layers) - 1:
                diag.addWidget(_label("  →  ", f"font-size: 28px; color: {C.TEXT_MUTED}; font-weight: 700; font-family: {T.MONO};"))
        content.addLayout(diag)

        # Simulation
        sim_card = GlassCard()
        sl = QVBoxLayout(sim_card)
        sl.addWidget(SectionTitle("🔄 Data Flow Simulation"))
        self.sim_status = QLabel("Ready. Click 'Simulate' to demonstrate the architecture in action.")
        self.sim_status.setStyleSheet(f"font-size: 13px; color: {C.TEXT_SECONDARY}; font-family: {T.FAMILY};")
        sl.addWidget(self.sim_status)
        self.sim_progress = QProgressBar()
        self.sim_progress.setVisible(False)
        self.sim_progress.setMaximum(100)
        sl.addWidget(self.sim_progress)
        btn = QPushButton("▶ Run Simulation")
        btn.setStyleSheet(accent_glow_style())
        btn.clicked.connect(self._run_simulation)
        sl.addWidget(btn)
        content.addWidget(sim_card)

        # Institution stats
        stats_card = GlassCard()
        sl2 = QVBoxLayout(stats_card)
        sl2.addWidget(SectionTitle("🏛 Connected Institution Statistics"))
        inst = self.data["institution"]
        for label, val in [
            ("Institution", inst["name"]),
            ("Type", inst["type"]),
            ("Accreditation", inst["accreditation"]),
            ("Total Students", f"{inst['students']:,}"),
            ("Faculty & Staff", f"{inst['faculty'] + inst['staff']:,}"),
            ("Departments", str(inst["departments"])),
            ("Programs", str(inst["programs"])),
            ("Total Devices", f"{inst['total_devices']:,}"),
            ("Devices Online", f"{inst['online_devices']:,} ({round(inst['online_devices']/inst['total_devices']*100)}%)"),
        ]:
            sl2.addWidget(_stat_row(label, val))
        content.addWidget(stats_card)

        # Device monitoring
        dev_card = GlassCard()
        dl = QVBoxLayout(dev_card)
        dl.addWidget(SectionTitle("📡 Live Device Monitoring"))
        devices = self.data.get("devices", [])
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(["Device", "Type", "Department", "Status", "OS", "IP", "Last Seen"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.verticalHeader().setVisible(False)
        table.setStyleSheet(f"""
            QTableWidget {{ border: none; background: transparent; gridline-color: transparent;
                font-size: 13px; font-family: {T.FAMILY}; color: {C.TEXT_PRIMARY}; }}
            QTableWidget::item {{ padding: 10px 14px; border-bottom: 1px solid rgba(255,255,255,0.04); }}
            QTableWidget::item:selected {{ background: rgba(108,99,255,0.15); color: white; }}
            QHeaderView::section {{ background: transparent; padding: 12px 14px; font-weight: 600;
                font-size: 11px; color: {C.TEXT_SECONDARY}; border: none;
                border-bottom: 1px solid rgba(255,255,255,0.06);
                text-transform: uppercase; letter-spacing: 0.5px; }}
        """)
        for d in devices:
            row = table.rowCount()
            table.insertRow(row)
            for col, key in enumerate(["name", "type", "dept", "status", "os", "ip", "last_seen"]):
                item = QTableWidgetItem(str(d.get(key, "")))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(row, col, item)
            st = d.get("status", "offline")
            table.setCellWidget(row, 3, StatusBadge(st.capitalize(), st))
        dl.addWidget(table)
        content.addWidget(dev_card)

        # Update distribution
        upd_card = GlassCard()
        ul = QVBoxLayout(upd_card)
        ul.addWidget(SectionTitle("📦 Update Distribution Queue"))
        updates = self.data.get("updates", [])
        for u in updates:
            row_w = QFrame()
            row_w.setStyleSheet(f"border-bottom: 1px solid {C.GLASS_BORDER}; padding: 8px 0;")
            rl = QHBoxLayout(row_w)
            rl.setContentsMargins(0, 4, 0, 4)
            rl.addWidget(_label(f"{u['package']}", f"font-size: 13px; font-weight: 600; color: {C.TEXT_PRIMARY}; font-family: {T.FAMILY};"))
            rl.addWidget(_label(f"v{u['version']}", f"font-size: 12px; color: {C.TEXT_MUTED}; font-family: {T.FAMILY};"))
            rl.addWidget(StatusBadge(u["type"], "danger" if u.get("critical") else "info"))
            if u.get("critical"):
                rl.addWidget(StatusBadge("CRITICAL", "danger"))
            pb = QProgressBar()
            pb.setMaximum(100)
            pb.setValue(random.randint(0, 100))
            pb.setFixedWidth(120)
            pb.setFormat(f"{pb.value()}% deployed")
            rl.addWidget(pb)
            rl.addStretch()
            deploy_btn = QPushButton("Deploy")
            deploy_btn.setStyleSheet(glass_success_button_style())
            deploy_btn.clicked.connect(lambda checked, p=u["package"]: self._deploy_update(p))
            rl.addWidget(deploy_btn)
            ul.addWidget(row_w)
        content.addWidget(upd_card)
        content.addStretch()
        layout.addWidget(scroll)

    def _run_simulation(self):
        self.sim_progress.setVisible(True)
        self.sim_progress.setValue(0)
        self._sim_step = 0
        self._sim_timer = QTimer()
        self._sim_timer.timeout.connect(self._sim_tick)
        self._sim_timer.start(300)

    def _sim_tick(self):
        self._sim_step += 1
        self.sim_progress.setValue(self._sim_step * 10)
        steps = [
            "☁️ Central Platform: Preparing update payload...",
            "☁️ Central Platform: Encrypting with institution key...",
            "📡 Transmitting to Institution Server (10 Gbps link)...",
            "🏛 Institution Server: Verifying cryptographic signature...",
            "🏛 Institution Server: Decrypting and staging update...",
            "🏛 Institution Server: Queuing distribution to 4,892 devices...",
            "💻 Student Devices: Receiving update (42% complete)...",
            "💻 Student Devices: Receiving update (89% complete)...",
            "✅ All devices updated. Confirmation sent to Central Platform.",
            "📊 Analytics updated. 100% compliance achieved.",
        ]
        if self._sim_step <= len(steps):
            self.sim_status.setText(steps[self._sim_step - 1])
        if self._sim_step >= 10:
            self._sim_timer.stop()
            self.sim_status.setText("✅ Simulation complete: Central Platform → Institution Server → 4,892 Student Devices validated.")

    def _deploy_update(self, pkg):
        QMessageBox.information(self, "Deploy Update",
            f"[SIMULATION] Deploying {pkg} to all connected devices...\n\n"
            f"Central Platform → Institution Server → Student Devices\n\n"
            f"Status: Queued for distribution to {self.data['institution']['online_devices']:,} online devices.")


# ═══════════════════════════════════════════════════════════════
#  PHASE 3 — MODULE MANAGEMENT SYSTEM
# ═══════════════════════════════════════════════════════════════

class ModuleManagement(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        sw = QWidget()
        scroll.setWidget(sw)
        content = QVBoxLayout(sw)
        content.setSpacing(12)

        # Header
        banner = GlassBanner("🧩 EduOS Module Store",
            "9 modular components with enable/disable/install/remove and dependency management.")
        bl = QHBoxLayout()
        bl.addStretch()
        installed = sum(1 for m in self.data["modules"] if m["status"] == "installed")
        bl.addWidget(_label(f"{installed}/9 Installed",
            f"font-size: 14px; color: {C.TEXT_SECONDARY}; font-family: {T.FAMILY};"))
        banner.layout().addLayout(bl)
        content.addWidget(banner)

        # Module cards
        for mod in self.data["modules"]:
            card = GlassCard()
            installed = mod["status"] == "installed"
            enabled = mod.get("enabled", False)

            cl = QVBoxLayout(card)
            cl.setSpacing(8)

            row = QHBoxLayout()
            row.addWidget(_label(f"{mod['icon']} {mod['name']}",
                f"font-size: 16px; font-weight: 600; color: {C.TEXT_PRIMARY}; font-family: {T.FAMILY};"))
            row.addStretch()
            row.addWidget(_label(f"v{mod['version']}",
                f"font-size: 11px; color: {C.TEXT_MUTED}; background: {C.GLASS_CARD}; padding: 2px 8px; border-radius: 4px; font-family: {T.MONO};"))
            row.addWidget(StatusBadge(mod["category"], "info"))
            if installed:
                row.addWidget(StatusBadge("Enabled" if enabled else "Disabled", "success" if enabled else "inactive"))
            else:
                row.addWidget(StatusBadge("Not Installed", "not_installed"))
            cl.addLayout(row)

            if installed:
                res = QHBoxLayout()
                res.addWidget(_label(f"RAM: {mod['ram_mb']} MB", f"font-size: 11px; color: {C.TEXT_MUTED}; font-family: {T.FAMILY};"))
                res.addWidget(_label(f"CPU: {mod['cpu_pct']}%", f"font-size: 11px; color: {C.TEXT_MUTED}; font-family: {T.FAMILY};"))
                res.addWidget(_label(f"Size: {mod['size_mb']} MB", f"font-size: 11px; color: {C.TEXT_MUTED}; font-family: {T.FAMILY};"))
                res.addStretch()
                cl.addLayout(res)

            actions = QHBoxLayout()
            mid = mod["id"]
            if not installed:
                btn = QPushButton("📥 Install Module")
                btn.setStyleSheet(accent_glow_style())
                btn.clicked.connect(lambda checked, m=mid: self._install(m))
                actions.addWidget(btn)
            else:
                if enabled:
                    btn = QPushButton("⏸ Disable")
                    btn.setStyleSheet(glass_warning_button_style())
                    btn.clicked.connect(lambda checked, m=mid: self._toggle(m, False))
                    actions.addWidget(btn)
                else:
                    btn = QPushButton("▶ Enable")
                    btn.setStyleSheet(glass_success_button_style())
                    btn.clicked.connect(lambda checked, m=mid: self._toggle(m, True))
                    actions.addWidget(btn)
                btn_remove = QPushButton("🗑 Remove")
                btn_remove.setStyleSheet(glass_danger_button_style())
                btn_remove.clicked.connect(lambda checked, m=mid: self._remove(m))
                actions.addWidget(btn_remove)
            actions.addStretch()
            cl.addLayout(actions)
            content.addWidget(card)

        content.addStretch()
        layout.addWidget(scroll)

    def _install(self, mid):
        for m in self.data["modules"]:
            if m["id"] == mid:
                m["status"] = "installed"
                m["enabled"] = True
                break
        self._refresh()
        QMessageBox.information(self, "Module Installed", f"{mid.replace('_',' ').title()} installed successfully.")

    def _toggle(self, mid, enable):
        for m in self.data["modules"]:
            if m["id"] == mid:
                m["enabled"] = enable
                break
        self._refresh()
        action = "enabled" if enable else "disabled"

    def _remove(self, mid):
        for m in self.data["modules"]:
            if m["id"] == mid:
                m["status"] = "not_installed"
                m["enabled"] = False
                break
        self._refresh()

    def _refresh(self):
        parent = self.parent()
        if parent:
            idx = parent.indexOf(self)
            if idx >= 0:
                parent.removeTab(idx)
                parent.insertTab(idx, ModuleManagement(self.data), "🧩 Modules")
                parent.setCurrentIndex(idx)


# ═══════════════════════════════════════════════════════════════
#  PHASE 4 — INSTITUTION CUSTOMIZATION
# ═══════════════════════════════════════════════════════════════

class InstitutionCustomization(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self._cfg = {
            "institution_name": data["institution"]["name"],
            "short_name": data["institution"]["short"],
            "theme": "Professional Blue",
            "welcome_message": "Welcome to EduOS — Your Learning Platform",
            "login_branding": "Powered by EduOS Educational Infrastructure",
            "primary_color": "#6c63ff",
            "secondary_color": "#4fc3f7",
        }
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        sw = QWidget()
        scroll.setWidget(sw)
        content = QVBoxLayout(sw)
        content.setSpacing(16)

        # Banner
        banner = GlassBanner("🎨 Institution Customization",
            "Custom branding without OS modifications. Everything is a config overlay.")
        content.addWidget(banner)

        # Form
        form_card = GlassCard()
        fl = QVBoxLayout(form_card)
        fl.setSpacing(12)
        fl.addWidget(SectionTitle("🏫 Institution Identity"))

        self.name_edit = QLineEdit(self._cfg["institution_name"])
        self.name_edit.setPlaceholderText("e.g. Parul University")
        fl.addWidget(self._labeled("Institution Name", self.name_edit))

        self.short_edit = QLineEdit(self._cfg["short_name"])
        self.short_edit.setPlaceholderText("e.g. PU")
        fl.addWidget(self._labeled("Short Name", self.short_edit))

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Professional Blue", "Dark Academia", "Modern Purple", "Clean Green", "Warm Orange", "Midnight Black"])
        self.theme_combo.setCurrentText(self._cfg["theme"])
        fl.addWidget(self._labeled("Theme", self.theme_combo))

        self.welcome_edit = QLineEdit(self._cfg["welcome_message"])
        fl.addWidget(self._labeled("Welcome Message", self.welcome_edit))

        self.login_edit = QLineEdit(self._cfg["login_branding"])
        fl.addWidget(self._labeled("Login Screen Branding", self.login_edit))

        colors = QHBoxLayout()
        colors.setSpacing(16)
        self.primary_btn = QPushButton("     Primary Color     ")
        self.primary_btn.setStyleSheet(f"background: {self._cfg['primary_color']}; color: white; padding: 8px 16px; border: none; border-radius: 6px; font-weight: 600; font-family: {T.FAMILY};")
        self.primary_btn.clicked.connect(lambda: self._pick_color("primary"))
        colors.addWidget(self.primary_btn)
        self.secondary_btn = QPushButton("     Secondary Color     ")
        self.secondary_btn.setStyleSheet(f"background: {self._cfg['secondary_color']}; color: white; padding: 8px 16px; border: none; border-radius: 6px; font-weight: 600; font-family: {T.FAMILY};")
        self.secondary_btn.clicked.connect(lambda: self._pick_color("secondary"))
        colors.addWidget(self.secondary_btn)
        colors.addStretch()
        fl.addLayout(colors)

        save_btn = QPushButton("💾 Apply Customization")
        save_btn.setStyleSheet(accent_glow_style())
        save_btn.clicked.connect(self._apply)
        fl.addWidget(save_btn)
        content.addWidget(form_card)

        # Preview
        preview_card = GlassCard()
        pl = QVBoxLayout(preview_card)
        pl.addWidget(SectionTitle("👁 Live Preview"))
        self.preview = QFrame()
        self.preview.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {self._cfg['primary_color']},
                stop:1 {self._cfg['secondary_color']});
            border-radius: 16px; padding: 24px;
        """)
        pvl = QVBoxLayout(self.preview)
        pvl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_name = QLabel(f"🏫 {self._cfg['institution_name']} EduOS")
        self.preview_name.setStyleSheet(f"font-size: 22px; font-weight: 700; color: white; font-family: {T.FAMILY};")
        self.preview_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pvl.addWidget(self.preview_name)
        self.preview_welcome = QLabel(f'"{self._cfg["welcome_message"]}"')
        self.preview_welcome.setStyleSheet(f"font-size: 14px; color: rgba(255,255,255,0.8); padding: 8px 0; font-family: {T.FAMILY};")
        self.preview_welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pvl.addWidget(self.preview_welcome)
        self.preview_login = QLabel(self._cfg["login_branding"])
        self.preview_login.setStyleSheet(f"font-size: 11px; color: rgba(255,255,255,0.5); font-style: italic; font-family: {T.FAMILY};")
        self.preview_login.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pvl.addWidget(self.preview_login)
        pl.addWidget(self.preview)

        # Quick examples
        examples = QHBoxLayout()
        examples.setSpacing(8)
        examples.addWidget(_label("Quick Examples:", f"font-size: 11px; color: {C.TEXT_MUTED}; font-family: {T.FAMILY};"))
        for ex in ["Parul University EduOS", "ABC School EduOS", "XYZ College EduOS"]:
            btn = QPushButton(ex)
            btn.setStyleSheet(glass_button_style())
            btn.clicked.connect(lambda checked, e=ex: self.name_edit.setText(e))
            examples.addWidget(btn)
        examples.addStretch()
        pl.addLayout(examples)
        content.addWidget(preview_card)

        content.addStretch()
        layout.addWidget(scroll)

    def _labeled(self, text, widget):
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(0, 2, 0, 2)
        label = QLabel(text)
        label.setStyleSheet(f"font-size: 13px; color: {C.TEXT_SECONDARY}; font-weight: 500; min-width: 160px; font-family: {T.FAMILY};")
        l.addWidget(label)
        l.addWidget(widget, 1)
        return w

    def _pick_color(self, which):
        from PyQt6.QtGui import QColorDialog
        color = QColorDialog.getColor(QColor(self._cfg[f"{which}_color"]), self, f"Choose {which.title()} Color")
        if color.isValid():
            hex_c = color.name()
            self._cfg[f"{which}_color"] = hex_c
            getattr(self, f"{which}_btn").setStyleSheet(f"background: {hex_c}; color: white; padding: 8px 16px; border: none; border-radius: 6px; font-weight: 600; font-family: {T.FAMILY};")
            self._update_preview()

    def _apply(self):
        self._cfg["institution_name"] = self.name_edit.text()
        self._cfg["short_name"] = self.short_edit.text()
        self._cfg["theme"] = self.theme_combo.currentText()
        self._cfg["welcome_message"] = self.welcome_edit.text()
        self._cfg["login_branding"] = self.login_edit.text()
        self._update_preview()
        QMessageBox.information(self, "Applied",
            f"✅ Customization applied to {self._cfg['institution_name']} EduOS\n\n"
            f"Theme: {self._cfg['theme']}\n"
            f"Login: \"{self._cfg['login_branding']}\"\n\n"
            "No OS-level changes were made. Branding is applied as a configuration overlay.")

    def _update_preview(self):
        self.preview.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {self._cfg['primary_color']},
                stop:1 {self._cfg['secondary_color']});
            border-radius: 16px; padding: 24px;
        """)
        self.preview_name.setText(f"🏫 {self._cfg['institution_name']} EduOS")
        self.preview_welcome.setText(f'"{self._cfg["welcome_message"]}"')
        self.preview_login.setText(self._cfg["login_branding"])


# ═══════════════════════════════════════════════════════════════
#  PHASE 5 — AI ASSISTANT
# ═══════════════════════════════════════════════════════════════

class AIAssistant(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self._mode = "ask"
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        sw = QWidget()
        scroll.setWidget(sw)
        content = QVBoxLayout(sw)
        content.setSpacing(16)

        # Header
        banner = GlassBanner("🤖 EduOS AI Assistant",
            "AI-powered learning (mock responses, no external APIs required).")
        content.addWidget(banner)

        # Mode selector
        caps = QHBoxLayout()
        caps.setSpacing(6)
        self._mode_btns = {}
        for label, mode in [
            ("❓ Ask Questions", "ask"),
            ("📝 Generate Notes", "notes"),
            ("📝 Practice MCQs", "mcq"),
            ("💻 Coding Help", "coding"),
            ("📚 Recommendations", "recommend"),
        ]:
            btn = QPushButton(label)
            btn.setStyleSheet(self._btn_style(mode == "ask"))
            btn.clicked.connect(lambda checked, m=mode: self._set_mode(m))
            caps.addWidget(btn)
            self._mode_btns[mode] = btn
        caps.addStretch()
        content.addLayout(caps)

        # Input
        input_card = GlassCard()
        il = QVBoxLayout(input_card)
        il.addWidget(_label("What would you like help with?",
            f"font-size: 13px; color: {C.TEXT_SECONDARY}; font-family: {T.FAMILY};"))
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("e.g., Explain recursion, Generate notes on machine learning, Help me with Python...")
        self.query_input.returnPressed.connect(self._generate)
        il.addWidget(self.query_input)
        gen_btn = QPushButton("✨ Generate")
        gen_btn.setStyleSheet(accent_glow_style())
        gen_btn.clicked.connect(self._generate)
        il.addWidget(gen_btn)
        content.addWidget(input_card)

        # Response
        resp_card = GlassCard()
        rl = QVBoxLayout(resp_card)
        rl.addWidget(_label("💬 Response",
            f"font-size: 15px; font-weight: 600; color: {C.TEXT_PRIMARY}; font-family: {T.FAMILY};"))
        self.response = QTextEdit()
        self.response.setReadOnly(True)
        self.response.setStyleSheet(f"""
            QTextEdit {{ font-size: 13px; padding: 16px; border: 1px solid {C.GLASS_BORDER};
            border-radius: 10px; background: {C.GLASS_LIGHT}; color: {C.TEXT_PRIMARY};
            font-family: {T.FAMILY}; }}
        """)
        self.response.setMinimumHeight(200)
        self.response.setHtml(f"""
            <div style="color: {C.TEXT_MUTED}; text-align: center; padding: 40px;">
                <p style="font-size: 18px;">🤖 AI Assistant Ready</p>
                <p style="font-size: 13px;">Select a mode and type your question above.</p>
                <p style="font-size: 12px; margin-top: 16px;">Try: "Explain recursion" or "Generate notes on machine learning"</p>
            </div>
        """)
        rl.addWidget(self.response)
        content.addWidget(resp_card)
        content.addStretch()
        layout.addWidget(scroll)

    def _btn_style(self, active):
        if active:
            return f"""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6c63ff, stop:1 #b388ff);
                color: white; padding: 8px 16px; font-size: 12px; font-weight: 600;
                border: none; border-radius: 10px; font-family: {T.FAMILY};
            """
        return f"""
            background: {C.GLASS_CARD}; color: {C.TEXT_PRIMARY};
            border: 1px solid {C.GLASS_BORDER};
            padding: 8px 16px; font-size: 12px; font-weight: 500;
            border-radius: 10px; font-family: {T.FAMILY};
        """

    def _set_mode(self, mode):
        self._mode = mode
        for m, btn in self._mode_btns.items():
            btn.setStyleSheet(self._btn_style(m == mode))

    def _generate(self):
        query = self.query_input.text().strip()
        if not query:
            QMessageBox.information(self, "Input Needed", "Please enter a question or topic.")
            return

        self.response.setHtml(f'<div style="text-align: center; padding: 20px; color: {C.TEXT_MUTED};">🤔 Generating response...</div>')

        responses = {
            "ask": f"""<div style="font-family: {T.FAMILY};">
<div style="background: rgba(108,99,255,0.1); padding: 10px 14px; border-radius: 10px; margin-bottom: 12px; border: 1px solid rgba(108,99,255,0.15);">
<p style="font-size: 12px; color: #b388ff; font-weight: 600;">Your Question: {query}</p></div>
<h3 style="color: {C.TEXT_PRIMARY};">Answer</h3>
<p style="color: {C.TEXT_SECONDARY}; line-height: 1.6;">{
query.capitalize()} is a fundamental concept in computer science and education.</p>
<p style="color: {C.TEXT_SECONDARY}; line-height: 1.6;">It involves understanding the core principles and applying them to solve real-world problems. The key aspects include:</p>
<ul style="color: {C.TEXT_SECONDARY};">
<li><strong>Definition:</strong> Clear understanding of what {query} means</li>
<li><strong>Applications:</strong> How it is used in practical scenarios</li>
<li><strong>Examples:</strong> Real-world implementations and case studies</li>
<li><strong>Best Practices:</strong> Recommended approaches and methodologies</li>
</ul>
<p style="color: {C.TEXT_MUTED}; font-size: 12px; margin-top: 12px;">💡 Would you like me to elaborate on any specific aspect?</p></div>""",

            "notes": f"""<div style="font-family: {T.FAMILY};">
<h2 style="color: {C.TEXT_PRIMARY};">📝 Study Notes: {query}</h2>
<h3 style="color: {C.ACCENT_PRIMARY}; margin-top: 12px;">Overview</h3>
<p style="color: {C.TEXT_SECONDARY};">• Topic: {query}<br>• Difficulty: Intermediate<br>• Estimated Study Time: 45 minutes</p>
<h3 style="color: {C.ACCENT_PRIMARY}; margin-top: 12px;">Key Concepts</h3>
<p style="color: {C.TEXT_SECONDARY};"><strong>1. Fundamental Principles</strong><br>Core theory, historical context, and relevance in modern education.</p>
<p style="color: {C.TEXT_SECONDARY};"><strong>2. Practical Applications</strong><br>Real-world use cases, implementation strategies, and patterns.</p>
<p style="color: {C.TEXT_SECONDARY};"><strong>3. Advanced Topics</strong><br>Extended concepts, related fields, and emerging trends.</p>
<h3 style="color: {C.ACCENT_GREEN}; margin-top: 12px;">Summary Points</h3>
<p style="color: #81c784;">✓ Understand core concepts<br>✓ Practice with examples<br>✓ Review related topics</p>
<p style="color: {C.TEXT_MUTED}; font-size: 12px;">📌 Save these notes for revision.</p></div>""",

            "mcq": f"""<div style="font-family: {T.FAMILY};">
<h2 style="color: {C.TEXT_PRIMARY};">📝 Practice MCQs: {query}</h2>
<p style="color: {C.TEXT_SECONDARY};">Test your knowledge with these practice questions.</p>
<div style="background: {C.GLASS_CARD}; padding: 14px; border-radius: 10px; margin: 8px 0; border: 1px solid {C.GLASS_BORDER};">
<p style="font-weight: 600; color: {C.TEXT_PRIMARY};">Q1: What is the primary purpose of {query}?</p>
<p style="color: {C.TEXT_SECONDARY};">A) To simplify complex processes<br>B) To increase computational power<br>C) To reduce memory usage<br>D) To improve user interface</p>
</div>
<div style="background: {C.GLASS_CARD}; padding: 14px; border-radius: 10px; margin: 8px 0; border: 1px solid {C.GLASS_BORDER};">
<p style="font-weight: 600; color: {C.TEXT_PRIMARY};">Q2: Which of the following best describes {query}?</p>
<p style="color: {C.TEXT_SECONDARY};">A) A programming paradigm<br>B) A design pattern<br>C) A theoretical framework<br>D) A practical methodology</p>
</div>
<p style="color: {C.TEXT_MUTED}; font-size: 12px;">💡 Answers: 1-A, 2-D<br>📌 Want more questions? Try a different topic!</p></div>""",

            "coding": f"""<div style="font-family: {T.FAMILY};">
<h2 style="color: {C.TEXT_PRIMARY};">💻 Coding Help: {query}</h2>
<h3 style="color: {C.ACCENT_PRIMARY};">Approach</h3>
<p style="color: {C.TEXT_SECONDARY};">Here's a structured approach to solve this problem:</p>
<pre style="background: #0a0a14; color: #cdd6f4; padding: 14px; border-radius: 10px; font-size: 12px; font-family: {T.MONO}; border: 1px solid {C.GLASS_BORDER};">
def {query.lower().replace(' ', '_')}():
    # Step 1: Understand the requirements
    # Step 2: Design the algorithm
    # Step 3: Implement the solution
    # Step 4: Test with sample inputs

    # Your implementation here
    result = process(input_data)
    return result

# Test the solution
test_case = "example"
print(solution(test_case))
</pre>
<h3 style="color: {C.ACCENT_PRIMARY}; margin-top: 8px;">Complexity Analysis</h3>
<p style="color: {C.TEXT_SECONDARY};">• Time Complexity: O(n)<br>• Space Complexity: O(1)</p>
<p style="color: {C.TEXT_MUTED}; font-size: 12px;">💡 Try implementing and running this in EduOS Dev Suite!</p></div>""",

            "recommend": f"""<div style="font-family: {T.FAMILY};">
<h2 style="color: {C.TEXT_PRIMARY};">📚 Study Recommendations: {query}</h2>
<h3 style="color: {C.ACCENT_PRIMARY};">Personalized Learning Path</h3>
<p style="color: {C.TEXT_SECONDARY};">Based on your interest in {query}, here are recommendations:</p>
<div style="background: rgba(108,99,255,0.08); padding: 14px; border-radius: 10px; margin: 8px 0; border: 1px solid rgba(108,99,255,0.12);">
<p style="font-weight: 600; color: {C.TEXT_PRIMARY};">📖 Beginner Resources</p>
<p style="color: {C.TEXT_SECONDARY};">• Introduction to {query}<br>• Fundamentals and Core Concepts<br>• Interactive Tutorials in Learn Hub</p>
</div>
<div style="background: rgba(76,175,80,0.08); padding: 14px; border-radius: 10px; margin: 8px 0; border: 1px solid rgba(76,175,80,0.12);">
<p style="font-weight: 600; color: {C.TEXT_PRIMARY};">📗 Intermediate Resources</p>
<p style="color: {C.TEXT_SECONDARY};">• Advanced {query} Techniques<br>• Practical Projects in Dev Suite<br>• Cybersecurity Labs in Cyber Lab</p>
</div>
<div style="background: rgba(255,193,7,0.08); padding: 14px; border-radius: 10px; margin: 8px 0; border: 1px solid rgba(255,193,7,0.12);">
<p style="font-weight: 600; color: {C.TEXT_PRIMARY};">📕 Expert Resources</p>
<p style="color: {C.TEXT_SECONDARY};">• Research Papers and Case Studies<br>• Industry Certifications<br>• Research Portal Access</p>
</div>
<p style="color: {C.TEXT_MUTED}; font-size: 12px;">💡 Start with Learn Hub modules on this topic.</p></div>""",
        }

        response = responses.get(self._mode, responses["ask"])
        QTimer.singleShot(400, lambda: self.response.setHtml(response))


# ═══════════════════════════════════════════════════════════════
#  PHASE 6 — PRESENTATION MODE (Liquid Glass Edition)
# ═══════════════════════════════════════════════════════════════

class PresentationMode(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self._step = 0
        self._steps = [
            ("🎬 Platform Overview", "EduOS has evolved from an operating system into a complete educational infrastructure platform. This presentation demonstrates the ecosystem's capabilities."),
            ("🏗 Modular Architecture", "9 modules with enable/disable/install/remove support. Dependency management, resource tracking, and per-institution customization."),
            ("🏫 Institution Management", "Manage departments (12), courses (48), students (8,472), faculty (684), devices (5,280), and labs (42) from a single dashboard."),
            ("☁️ Centralized Management", "Central Platform → Institution Server → Student Devices architecture enables institution-wide update distribution, security patching, and monitoring."),
            ("🎨 Institutional Branding", "Every institution can brand EduOS as their own. 'Parul University EduOS', 'ABC School EduOS' — without modifying the OS."),
            ("🤖 AI-Enhanced Learning", "Built-in AI assistant for concept explanation, note generation, practice questions, and coding help. No external API dependencies."),
            ("📈 Startup Value", "EduOS is scalable from a single classroom to 50,000+ devices. Modular, secure, AI-enhanced, and enterprise-ready."),
        ]
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Header with glass
        banner = GlassBanner("🎬 EduOS Presentation Mode",
            "Maximum visual quality — investor-ready showcase experience.")
        bl = QHBoxLayout()
        bl.addStretch()
        self.step_counter = QLabel("Step 1 of 7")
        self.step_counter.setStyleSheet(f"font-size: 13px; color: {C.TEXT_SECONDARY}; font-family: {T.FAMILY};")
        bl.addWidget(self.step_counter)
        banner.layout().addLayout(bl)
        layout.addWidget(banner)

        # Glass progress bar
        progress_frame = QFrame()
        progress_frame.setStyleSheet(f"""
            background: {C.GLASS_CARD}; border: 1px solid {C.GLASS_BORDER};
            border-radius: 8px; padding: 6px;
        """)
        pl = QHBoxLayout(progress_frame)
        pl.setContentsMargins(2, 2, 2, 2)
        self.progress = QProgressBar()
        self.progress.setMaximum(len(self._steps))
        self.progress.setValue(1)
        self.progress.setFixedHeight(6)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(f"""
            QProgressBar {{ background: transparent; border: none; border-radius: 3px; }}
            QProgressBar::chunk {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #6c63ff, stop:1 #4fc3f7);
                border-radius: 3px; }}
        """)
        pl.addWidget(self.progress, 1)
        layout.addWidget(progress_frame)

        # Step navigation — glass dots
        nav = QHBoxLayout()
        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.setStyleSheet(glass_button_style())
        self.prev_btn.setEnabled(False)
        self.prev_btn.clicked.connect(self._prev)
        nav.addWidget(self.prev_btn)

        for i in range(len(self._steps)):
            dot = QPushButton(f"  {i+1}  ")
            dot.setStyleSheet(self._dot_style(i == 0))
            dot.clicked.connect(lambda checked, idx=i: self._jump(idx))
            nav.addWidget(dot)
            self._dots = getattr(self, "_dots", [])
            self._dots.append(dot)

        nav.addStretch()
        self.next_btn = QPushButton("Next →")
        self.next_btn.setStyleSheet(accent_glow_style())
        self.next_btn.clicked.connect(self._next)
        nav.addWidget(self.next_btn)
        layout.addLayout(nav)

        # Step content — enhanced glass card
        self.step_card = GlassCard()
        self.sl = QVBoxLayout(self.step_card)
        self.sl.setSpacing(20)

        # Step title with accent gradient
        title_frame = QFrame()
        title_frame.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(108,99,255,0.08), stop:1 rgba(79,195,247,0.04));
            border-radius: 12px; padding: 20px;
            border: 1px solid rgba(108,99,255,0.1);
        """)
        tfl = QVBoxLayout(title_frame)
        self.step_title = QLabel(self._steps[0][0])
        self.step_title.setStyleSheet(f"""
            font-size: 32px; font-weight: 700; color: {C.TEXT_PRIMARY};
            font-family: {T.FAMILY}; letter-spacing: -0.5px;
        """)
        tfl.addWidget(self.step_title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background: {C.GLASS_BORDER}; max-height: 1px;")
        tfl.addWidget(sep)

        self.step_desc = QLabel(self._steps[0][1])
        self.step_desc.setStyleSheet(f"""
            font-size: 16px; color: {C.TEXT_SECONDARY}; line-height: 1.8;
            font-family: {T.FAMILY}; padding: 4px 0;
        """)
        self.step_desc.setWordWrap(True)
        tfl.addWidget(self.step_desc)
        self.sl.addWidget(title_frame)

        # Step extra stats in glass tiles
        self.step_extra = QGridLayout()
        self.step_extra.setSpacing(10)
        self._update_extra(0)
        self.sl.addLayout(self.step_extra)
        self.sl.addStretch()

        layout.addWidget(self.step_card, 1)

        # Action buttons
        actions = QHBoxLayout()
        gen_doc = QPushButton("📄 Generate Documentation")
        gen_doc.setStyleSheet(glass_button_style())
        gen_doc.clicked.connect(self._gen_doc)
        actions.addWidget(gen_doc)
        gen_ss = QPushButton("📸 Export Presentation Materials")
        gen_ss.setStyleSheet(glass_button_style())
        gen_ss.clicked.connect(self._gen_screenshots)
        actions.addWidget(gen_ss)
        actions.addStretch()
        layout.addLayout(actions)

    def _update_extra(self, idx):
        while self.step_extra.count():
            item = self.step_extra.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        inst = self.data["institution"]
        extras = {
            0: [
                GlassStatCard(f"{inst['students']:,}", "Active Students", "🎓"),
                GlassStatCard(f"{inst['total_devices']:,}", "Connected Devices", "💻"),
                GlassStatCard(f"{inst['online_devices']:,}", "Online Now", "📡"),
                GlassStatCard(str(inst["departments"]), "Departments", "🏛"),
                GlassStatCard("98.7%", "Health Score", "🛡️"),
            ],
            1: [
                GlassStatCard("5/9", "Installed Modules", "🧩"),
                GlassStatCard("4 Available", "Learn, Attendance, Placement, Research", "📦"),
                GlassStatCard("Dependency", "Resolution + Enable/Disable", "⚙️"),
            ],
            6: [
                GlassStatCard("1 → 50K+", "Scalability Range", "📈"),
                GlassStatCard("Schools+Colleges", "Target Market", "🎯"),
                GlassStatCard("Modular+AI", "Competitive Edge", "⚡"),
                GlassStatCard("Startup Ready", "Demo Mode Active", "🚀"),
            ],
        }
        row, col = 0, 0
        for w in extras.get(idx, []):
            self.step_extra.addWidget(w, row, col)
            col += 1
            if col >= 4:
                col = 0
                row += 1

    def _dot_style(self, active):
        if active:
            return f"""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6c63ff, stop:1 #4fc3f7);
                color: white; font-size: 11px; font-weight: 600;
                border: none; border-radius: 14px; padding: 4px 10px;
                font-family: {T.FAMILY};
            """
        return f"""
            background: {C.GLASS_CARD}; color: {C.TEXT_MUTED};
            border: 1px solid {C.GLASS_BORDER};
            font-size: 11px; font-weight: 600;
            border-radius: 14px; padding: 4px 10px;
            font-family: {T.FAMILY};
        """

    def _next(self):
        if self._step < len(self._steps) - 1:
            self._step += 1
            self._update_step()

    def _prev(self):
        if self._step > 0:
            self._step -= 1
            self._update_step()

    def _jump(self, idx):
        self._step = idx
        self._update_step()

    def _update_step(self):
        self.step_title.setText(self._steps[self._step][0])
        self.step_desc.setText(self._steps[self._step][1])
        self.step_counter.setText(f"Step {self._step + 1} of {len(self._steps)}")
        self.progress.setValue(self._step + 1)
        self.prev_btn.setEnabled(self._step > 0)
        self.next_btn.setEnabled(self._step < len(self._steps) - 1)
        self._update_extra(self._step)
        for i, dot in enumerate(self._dots):
            dot.setStyleSheet(self._dot_style(i == self._step))

    def _gen_doc(self):
        path = Path.home() / ".eduos" / "exports" / "eduos_liquid_glass_presentation.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        inst = self.data["institution"]
        html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>EduOS Presentation — Liquid Glass</title>
<style>
body {{ font-family: 'Inter', system-ui, sans-serif; max-width: 1000px; margin: 0 auto; padding: 40px;
  background: #0a0a14; color: #e2e8f0; }}
.header {{ background: linear-gradient(135deg, #6c63ff, #4fc3f7); color: white; padding: 40px;
  border-radius: 18px; margin-bottom: 32px; }}
.header h1 {{ margin: 0; font-size: 32px; }}
.slide {{ background: rgba(255,255,255,0.04); backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 28px;
  margin-bottom: 16px; }}
h2 {{ color: #b388ff; font-size: 20px; }}
p {{ color: rgba(255,255,255,0.7); line-height: 1.6; }}
.footer {{ margin-top: 32px; padding: 16px; text-align: center; font-size: 12px;
  color: rgba(255,255,255,0.3); }}
</style></head><body>
<div class="header"><h1>🎬 EduOS Liquid Glass Presentation</h1>
<p>Complete Educational Infrastructure Platform — Design System Edition</p>
<p style="font-size: 12px; color: rgba(255,255,255,0.5);">Generated: {datetime.now().strftime('%B %d, %Y %H:%M')}</p></div>
{''.join(f'<div class="slide"><h2>{s[0]}</h2><p>{s[1]}</p></div>' for s in self._steps)}
<div class="slide"><h2>📊 Platform Metrics</h2>
<p>Students: {inst['students']:,} | Faculty: {inst['faculty']:,} | Devices: {inst['total_devices']:,} | Departments: {inst['departments']}</p>
<p>Design: Liquid Glass — Premium | Transparent Taskbar | Glass Effects | Smooth Animations</p></div>
<div class="footer"><p><strong>EduOS</strong> — Premium Educational Infrastructure Platform</p>
<p>Liquid Glass Design Language | Modular | AI-Enhanced | Enterprise-Ready</p></div></body></html>"""
        path.write_text(html)
        QMessageBox.information(self, "Documentation Generated",
            f"Liquid Glass presentation saved to:\n{path}")

    def _gen_screenshots(self):
        path = Path.home() / ".eduos" / "exports" / "eduos_liquid_glass_materials.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "=" * 60,
            "  EDUOS ECOSYSTEM — LIQUID GLASS PRESENTATION MATERIALS",
            "=" * 60,
            "",
            "  DESIGN SYSTEM OVERVIEW",
            "  ---------------------",
            "  Theme:           Liquid Glass (Frosted Glass + Dark Premium)",
            "  Background:      #0a0a14 (deep) → #0f0f1e (mid)",
            "  Glass Cards:     rgba(255,255,255,0.04) with border",
            "  Primary Accent:  #6c63ff → #4fc3f7 gradient",
            "  Secondary:       #b388ff (purple glow)",
            "  Tertiary:        #ff6b9d (pink accent)",
            "  Typography:      Inter / SF Pro Display",
            "  Corner Radius:   16px (cards), 10px (buttons)",
            "  Shadows:         20px blur, 4px offset, 40% black",
            "",
            "  BEFORE (Classic Theme):",
            "  - Light bg (#f1f5f9), white cards, hard edges",
            "  - Primary accent: #2563eb, flat shadows",
            "  - Standard Qt widgets, no blur effects",
            "  - 8px border radius, limited hover effects",
            "",
            "  AFTER (Liquid Glass):",
            "  - Dark premium bg (#0a0a14), frosted glass cards",
            "  - Gradient accents: #6c63ff → #4fc3f7 → #b388ff",
            "  - rgba(255,255,255,0.04) glass with border glow",
            "  - 16px rounded corners, QGraphicsDropShadowEffect",
            "  - Smooth hover transitions, glass borders",
            "  - Modern typography with letter-spacing",
            "  - Gradient progress bars, accent underlines",
            "",
            "  SCREENSHOT GUIDE",
            "  --------------",
            "  1: Dashboard — 5 KPI stat cards, device status, activity feed",
            "  2: Central Server — 3-tier architecture, simulation, device table",
            "  3: Module Store — 9 glass module cards with actions",
            "  4: Customization — Form + live preview with gradient",
            "  5: AI Assistant — 5 glass mode buttons, response area",
            "  6: Presentation — Enhanced glass step card with stats grid",
            "",
            "  PERFORMANCE NOTES",
            "  ----------------",
            "  - QGraphicsDropShadowEffect: 20px blur on ~20 cards",
            "  - All effects render in software (no compositor required)",
            "  - Same memory footprint as classic theme",
            "  - No additional CPU overhead on static widgets",
            "  - Glass effect uses rgba + borders (no real blur) for compatibility",
            "",
            "=" * 60,
        ]
        path.write_text("\n".join(lines))
        QMessageBox.information(self, "Materials Generated",
            f"Liquid Glass presentation materials saved to:\n{path}")


# ═══════════════════════════════════════════════════════════════
#  MAIN WINDOW — Liquid Glass Edition
# ═══════════════════════════════════════════════════════════════

class EcosystemMainWindow(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.setWindowTitle("EduOS Ecosystem Dashboard — Liquid Glass Edition")
        self.setGeometry(100, 50, 1400, 900)
        self.setMinimumSize(1100, 700)
        self._build()

    def _build(self):
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Glass navigation bar — floating on dark background
        nav = QFrame()
        nav.setStyleSheet(f"""
            background: {C.GLASS_DARK};
            border-bottom: 1px solid {C.GLASS_BORDER};
        """)
        nav.setFixedHeight(56)
        shadow = QGraphicsDropShadowEffect(nav)
        shadow.setBlurRadius(24)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 50))
        nav.setGraphicsEffect(shadow)

        nl = QHBoxLayout(nav)
        nl.setContentsMargins(24, 0, 24, 0)

        # Logo area
        logo = QLabel("◆ EduOS")
        logo.setStyleSheet(f"""
            font-size: 18px; font-weight: 800; color: {C.TEXT_PRIMARY};
            font-family: {T.FAMILY}; letter-spacing: -0.5px;
        """)
        nl.addWidget(logo)

        # Accent dot
        dot = QLabel("●")
        dot.setStyleSheet(f"font-size: 8px; color: {C.ACCENT_PRIMARY}; margin: 0 4px;")
        nl.addWidget(dot)

        version = QLabel("Liquid Glass v2.0")
        version.setStyleSheet(f"""
            font-size: 11px; color: {C.TEXT_MUTED};
            font-family: {T.FAMILY};
            padding: 2px 10px;
            border: 1px solid {C.GLASS_BORDER};
            border-radius: 10px;
        """)
        nl.addWidget(version)

        nl.addStretch()
        inst = self.data["institution"]
        inst_info = QLabel(f"{inst['name']}  |  {inst['students']:,} Students  |  {inst['total_devices']:,} Devices")
        inst_info.setStyleSheet(f"""
            font-size: 12px; color: {C.TEXT_MUTED};
            font-family: {T.FAMILY};
        """)
        nl.addWidget(inst_info)
        layout.addWidget(nav)

        # Tabs with glass styling
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: none; background: transparent; }}
            QTabBar::tab {{
                padding: 14px 24px; font-size: 13px; font-weight: 600;
                color: {C.TEXT_MUTED}; background: transparent;
                border: none; border-bottom: 2px solid transparent;
                font-family: {T.FAMILY}; transition: all 0.2s ease;
            }}
            QTabBar::tab:selected {{
                color: {C.ACCENT_PRIMARY};
                border-bottom: 2px solid {C.ACCENT_PRIMARY};
                background: rgba(108, 99, 255, 0.06);
            }}
            QTabBar::tab:hover {{
                color: {C.TEXT_PRIMARY};
                background: rgba(255, 255, 255, 0.04);
            }}
        """)

        self.tabs.addTab(EcosystemDashboard(self.data), "📊 Dashboard")
        self.tabs.addTab(CentralServerSimulation(self.data), "☁️ Central Server")
        self.tabs.addTab(ModuleManagement(self.data), "🧩 Modules")
        self.tabs.addTab(InstitutionCustomization(self.data), "🎨 Customization")
        self.tabs.addTab(AIAssistant(self.data), "🤖 AI Assistant")
        self.tabs.addTab(PresentationMode(self.data), "🎬 Presentation")

        layout.addWidget(self.tabs, 1)

        # Glass status bar
        health = self.data.get("health", {})
        self.statusBar().showMessage(
            f"🏫 {inst['name']}  |  "
            f"🎓 {inst['students']:,} Students  |  "
            f"💻 {inst['online_devices']:,}/{inst['total_devices']:,} Online  |  "
            f"🛡️ Health: {health.get('security_score', 96)}%  |  "
            f"📦 {len(self.data.get('updates', []))} Updates Available  |  "
            f"EduOS Liquid Glass v2.0"
        )
        self.statusBar().setStyleSheet(f"""
            background: {C.GLASS_DARK};
            color: {C.TEXT_MUTED};
            font-size: 12px; padding: 6px 20px;
            font-family: {T.FAMILY};
            border-top: 1px solid {C.GLASS_BORDER};
        """)

    @staticmethod
    def _label(text, style):
        l = QLabel(text)
        l.setStyleSheet(style)
        return l


# ═══════════════════════════════════════════════════════════════
#  IMPORTS FOR MAIN WINDOW
# ═══════════════════════════════════════════════════════════════

from PyQt6.QtWidgets import QGraphicsDropShadowEffect


# ─── Entry Point ──────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Apply EduOS Liquid Glass global stylesheet
    apply_glass_theme(app)

    font = QFont("Inter", 10)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)

    # Generate or load data
    if not (DATA_DIR / "ecosystem_data.json").exists():
        generate_all()
        print("Demo data generated.")

    data = load_data()

    window = EcosystemMainWindow(data)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
