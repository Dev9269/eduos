"""
EduOS Institution Manager — Reusable UI Components
"""

from PyQt6.QtWidgets import (
    QFrame, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QWidget, QProgressBar, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QColor, QFont

from styles import *


class Card(QFrame):
    """Reusable card widget with optional shadow and hover effect."""

    clicked = pyqtSignal()

    def __init__(self, title="", subtitle="", icon="", parent=None):
        super().__init__(parent)
        self.setStyleSheet(card_style())
        self.setCursor(Qt.CursorShape.PointingHandCursor) if title else None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        if icon or title:
            header = QHBoxLayout()
            if icon:
                icon_label = QLabel(icon)
                icon_label.setStyleSheet(f"font-size: 24px;")
                header.addWidget(icon_label)
            texts = QVBoxLayout()
            texts.setSpacing(2)
            if title:
                t = QLabel(title)
                t.setStyleSheet(f"font-size: 15px; font-weight: 600; color: {TEXT_PRIMARY};")
                texts.addWidget(t)
            if subtitle:
                s = QLabel(subtitle)
                s.setStyleSheet(f"font-size: 12px; color: {TEXT_SECONDARY};")
                s.setWordWrap(True)
                texts.addWidget(s)
            header.addLayout(texts, 1)
            layout.addLayout(header)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class StatCard(QFrame):
    """KPI stat card with value, label, trend."""

    def __init__(self, value, label, icon="", trend="", trend_up=True, color=PRIMARY, parent=None):
        super().__init__(parent)
        self.setStyleSheet(stat_card_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        top = QHBoxLayout()
        v = QLabel(str(value))
        v.setStyleSheet(f"font-size: 28px; font-weight: 700; color: {color};")
        top.addWidget(v)
        if icon:
            i = QLabel(icon)
            i.setStyleSheet("font-size: 22px;")
            i.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            top.addWidget(i, 1)
        layout.addLayout(top)

        l = QLabel(label)
        l.setStyleSheet(f"font-size: 12px; color: {TEXT_SECONDARY}; font-weight: 500;")
        layout.addWidget(l)

        if trend:
            t = QLabel(trend)
            tc = SUCCESS if trend_up else DANGER
            t.setStyleSheet(f"font-size: 11px; color: {tc};")
            layout.addWidget(t)


class TableWidget(QTableWidget):
    """Styled table widget with sortable columns."""

    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionsClickable(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setStyleSheet("""
            QTableWidget { border: 1px solid #e2e8f0; border-radius: 8px; background: white; gridline-color: #f1f5f9; font-size: 13px; }
            QTableWidget::item { padding: 8px 12px; }
            QTableWidget::item:selected { background: #dbeafe; color: #1e293b; }
            QHeaderView::section { background: #f8fafc; padding: 10px 12px; font-weight: 600; font-size: 12px; color: #475569; border: none; border-bottom: 1px solid #e2e8f0; }
        """)
        self.verticalHeader().setVisible(False)

    def add_row(self, values):
        row = self.rowCount()
        self.insertRow(row)
        for col, val in enumerate(values):
            item = QTableWidgetItem(str(val))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, col, item)
        return row


class MiniChart(QWidget):
    """Simple bar chart widget for dashboard KPIs."""

    def __init__(self, data, color=PRIMARY, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self.data = data
        self.bar_color = color

    def paintEvent(self, event):
        from PyQt6.QtGui import QPainter, QPen, QBrush, QPainterPath
        if not self.data:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        bar_count = len(self.data)
        max_val = max(self.data) if max(self.data) > 0 else 1
        bar_w = max(4, (w - bar_count) / bar_count - 1)

        path = QPainterPath()
        first = True
        for i, val in enumerate(self.data):
            x = i * (bar_w + 1) + 2
            bh = (val / max_val) * (h - 8)
            painter.setBrush(QBrush(QColor(self.bar_color)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(int(x), int(h - bh - 4), int(bar_w), int(bh), 2, 2)

        painter.end()


class StatusBadge(QLabel):
    """Colored status badge."""

    def __init__(self, text, status_type="info", parent=None):
        super().__init__(text, parent)
        colors = {
            "success": ("#dcfce7", "#16a34a"), "danger": ("#fee2e2", "#dc2626"),
            "warning": ("#fef3c7", "#d97706"), "info": ("#dbeafe", "#2563eb"),
            "neutral": ("#f1f5f9", "#64748b"), "active": ("#dcfce7", "#16a34a"),
            "inactive": ("#f1f5f9", "#94a3b8"),
        }
        bg, fg = colors.get(status_type, colors["info"])
        self.setStyleSheet(f"""
            background: {bg}; color: {fg}; padding: 3px 10px;
            border-radius: 10px; font-size: 11px; font-weight: 600;
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)


class SectionTitle(QLabel):
    """Section header title."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {TEXT_PRIMARY}; padding: 4px 0;")


class ActionBar(QWidget):
    """Top action bar with title and action buttons."""

    def __init__(self, title, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 12)

        t = QLabel(title)
        t.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {TEXT_PRIMARY};")
        layout.addWidget(t)
        layout.addStretch()
        self.btn_layout = layout

    def add_button(self, text, icon="", callback=None, style=None):
        btn = QPushButton(f"{icon} {text}" if icon else text)
        btn.setStyleSheet(style or btn_primary())
        if callback:
            btn.clicked.connect(callback)
        self.btn_layout.addWidget(btn)
        return btn
