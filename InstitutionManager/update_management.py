"""
EduOS Institution Manager — Update Management Tab
"""

import sys
from pathlib import Path
_DIR = Path(__file__).parent
if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QMessageBox, QScrollArea, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer

from styles import *
from ui_components import Card, SectionTitle, TableWidget, ActionBar, StatusBadge, btn_primary, btn_outline, btn_danger
from config import load_json, save_json, PATHS, log_activity


class UpdateManagementTab(QWidget):
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
        header.setStyleSheet(f"background: linear-gradient(135deg, {DANGER}, #7f1d1d); border-radius: 16px; padding: 20px;")
        hl = QHBoxLayout(header)
        ht = QVBoxLayout()
        ti = QLabel("🔄 Update & Security Management")
        ti.setStyleSheet("font-size: 22px; font-weight: 700; color: white;")
        ht.addWidget(ti)
        su = QLabel("Manage system updates, security patches, and software distribution across all institutional devices.")
        su.setStyleSheet("font-size: 13px; color: rgba(255,255,255,0.75);")
        su.setWordWrap(True)
        ht.addWidget(su)
        hl.addLayout(ht, 1)

        sys_stat = QFrame()
        sys_stat.setStyleSheet("background: rgba(255,255,255,0.15); border-radius: 10px; padding: 12px;")
        sl = QVBoxLayout(sys_stat)
        updates = load_json(PATHS["updates"], [])
        available = sum(1 for u in updates if u["status"] == "Available")
        critical = sum(1 for u in updates if u.get("critical") and u["status"] == "Available")

        sl.addWidget(QLabel(f"System Status"))
        sl.itemAt(0).widget().setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.7);")
        sl.addWidget(QLabel(f"{available} updates available"))
        sl.itemAt(1).widget().setStyleSheet("font-size: 18px; font-weight: 700; color: white;")
        if critical:
            sl.addWidget(QLabel(f"⚠ {critical} critical security updates"))
            sl.itemAt(2).widget().setStyleSheet("font-size: 12px; color: #fca5a5;")
        hl.addWidget(sys_stat)
        content.addWidget(header)

        # Action bar
        bar = ActionBar("Available Updates")
        bar.add_button("Check for Updates", "🔄", self._check_updates)
        bar.add_button("Install All", "📥", self._install_all, btn_success())
        content.addWidget(bar)

        # Update list
        for u in updates:
            card = QFrame()
            is_avail = u["status"] == "Available"
            is_critical = u.get("critical", False)
            card.setStyleSheet(f"""
                background: white; border: 1px solid {'#fecaca' if is_critical and is_avail else BORDER};
                border-radius: 12px; padding: 16px;
                border-left: 4px solid {DANGER if is_critical and is_avail else SUCCESS if u['status']=='Installed' else WARNING};
            """)
            cl = QVBoxLayout(card)
            cl.setSpacing(6)

            row = QHBoxLayout()
            pkg = QLabel(f"{'🔴' if is_critical else '🔵'} {u['package']}")
            pkg.setStyleSheet(f"font-size: 15px; font-weight: 600; color: {TEXT_PRIMARY};")
            row.addWidget(pkg)

            ver = QLabel(f"v{u['version']}")
            ver.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED}; padding: 2px 8px; background: {BG_SECTION}; border-radius: 4px;")
            row.addWidget(ver)

            size = QLabel(f"{u['size_mb']} MB")
            size.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED};")
            row.addWidget(size)

            st = StatusBadge(u["status"], "success" if u["status"] == "Installed" else "danger" if u["status"] == "Available" else "warning")
            row.addWidget(st)

            if is_critical:
                cs = StatusBadge("Critical", "danger")
                row.addWidget(cs)

            row.addStretch()
            cl.addLayout(row)

            desc = QLabel(u["description"])
            desc.setStyleSheet(f"font-size: 12px; color: {TEXT_SECONDARY};")
            desc.setWordWrap(True)
            cl.addWidget(desc)

            if is_avail:
                btn_row = QHBoxLayout()
                btn_install = QPushButton("📥 Install")
                btn_install.setStyleSheet(btn_small())
                btn_install.clicked.connect(lambda checked, p=u["id"]: self._install_update(p))
                btn_row.addWidget(btn_install)
                btn_row.addStretch()
                cl.addLayout(btn_row)

            if u["devices_updated"]:
                prog = QProgressBar()
                prog.setValue(min(100, u["devices_updated"]))
                prog.setFormat(f"Deployed to {u['devices_updated']} devices")
                prog.setStyleSheet("QProgressBar { background: #e2e8f0; border: none; border-radius: 4px; height: 6px; text-align: center; font-size: 10px; color: #64748b; } QProgressBar::chunk { background: #2563eb; border-radius: 4px; }")
                cl.addWidget(prog)

            content.addWidget(card)

        content.addStretch()
        layout.addWidget(scroll)

    def _check_updates(self):
        QMessageBox.information(self, "Check Updates", "Update check initiated. Scanning repositories...\n\nNo new updates found (all up to date).")

    def _install_all(self):
        QMessageBox.information(self, "Install All", "Queuing all available updates for installation...\n\nUpdates will be installed in sequence. Estimated time: 5 minutes.")

    def _install_update(self, pkg_id):
        updates = load_json(PATHS["updates"], [])
        for u in updates:
            if u["id"] == pkg_id and u["status"] == "Available":
                u["status"] = "Installed"
                u["devices_updated"] = u["devices_updated"] + 50
                save_json(PATHS["updates"], updates)
                log_activity("Update Installed", f"{u['package']} v{u['version']}")
                QMessageBox.information(self, "Update", f"{u['package']} v{u['version']} installed successfully.")
                self._rebuild()
                return
        QMessageBox.information(self, "Update", "Update already installed or not found.")

    def _rebuild(self):
        parent = self.parent()
        if parent:
            idx = parent.indexOf(self)
            if idx >= 0:
                parent.removeTab(idx)
                new_tab = UpdateManagementTab(parent)
                parent.insertTab(idx, new_tab, "🔄 Updates")
                parent.setCurrentIndex(idx)
