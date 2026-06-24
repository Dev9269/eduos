"""
EduOS Institution Manager — Module Management Tab
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QMessageBox, QScrollArea, QDialog, QFormLayout, QTextEdit, QLineEdit
)
from PyQt6.QtCore import Qt

from styles import *
from ui_components import Card, SectionTitle, ActionBar, StatusBadge, btn_primary, btn_outline, btn_danger, btn_small
from module_registry import ModuleRegistry, MODULE_CATALOG


class ModuleManagementTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.registry = ModuleRegistry()
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
        content.setSpacing(12)

        # Header
        header = QWidget()
        header.setStyleSheet(f"background: linear-gradient(135deg, {PRIMARY}, {SECONDARY}); border-radius: 16px; padding: 20px;")
        hl = QHBoxLayout(header)
        ht = QVBoxLayout()
        ti = QLabel("🧩 EduOS Module System")
        ti.setStyleSheet("font-size: 22px; font-weight: 700; color: white;")
        ht.addWidget(ti)
        su = QLabel("Enable, disable, install, remove, and configure platform modules. Each module extends EduOS with new capabilities.")
        su.setStyleSheet("font-size: 13px; color: rgba(255,255,255,0.75);")
        su.setWordWrap(True)
        ht.addWidget(su)
        hl.addLayout(ht, 1)
        content.addWidget(header)

        # Stats
        modules = self.registry.list_modules()
        enabled = sum(1 for m in modules if m.get("enabled"))
        installed = sum(1 for m in modules if m.get("installed"))

        stats = QHBoxLayout()
        stats.setSpacing(12)
        for val, label, color in [
            (f"{installed}/{len(modules)}", "Modules Installed", SUCCESS),
            (f"{enabled}", "Currently Enabled", PRIMARY),
            (sum(1 for m in modules if not m.get("installed")), "Available", INFO)
        ]:
            card = QFrame()
            card.setStyleSheet(f"background: white; border: 1px solid {BORDER}; border-radius: 10px; padding: 12px 20px;")
            cl = QVBoxLayout(card)
            cl.setContentsMargins(8, 4, 8, 4)
            v = QLabel(str(val))
            v.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {color};")
            cl.addWidget(v)
            l = QLabel(label)
            l.setStyleSheet(f"font-size: 11px; color: {TEXT_SECONDARY};")
            cl.addWidget(l)
            stats.addWidget(card)
        stats.addStretch()
        content.addLayout(stats)

        # Module cards
        for mod in modules:
            card = QFrame()
            enabled = mod.get("enabled", False)
            installed = mod.get("installed", False)
            card.setStyleSheet(f"""
                background: white; border: 1px solid {BORDER}; border-radius: 12px; padding: 16px;
                border-left: 4px solid {SUCCESS if enabled else '#cbd5e1'};
            """)
            cl = QVBoxLayout(card)
            cl.setSpacing(8)

            # Header row
            row = QHBoxLayout()
            icon_map = {
                "learn_hub": "📚", "exam_hub": "📝", "dev_suite": "💻", "cyber_lab": "🛡️",
                "library": "📖", "attendance": "✅", "placement": "💼", "research": "🔬", "ai_assistant": "🤖"
            }
            icon = QLabel(icon_map.get(mod["id"], "📦"))
            icon.setStyleSheet("font-size: 28px;")
            row.addWidget(icon)

            texts = QVBoxLayout()
            texts.setSpacing(2)
            name = QLabel(mod["name"])
            name.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {TEXT_PRIMARY};")
            texts.addWidget(name)
            desc = QLabel(mod.get("description", ""))
            desc.setStyleSheet(f"font-size: 12px; color: {TEXT_SECONDARY};")
            desc.setWordWrap(True)
            texts.addWidget(desc)
            row.addLayout(texts, 1)

            # Version + status
            ver = QLabel(f"v{mod.get('version', '1.0')}")
            ver.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED}; padding: 2px 8px; background: {BG_SECTION}; border-radius: 4px;")
            row.addWidget(ver)

            cat = StatusBadge(mod.get("category", "General"), "info")
            row.addWidget(cat)

            if installed:
                st = StatusBadge("Enabled" if enabled else "Disabled", "success" if enabled else "inactive")
                row.addWidget(st)
            else:
                st = StatusBadge("Not Installed", "neutral")
                row.addWidget(st)

            cl.addLayout(row)

            # Dependencies
            deps = mod.get("dependencies", [])
            if deps:
                dep_text = f"Depends on: {', '.join(MODULE_CATALOG[d]['name'] for d in deps if d in MODULE_CATALOG)}"
                dl = QLabel(dep_text)
                dl.setStyleSheet(f"font-size: 11px; color: {TEXT_MUTED}; padding-left: 4px;")
                cl.addWidget(dl)

            # Action buttons
            actions = QHBoxLayout()
            mid = mod["id"]

            if not installed:
                btn_install = QPushButton("📥 Install")
                btn_install.setStyleSheet(btn_small())
                btn_install.clicked.connect(lambda checked, m=mid: self._install(m))
                actions.addWidget(btn_install)
            else:
                if enabled:
                    btn_disable = QPushButton("⏸ Disable")
                    btn_disable.setStyleSheet(f"QPushButton {{ background: {WARNING}; color: white; padding: 6px 12px; font-size: 12px; font-weight: 500; border: none; border-radius: 6px; }} QPushButton:hover {{ background: #d97706; }} QPushButton:pressed {{ padding: 7px 11px 5px 13px; }}")
                    btn_disable.clicked.connect(lambda checked, m=mid: self._disable(m))
                    actions.addWidget(btn_disable)
                else:
                    btn_enable = QPushButton("▶ Enable")
                    btn_enable.setStyleSheet(btn_small())
                    btn_enable.clicked.connect(lambda checked, m=mid: self._enable(m))
                    actions.addWidget(btn_enable)

                btn_configure = QPushButton("⚙ Configure")
                btn_configure.setStyleSheet(f"QPushButton {{ background: transparent; color: {TEXT_PRIMARY}; border: 1px solid {BORDER}; padding: 6px 12px; font-size: 12px; font-weight: 500; border-radius: 6px; }} QPushButton:hover {{ border-color: {PRIMARY}; color: {PRIMARY}; }} QPushButton:pressed {{ padding: 7px 11px 5px 13px; }}")
                btn_configure.clicked.connect(lambda checked, m=mid: self._configure(m))
                actions.addWidget(btn_configure)

                btn_remove = QPushButton("🗑 Remove")
                btn_remove.setStyleSheet(f"QPushButton {{ background: transparent; color: {DANGER}; border: 1px solid {DANGER}; padding: 6px 12px; font-size: 12px; font-weight: 500; border-radius: 6px; }} QPushButton:hover {{ background: {DANGER}; color: white; }} QPushButton:pressed {{ padding: 7px 11px 5px 13px; }}")
                btn_remove.clicked.connect(lambda checked, m=mid: self._remove(m))
                actions.addWidget(btn_remove)

            actions.addStretch()
            cl.addLayout(actions)

            content.addWidget(card)

        content.addStretch()
        layout.addWidget(scroll)

    def _enable(self, mid):
        ok, msg = self.registry.enable(mid)
        if ok:
            self._rebuild()
        QMessageBox.information(self, "Module", msg)

    def _disable(self, mid):
        ok, msg = self.registry.disable(mid)
        if ok:
            self._rebuild()
        QMessageBox.information(self, "Module", msg)

    def _install(self, mid):
        ok, msg = self.registry.install(mid)
        if ok:
            self._rebuild()
        QMessageBox.information(self, "Module", msg)

    def _remove(self, mid):
        ok, msg = self.registry.remove(mid)
        if ok:
            self._rebuild()
        else:
            QMessageBox.warning(self, "Cannot Remove", msg)

    def _configure(self, mid):
        mod = self.registry.get_module(mid)
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Configure: {mod['name']}")
        dlg.setFixedSize(500, 400)
        layout = QVBoxLayout(dlg)
        form = QFormLayout()
        config = mod.get("config", {})

        config_edit = QTextEdit()
        config_edit.setPlainText(str(config))
        form.addRow("Current Config:", config_edit)

        layout.addLayout(form)
        from PyQt6.QtWidgets import QDialogButtonBox
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        layout.addWidget(buttons)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.registry.configure(mid, {"configured": True, "notes": "User-configured"})
            QMessageBox.information(self, "Configured", f"{mod['name']} configuration saved.")

    def _rebuild(self):
        parent = self.parent()
        if parent:
            idx = parent.indexOf(self)
            if idx >= 0:
                parent.removeTab(idx)
                new_tab = ModuleManagementTab(parent)
                parent.insertTab(idx, new_tab, "🧩 Modules")
                parent.setCurrentIndex(idx)
