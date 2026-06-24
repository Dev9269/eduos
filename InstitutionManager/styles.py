"""
EduOS Institution Manager — Shared Styles & Color Palette
"""

PRIMARY = "#2563eb"
PRIMARY_DARK = "#1e40af"
PRIMARY_LIGHT = "#dbeafe"
SECONDARY = "#0f172a"
ACCENT = "#f59e0b"
SUCCESS = "#16a34a"
DANGER = "#dc2626"
WARNING = "#f59e0b"
INFO = "#0891b2"
BG_DARK = "#0f172a"
BG_CARD = "#ffffff"
BG_SECTION = "#f8fafc"
TEXT_PRIMARY = "#1e293b"
TEXT_SECONDARY = "#64748b"
TEXT_MUTED = "#94a3b8"
BORDER = "#e2e8f0"

APP_STYLESHEET = """
QMainWindow, QWidget#centralWidget { background: #f1f5f9; }
QTabWidget::pane { border: none; background: transparent; }
QTabBar::tab { padding: 10px 20px; font-size: 13px; font-weight: 500; color: #64748b; background: transparent; border: none; border-bottom: 2px solid transparent; margin-right: 4px; }
QTabBar::tab:selected { color: #2563eb; border-bottom: 2px solid #2563eb; background: transparent; }
QTabBar::tab:hover { color: #1e293b; }
QPushButton { border: none; border-radius: 6px; padding: 8px 16px; font-size: 13px; font-weight: 500; }
QPushButton:hover { }
QPushButton:pressed { }
QTableWidget { border: 1px solid #e2e8f0; border-radius: 8px; background: white; gridline-color: #f1f5f9; font-size: 13px; }
QTableWidget::item { padding: 8px 12px; }
QHeaderView::section { background: #f8fafc; padding: 10px 12px; font-weight: 600; font-size: 12px; color: #475569; border: none; border-bottom: 1px solid #e2e8f0; }
QLineEdit, QTextEdit, QSpinBox, QComboBox { border: 1px solid #e2e8f0; border-radius: 6px; padding: 8px 12px; font-size: 13px; background: white; }
QLineEdit:focus, QTextEdit:focus { border-color: #2563eb; }
QGroupBox { font-weight: 600; font-size: 14px; border: 1px solid #e2e8f0; border-radius: 8px; margin-top: 12px; padding: 16px 12px 12px 12px; background: white; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; color: #1e293b; }
QScrollBar:vertical { background: #f1f5f9; width: 8px; border-radius: 4px; }
QScrollBar::handle:vertical { background: #cbd5e1; border-radius: 4px; min-height: 30px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""


def card_style():
    return "background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px;"


def stat_card_style():
    return "background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px;"


def btn_primary():
    return f"""
        QPushButton {{ background: {PRIMARY}; color: white; padding: 10px 20px; font-size: 13px; font-weight: 600; border: none; border-radius: 8px; }}
        QPushButton:hover {{ background: {PRIMARY_DARK}; }}
        QPushButton:pressed {{ background: #1e40af; padding: 11px 19px 9px 21px; }}
    """


def btn_success():
    return f"""
        QPushButton {{ background: {SUCCESS}; color: white; padding: 8px 16px; font-size: 13px; font-weight: 500; border: none; border-radius: 8px; }}
        QPushButton:hover {{ background: #15803d; }}
        QPushButton:pressed {{ background: #166534; padding: 9px 15px 7px 17px; }}
    """


def btn_danger():
    return f"""
        QPushButton {{ background: {DANGER}; color: white; padding: 8px 16px; font-size: 13px; font-weight: 500; border: none; border-radius: 8px; }}
        QPushButton:hover {{ background: #b91c1c; }}
        QPushButton:pressed {{ background: #991b1b; padding: 9px 15px 7px 17px; }}
    """


def btn_outline():
    return f"""
        QPushButton {{ background: transparent; color: {TEXT_PRIMARY}; border: 1px solid {BORDER}; padding: 8px 16px; font-size: 13px; font-weight: 500; border-radius: 8px; }}
        QPushButton:hover {{ background: {BG_SECTION}; border-color: {PRIMARY}; color: {PRIMARY}; }}
        QPushButton:pressed {{ background: {PRIMARY_LIGHT}; padding: 9px 15px 7px 17px; }}
    """


def btn_small():
    return f"""
        QPushButton {{ background: {PRIMARY}; color: white; padding: 6px 12px; font-size: 12px; font-weight: 500; border: none; border-radius: 6px; }}
        QPushButton:hover {{ background: {PRIMARY_DARK}; }}
        QPushButton:pressed {{ padding: 7px 11px 5px 13px; }}
    """
