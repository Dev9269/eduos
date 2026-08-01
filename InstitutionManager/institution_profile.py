"""
EduOS Institution Manager — Institution Profile & Branding Tab
"""

import sys
from pathlib import Path
_DIR = Path(__file__).parent
if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QFormLayout, QGroupBox, QScrollArea, QFrame, QFileDialog,
    QMessageBox, QColorDialog, QSpinBox
)
from PyQt6.QtCore import Qt

from styles import *
from ui_components import Card, SectionTitle, ActionBar, btn_primary, btn_outline, btn_small, btn_danger
from config import institution_config, save_institution, branding_config, save_branding, log_activity


class InstitutionProfileTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_w = QWidget()
        scroll.setWidget(scroll_w)
        content = QVBoxLayout(scroll_w)
        content.setSpacing(16)

        # Institution Details
        details_card = QFrame()
        details_card.setStyleSheet(card_style())
        details_layout = QVBoxLayout(details_card)
        details_layout.setSpacing(12)

        dt = QLabel("🏛️ Institution Details")
        dt.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {TEXT_PRIMARY};")
        details_layout.addWidget(dt)

        form = QFormLayout()
        form.setSpacing(8)
        form.setContentsMargins(0, 8, 0, 0)

        cfg = institution_config()
        self.cfg = cfg

        self.name_edit = QLineEdit(cfg["name"])
        form.addRow("Institution Name:", self.name_edit)

        self.type_combo = QLineEdit(cfg["type"])
        form.addRow("Institution Type:", self.type_combo)

        self.address_edit = QLineEdit(cfg["address"])
        form.addRow("Address:", self.address_edit)

        self.city_edit = QLineEdit(cfg["city"])
        form.addRow("City:", self.city_edit)

        self.country_edit = QLineEdit(cfg["country"])
        form.addRow("Country:", self.country_edit)

        self.phone_edit = QLineEdit(cfg["phone"])
        form.addRow("Phone:", self.phone_edit)

        self.email_edit = QLineEdit(cfg["email"])
        form.addRow("Email:", self.email_edit)

        self.website_edit = QLineEdit(cfg["website"])
        form.addRow("Website:", self.website_edit)

        self.established_edit = QLineEdit(str(cfg["established"]))
        form.addRow("Established:", self.established_edit)

        self.accred_edit = QLineEdit(cfg["accreditation"])
        form.addRow("Accreditation:", self.accred_edit)

        self.principal_edit = QLineEdit(cfg["principal"])
        form.addRow("Principal/Vice-Chancellor:", self.principal_edit)

        details_layout.addLayout(form)

        save_btn = QPushButton("💾 Save Institution Details")
        save_btn.clicked.connect(self._save_details)
        save_btn.setStyleSheet(btn_primary())
        details_layout.addWidget(save_btn)

        content.addWidget(details_card)

        # Branding Card
        brand_card = QFrame()
        brand_card.setStyleSheet(card_style())
        brand_layout = QVBoxLayout(brand_card)
        brand_layout.setSpacing(12)

        bt = QLabel("🎨 Institution Branding")
        bt.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {TEXT_PRIMARY};")
        brand_layout.addWidget(bt)

        b_cfg = branding_config()
        self.b_cfg = b_cfg

        b_form = QFormLayout()
        b_form.setSpacing(8)
        b_form.setContentsMargins(0, 8, 0, 0)

        self.brand_name = QLineEdit(b_cfg["institution_name"])
        b_form.addRow("Brand Name:", self.brand_name)

        self.short_name = QLineEdit(b_cfg["short_name"])
        b_form.addRow("Short Name:", self.short_name)

        # Color picker buttons
        color_row = QHBoxLayout()
        self.primary_color_btn = QPushButton(f"  Primary Color  ")
        self.primary_color_btn.setStyleSheet(f"background: {b_cfg['primary_color']}; color: white; padding: 8px 16px; border: none; border-radius: 6px; font-weight: 600;")
        self.primary_color_btn.clicked.connect(lambda: self._pick_color("primary"))
        color_row.addWidget(self.primary_color_btn)

        self.secondary_color_btn = QPushButton(f"  Secondary Color  ")
        self.secondary_color_btn.setStyleSheet(f"background: {b_cfg['secondary_color']}; color: white; padding: 8px 16px; border: none; border-radius: 6px; font-weight: 600;")
        self.secondary_color_btn.clicked.connect(lambda: self._pick_color("secondary"))
        color_row.addWidget(self.secondary_color_btn)

        color_row.addWidget(QLabel("Click to change"))
        b_form.addRow("Theme Colors:", color_row)

        self.login_msg = QLineEdit(b_cfg["login_message"])
        b_form.addRow("Login Message:", self.login_msg)

        self.welcome_title = QLineEdit(b_cfg["welcome_title"])
        b_form.addRow("Welcome Title:", self.welcome_title)

        self.welcome_sub = QLineEdit(b_cfg["welcome_subtitle"])
        b_form.addRow("Welcome Subtitle:", self.welcome_sub)

        brand_layout.addLayout(b_form)

        save_brand_btn = QPushButton("💾 Save Branding")
        save_brand_btn.setStyleSheet(btn_primary())
        save_brand_btn.clicked.connect(self._save_branding)
        brand_layout.addWidget(save_brand_btn)

        content.addWidget(brand_card)

        # Preview section
        preview_card = QFrame()
        preview_card.setStyleSheet(card_style())
        preview_layout = QVBoxLayout(preview_card)
        pt = QLabel("👁 Branding Preview")
        pt.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {TEXT_PRIMARY};")
        preview_layout.addWidget(pt)

        preview_w = QFrame()
        preview_w.setStyleSheet(f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {b_cfg['primary_color']}, stop:1 {b_cfg['secondary_color']}); border-radius: 12px; padding: 24px;")
        pl = QVBoxLayout(preview_w)
        pi = QLabel(f"🏫 {b_cfg['institution_name']} EduOS")
        pi.setStyleSheet("font-size: 20px; font-weight: 700; color: white;")
        pl.addWidget(pi)
        ps = QLabel(b_cfg['welcome_subtitle'])
        ps.setStyleSheet("font-size: 13px; color: rgba(255,255,255,0.8);")
        pl.addWidget(ps)
        pm = QLabel(f"\"{b_cfg['login_message']}\"")
        pm.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.6); font-style: italic; padding-top: 8px;")
        pl.addWidget(pm)
        preview_layout.addWidget(preview_w)

        content.addWidget(preview_card)

        content.addStretch()
        layout.addWidget(scroll)

    def _save_details(self):
        self.cfg.update({
            "name": self.name_edit.text(),
            "type": self.type_combo.text(),
            "address": self.address_edit.text(),
            "city": self.city_edit.text(),
            "country": self.country_edit.text(),
            "phone": self.phone_edit.text(),
            "email": self.email_edit.text(),
            "website": self.website_edit.text(),
            "established": self.established_edit.text(),
            "accreditation": self.accred_edit.text(),
            "principal": self.principal_edit.text()
        })
        save_institution(self.cfg)
        log_activity("Institution Details Updated", "Institution profile modified")
        QMessageBox.information(self, "Saved", "Institution details saved successfully.")

    def _save_branding(self):
        self.b_cfg.update({
            "institution_name": self.brand_name.text(),
            "short_name": self.short_name.text(),
            "login_message": self.login_msg.text(),
            "welcome_title": self.welcome_title.text(),
            "welcome_subtitle": self.welcome_sub.text()
        })
        save_branding(self.b_cfg)
        log_activity("Branding Updated", "Institution branding modified")
        QMessageBox.information(self, "Saved", "Branding saved successfully.")

    def _pick_color(self, which):
        current = self.b_cfg["primary_color"] if which == "primary" else self.b_cfg["secondary_color"]
        color = QColorDialog.getColor(QColor(current), self, f"Choose {which.title()} Color")
        if color.isValid():
            hex_color = color.name()
            if which == "primary":
                self.b_cfg["primary_color"] = hex_color
                self.primary_color_btn.setStyleSheet(f"background: {hex_color}; color: white; padding: 8px 16px; border: none; border-radius: 6px; font-weight: 600;")
            else:
                self.b_cfg["secondary_color"] = hex_color
                self.secondary_color_btn.setStyleSheet(f"background: {hex_color}; color: white; padding: 8px 16px; border: none; border-radius: 6px; font-weight: 600;")
