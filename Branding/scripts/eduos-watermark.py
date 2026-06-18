#!/usr/bin/env python3
"""
EduOS Desktop Watermark
Displays a semi-transparent branding overlay at top-right of the screen.
Auto-starts with Plasma session via autostart.
"""

import sys
import signal
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtCore import Qt, QTimer, QRect
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush, QFontDatabase


class WatermarkWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EduOS Watermark")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_X11NetWmWindowTypeDock)

        screen = QApplication.primaryScreen()
        self.screen_geometry = screen.availableGeometry() if screen else QRect(0, 0, 1280, 800)

        self.watermark_text = "EduOS \u2013 Engineering Education Edition"
        self.subtitle_text = "Developed by Jainam H. Maru"

        self.setGeometry(0, 0, self.screen_geometry.width(), self.screen_geometry.height())
        self.raise_()
        self.lower()

        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        screen_w = self.screen_geometry.width()
        screen_h = self.screen_geometry.height()

        # Draw watermark text at top-right
        painter.setPen(QColor(255, 255, 255, 55))

        title_font = QFont("Inter", 11)
        title_font.setWeight(QFont.Weight.Normal)
        painter.setFont(title_font)
        title_rect = painter.fontMetrics().boundingRect(self.watermark_text)

        subtitle_font = QFont("Inter", 9)
        subtitle_font.setWeight(QFont.Weight.Light)
        painter.setFont(subtitle_font)
        subtitle_rect = painter.fontMetrics().boundingRect(self.subtitle_text)

        margin = 20
        block_w = max(title_rect.width(), subtitle_rect.width()) + 24
        block_h = title_rect.height() + subtitle_rect.height() + 24

        x = screen_w - block_w - margin
        y = margin

        # Background pill
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(15, 23, 42, 120))
        painter.drawRoundedRect(x, y, block_w, block_h, 10, 10)

        # Accent line on left
        painter.setBrush(QColor(37, 99, 235, 160))
        painter.drawRoundedRect(x, y + 4, 3, block_h - 8, 2, 2)

        # Title
        painter.setPen(QColor(255, 255, 255, 160))
        title_font.setWeight(QFont.Weight.Medium)
        painter.setFont(title_font)
        painter.drawText(
            x + 14, y + 12,
            block_w - 14, title_rect.height() + 4,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self.watermark_text
        )

        # Subtitle
        painter.setPen(QColor(255, 255, 255, 100))
        subtitle_font.setWeight(QFont.Weight.Light)
        painter.setFont(subtitle_font)
        painter.drawText(
            x + 14, y + 12 + title_rect.height() + 2,
            block_w - 14, subtitle_rect.height() + 4,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self.subtitle_text
        )

        painter.end()

    def resizeEvent(self, event):
        screen = QApplication.primaryScreen()
        if screen:
            self.screen_geometry = screen.availableGeometry()
        self.setGeometry(0, 0, self.screen_geometry.width(), self.screen_geometry.height())
        super().resizeEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("EduOS Watermark")

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    watermark = WatermarkWidget()

    # Re-position on screen changes
    timer = QTimer()
    timer.timeout.connect(lambda: watermark.update())
    timer.start(5000)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
