"""
EduOS Design System — Liquid Glass Design Language
Premium, modern aesthetic inspired by glassmorphism, fluent design, and material you.
"""

from PyQt6.QtWidgets import (
    QFrame, QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout,
    QGraphicsDropShadowEffect, QScrollArea
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QLinearGradient, QBrush, QPen, QFontDatabase


# ═══════════════════════════════════════════════════════════════
#  EDUOS COLOR PALETTE — Liquid Glass Edition
# ═══════════════════════════════════════════════════════════════

class EduOSColors:
    # Core backgrounds
    BG_DEEP = "#0a0a14"           # Deepest background
    BG_DARK = "#0f0f1e"           # Main app background  
    BG_MID = "#1a1a2e"            # Card/surface background
    BG_LIGHT = "#252540"          # Elevated surface

    # Glass effects (RGBA strings for frosted glass)
    GLASS_DARK = "rgba(15, 15, 30, 0.55)"
    GLASS_MID = "rgba(26, 26, 46, 0.65)"
    GLASS_LIGHT = "rgba(37, 37, 64, 0.45)"
    GLASS_CARD = "rgba(255, 255, 255, 0.04)"
    GLASS_CARD_HOVER = "rgba(255, 255, 255, 0.08)"
    GLASS_BORDER = "rgba(255, 255, 255, 0.08)"
    GLASS_BORDER_HOVER = "rgba(255, 255, 255, 0.15)"

    # Accent colors
    ACCENT_PRIMARY = "#6c63ff"     # Primary brand accent
    ACCENT_SECONDARY = "#4fc3f7"   # Secondary accent
    ACCENT_TERTIARY = "#ff6b9d"    # Tertiary accent
    ACCENT_GREEN = "#4caf50"       # Success
    ACCENT_AMBER = "#ffc107"       # Warning
    ACCENT_RED = "#ef5350"         # Danger
    ACCENT_PURPLE = "#b388ff"      # Info/Purple accent
    ACCENT_CYAN = "#26c6da"        # Info/Cyan

    # Text colors
    TEXT_PRIMARY = "rgba(255, 255, 255, 0.92)"
    TEXT_SECONDARY = "rgba(255, 255, 255, 0.65)"
    TEXT_MUTED = "rgba(255, 255, 255, 0.38)"
    TEXT_ACCENT = "#6c63ff"

    # Gradient definitions
    @staticmethod
    def gradient_primary():
        return "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6c63ff, stop:1 #4fc3f7)"

    @staticmethod
    def gradient_dark():
        return "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0a0a14, stop:1 #0f0f1e)"

    @staticmethod
    def gradient_card():
        return "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255,255,255,0.06), stop:1 rgba(255,255,255,0.02))"

    @staticmethod
    def gradient_accent():
        return "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6c63ff, stop:0.5 #b388ff, stop:1 #4fc3f7)"


# ═══════════════════════════════════════════════════════════════
#  TYPOGRAPHY STANDARDS
# ═══════════════════════════════════════════════════════════════

class EduOSTypography:
    FAMILY = "'Inter', 'SF Pro Display', 'Segoe UI', system-ui, sans-serif"
    MONO = "'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace"

    # Font sizes
    H1 = "28px"
    H2 = "22px"
    H3 = "18px"
    H4 = "15px"
    BODY = "13px"
    SMALL = "11px"
    TINY = "10px"

    # Weights
    THIN = "300"
    REGULAR = "400"
    MEDIUM = "500"
    SEMIBOLD = "600"
    BOLD = "700"

    @staticmethod
    def h1_style():
        return f"font-family: {EduOSTypography.FAMILY}; font-size: {EduOSTypography.H1}; font-weight: {EduOSTypography.BOLD}; color: {EduOSColors.TEXT_PRIMARY}; letter-spacing: -0.5px;"

    @staticmethod
    def h2_style():
        return f"font-family: {EduOSTypography.FAMILY}; font-size: {EduOSTypography.H2}; font-weight: {EduOSTypography.SEMIBOLD}; color: {EduOSColors.TEXT_PRIMARY}; letter-spacing: -0.3px;"

    @staticmethod
    def h3_style():
        return f"font-family: {EduOSTypography.FAMILY}; font-size: {EduOSTypography.H3}; font-weight: {EduOSTypography.MEDIUM}; color: {EduOSColors.TEXT_PRIMARY};"

    @staticmethod
    def body_style():
        return f"font-family: {EduOSTypography.FAMILY}; font-size: {EduOSTypography.BODY}; font-weight: {EduOSTypography.REGULAR}; color: {EduOSColors.TEXT_SECONDARY};"

    @staticmethod
    def caption_style():
        return f"font-family: {EduOSTypography.FAMILY}; font-size: {EduOSTypography.SMALL}; font-weight: {EduOSTypography.REGULAR}; color: {EduOSColors.TEXT_MUTED};"


# ═══════════════════════════════════════════════════════════════
#  GLOBAL STYLESHEET — Applied to QApplication
# ═══════════════════════════════════════════════════════════════

LIQUID_GLASS_STYLESHEET = f"""
QMainWindow, QWidget#central {{
    background: {EduOSColors.BG_DARK};
}}

QTabWidget::pane {{
    border: none;
    background: transparent;
}}

QTabBar::tab {{
    padding: 12px 24px;
    font-size: 13px;
    font-weight: 600;
    color: {EduOSColors.TEXT_MUTED};
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    font-family: {EduOSTypography.FAMILY};
}}

QTabBar::tab:selected {{
    color: {EduOSColors.ACCENT_PRIMARY};
    border-bottom: 2px solid {EduOSColors.ACCENT_PRIMARY};
    background: rgba(108, 99, 255, 0.06);
}}

QTabBar::tab:hover {{
    color: {EduOSColors.TEXT_PRIMARY};
    background: rgba(255, 255, 255, 0.04);
}}

QPushButton {{
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 600;
    font-family: {EduOSTypography.FAMILY};
    color: {EduOSColors.TEXT_PRIMARY};
}}

QPushButton:hover {{
    opacity: 0.9;
}}

QPushButton:pressed {{
    padding: 11px 19px 9px 21px;
}}

QTableWidget {{
    border: 1px solid {EduOSColors.GLASS_BORDER};
    border-radius: 12px;
    background: {EduOSColors.GLASS_CARD};
    gridline-color: rgba(255, 255, 255, 0.04);
    font-size: 13px;
    font-family: {EduOSTypography.FAMILY};
    color: {EduOSColors.TEXT_PRIMARY};
}}

QTableWidget::item {{
    padding: 10px 14px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}}

QTableWidget::item:selected {{
    background: rgba(108, 99, 255, 0.15);
    color: white;
}}

QHeaderView::section {{
    background: rgba(255, 255, 255, 0.03);
    padding: 12px 14px;
    font-weight: 600;
    font-size: 12px;
    color: {EduOSColors.TEXT_SECONDARY};
    border: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    font-family: {EduOSTypography.FAMILY};
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QLineEdit, QTextEdit, QSpinBox, QComboBox {{
    border: 1px solid {EduOSColors.GLASS_BORDER};
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    font-family: {EduOSTypography.FAMILY};
    background: rgba(255, 255, 255, 0.04);
    color: {EduOSColors.TEXT_PRIMARY};
}}

QLineEdit:focus, QTextEdit:focus {{
    border-color: {EduOSColors.ACCENT_PRIMARY};
    background: rgba(108, 99, 255, 0.06);
}}

QGroupBox {{
    font-weight: 600;
    font-size: 14px;
    border: 1px solid {EduOSColors.GLASS_BORDER};
    border-radius: 12px;
    margin-top: 12px;
    padding: 20px 16px 16px 16px;
    background: {EduOSColors.GLASS_CARD};
    font-family: {EduOSTypography.FAMILY};
    color: {EduOSColors.TEXT_PRIMARY};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
    color: {EduOSColors.TEXT_SECONDARY};
}}

QProgressBar {{
    background: rgba(255, 255, 255, 0.06);
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
    font-size: 10px;
    color: {EduOSColors.TEXT_MUTED};
}}

QProgressBar::chunk {{
    background: {EduOSColors.gradient_primary()};
    border-radius: 4px;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    border-radius: 3px;
}}

QScrollBar::handle:vertical {{
    background: rgba(255, 255, 255, 0.15);
    border-radius: 3px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: rgba(255, 255, 255, 0.25);
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollArea {{
    border: none;
    background: transparent;
}}
"""


# ═══════════════════════════════════════════════════════════════
#  REUSABLE COMPONENT STYLES
# ═══════════════════════════════════════════════════════════════

def glass_card_style():
    """Frosted glass card with subtle border and gradient."""
    return f"""
        background: {EduOSColors.GLASS_CARD};
        border: 1px solid {EduOSColors.GLASS_BORDER};
        border-radius: 16px;
        padding: 20px;
    """


def glass_card_hover_style():
    return f"""
        background: {EduOSColors.GLASS_CARD_HOVER};
        border: 1px solid {EduOSColors.GLASS_BORDER_HOVER};
        border-radius: 16px;
        padding: 20px;
    """


def glass_stat_card_style():
    return f"""
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(108, 99, 255, 0.06),
            stop:1 rgba(79, 195, 247, 0.03));
        border: 1px solid {EduOSColors.GLASS_BORDER};
        border-radius: 14px;
        padding: 16px;
    """


def glass_banner_style():
    return f"""
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #1a1a2e, stop:0.5 #0f0f1e, stop:1 #0a0a14);
        border: 1px solid {EduOSColors.GLASS_BORDER};
        border-radius: 18px;
        padding: 24px;
    """


def accent_glow_style():
    """Glassy accent button."""
    return f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #6c63ff, stop:1 #4fc3f7);
            color: white; padding: 10px 24px;
            font-size: 13px; font-weight: 600;
            border: none; border-radius: 10px;
            font-family: {EduOSTypography.FAMILY};
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #7c73ff, stop:1 #5fd3ff);
        }}
        QPushButton:pressed {{
            padding: 11px 23px 9px 25px;
        }}
    """


def glass_button_style():
    """Glass outline button."""
    return f"""
        QPushButton {{
            background: rgba(255, 255, 255, 0.04);
            color: {EduOSColors.TEXT_PRIMARY};
            border: 1px solid {EduOSColors.GLASS_BORDER};
            padding: 10px 24px;
            font-size: 13px; font-weight: 500;
            border-radius: 10px;
            font-family: {EduOSTypography.FAMILY};
        }}
        QPushButton:hover {{
            background: rgba(108, 99, 255, 0.1);
            border-color: {EduOSColors.ACCENT_PRIMARY};
        }}
        QPushButton:pressed {{
            padding: 11px 23px 9px 25px;
        }}
    """


def glass_success_button_style():
    return f"""
        QPushButton {{
            background: rgba(76, 175, 80, 0.2);
            color: #81c784;
            border: 1px solid rgba(76, 175, 80, 0.3);
            padding: 8px 16px;
            font-size: 12px; font-weight: 600;
            border-radius: 8px;
        }}
        QPushButton:hover {{
            background: rgba(76, 175, 80, 0.3);
        }}
        QPushButton:pressed {{
            padding: 9px 15px 7px 17px;
        }}
    """


def glass_danger_button_style():
    return f"""
        QPushButton {{
            background: rgba(239, 83, 80, 0.15);
            color: #ef9a9a;
            border: 1px solid rgba(239, 83, 80, 0.3);
            padding: 8px 16px;
            font-size: 12px; font-weight: 600;
            border-radius: 8px;
        }}
        QPushButton:hover {{
            background: rgba(239, 83, 80, 0.25);
        }}
        QPushButton:pressed {{
            padding: 9px 15px 7px 17px;
        }}
    """


def glass_warning_button_style():
    return f"""
        QPushButton {{
            background: rgba(255, 193, 7, 0.15);
            color: #ffd54f;
            border: 1px solid rgba(255, 193, 7, 0.3);
            padding: 8px 16px;
            font-size: 12px; font-weight: 600;
            border-radius: 8px;
        }}
        QPushButton:hover {{
            background: rgba(255, 193, 7, 0.25);
        }}
        QPushButton:pressed {{
            padding: 9px 15px 7px 17px;
        }}
    """


def status_badge_style(stype="info"):
    styles = {
        "success": ("rgba(76, 175, 80, 0.15)", "#81c784"),
        "danger": ("rgba(239, 83, 80, 0.15)", "#ef9a9a"),
        "warning": ("rgba(255, 193, 7, 0.15)", "#ffd54f"),
        "info": ("rgba(108, 99, 255, 0.15)", "#b388ff"),
        "neutral": ("rgba(255, 255, 255, 0.06)", "#9e9e9e"),
        "active": ("rgba(76, 175, 80, 0.15)", "#81c784"),
        "inactive": ("rgba(255, 255, 255, 0.04)", "#616161"),
        "installed": ("rgba(76, 175, 80, 0.15)", "#81c784"),
        "not_installed": ("rgba(255, 255, 255, 0.04)", "#616161"),
        "available": ("rgba(108, 99, 255, 0.15)", "#b388ff"),
        "online": ("rgba(76, 175, 80, 0.15)", "#81c784"),
        "offline": ("rgba(239, 83, 80, 0.15)", "#ef9a9a"),
    }
    bg, fg = styles.get(stype, styles["info"])
    return f"background: {bg}; color: {fg}; padding: 3px 12px; border-radius: 10px; font-size: 11px; font-weight: 600; border: 1px solid rgba(255,255,255,0.06);"


# ═══════════════════════════════════════════════════════════════
#  REUSABLE UI COMPONENTS
# ═══════════════════════════════════════════════════════════════

class GlassCard(QFrame):
    """Frosted glass card with shadow and hover effect."""

    clicked = pyqtSignal()

    def __init__(self, parent=None, clickable=False):
        super().__init__(parent)
        self.setStyleSheet(glass_card_style())
        self._add_shadow()
        if clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _add_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event):
        self.setStyleSheet(glass_card_hover_style())
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(glass_card_style())
        super().leaveEvent(event)


class GlassStatCard(QFrame):
    """Glass KPI stat card with accent gradient."""

    def __init__(self, value, label, icon="", sublabel="", parent=None):
        super().__init__(parent)
        self.setStyleSheet(glass_stat_card_style())
        self._add_shadow()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(4)

        top = QHBoxLayout()
        v = QLabel(str(value))
        v.setStyleSheet(f"font-size: 30px; font-weight: 700; color: {EduOSColors.TEXT_PRIMARY}; font-family: {EduOSTypography.FAMILY}; letter-spacing: -1px;")
        top.addWidget(v)
        if icon:
            i = QLabel(icon)
            i.setStyleSheet("font-size: 24px;")
            i.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            top.addWidget(i, 1)
        layout.addLayout(top)

        l = QLabel(label)
        l.setStyleSheet(f"font-size: 12px; color: {EduOSColors.TEXT_SECONDARY}; font-weight: 500; font-family: {EduOSTypography.FAMILY};")
        layout.addWidget(l)

        if sublabel:
            s = QLabel(sublabel)
            s.setStyleSheet(f"font-size: 10px; color: {EduOSColors.TEXT_MUTED}; font-family: {EduOSTypography.FAMILY};")
            layout.addWidget(s)

    def _add_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)


class GlassBanner(QFrame):
    """Large glass banner with gradient background for page headers."""

    def __init__(self, title, subtitle="", parent=None):
        super().__init__(parent)
        self.setStyleSheet(glass_banner_style())
        self._add_shadow()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(28, 22, 28, 22)

        texts = QVBoxLayout()
        texts.setSpacing(4)
        t = QLabel(title)
        t.setStyleSheet(EduOSTypography.h1_style())
        texts.addWidget(t)
        if subtitle:
            s = QLabel(subtitle)
            s.setStyleSheet(EduOSTypography.body_style())
            s.setWordWrap(True)
            texts.addWidget(s)
        layout.addLayout(texts, 1)

    def _add_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setXOffset(0)
        shadow.setYOffset(6)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(shadow)


class SectionTitle(QLabel):
    """Styled section title with accent underline."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            font-size: 18px; font-weight: 700;
            color: {EduOSColors.TEXT_PRIMARY};
            font-family: {EduOSTypography.FAMILY};
            letter-spacing: -0.3px;
            padding: 4px 0;
        """)


class GlassTable(QFrame):
    """Glass-styled table with shadow."""

    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.setStyleSheet(glass_card_style())
        self._add_shadow()

        from PyQt6.QtWidgets import QTableWidget, QHeaderView
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)

        # Apply glass style
        self.table.setStyleSheet(f"""
            QTableWidget {{
                border: none; border-radius: 12px;
                background: transparent;
                gridline-color: transparent;
                font-size: 13px;
                font-family: {EduOSTypography.FAMILY};
                color: {EduOSColors.TEXT_PRIMARY};
            }}
            QTableWidget::item {{
                padding: 10px 14px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            }}
            QTableWidget::item:selected {{
                background: rgba(108, 99, 255, 0.15);
                color: white;
            }}
            QHeaderView::section {{
                background: transparent;
                padding: 12px 14px;
                font-weight: 600;
                font-size: 11px;
                color: {EduOSColors.TEXT_SECONDARY};
                border: none;
                border-bottom: 1px solid rgba(255, 255, 255, 0.06);
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
        """)
        layout.addWidget(self.table)

    def _add_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)

    def add_row(self, values):
        row = self.table.rowCount()
        self.table.insertRow(row)
        for col, val in enumerate(values):
            from PyQt6.QtWidgets import QTableWidgetItem
            item = QTableWidgetItem(str(val))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, col, item)
        return row

    @property
    def rowCount(self):
        return self.table.rowCount


def StatusBadge(text, stype="info"):
    """Create a glass status badge label."""
    label = QLabel(text)
    label.setStyleSheet(status_badge_style(stype))
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return label


# ═══════════════════════════════════════════════════════════════
#  ANIMATION HELPERS
# ═══════════════════════════════════════════════════════════════

class FadeInAnimation:
    """Smooth opacity fade-in for widgets."""

    @staticmethod
    def apply(widget, duration=300):
        anim = QPropertyAnimation(widget, b"windowOpacity")
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()


def apply_glass_theme(app):
    """Apply the Liquid Glass global stylesheet to the application."""
    app.setStyleSheet(LIQUID_GLASS_STYLESHEET)
