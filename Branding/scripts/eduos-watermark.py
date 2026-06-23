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
        self.engine_text = "KDE Plasma Desktop"

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

        engine_font = QFont("Inter", 8)
        painter.setFont(engine_font)
        engine_rect = painter.fontMetrics().boundingRect(self.engine_text)

        margin = 20
        block_w = max(title_rect.width(), subtitle_rect.width(), engine_rect.width()) + 24
        block_h = title_rect.height() + subtitle_rect.height() + engine_rect.height() + 30

        x = screen_w - block_w - margin
        y = margin

        # Background pill (glass)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(10, 10, 20, 130))
        painter.drawRoundedRect(x, y, block_w, block_h, 12, 12)

        # Glass border
        painter.setPen(QPen(QColor(255, 255, 255, 25), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(x, y, block_w, block_h, 12, 12)

        # Accent line on left (amber)
        painter.setBrush(QColor(200, 145, 62, 160))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(x, y + 4, 3, block_h - 8, 2, 2)

        # Title
        painter.setPen(QColor(255, 255, 255, 160))
        title_font.setWeight(QFont.Weight.Medium)
        painter.setFont(title_font)
        painter.drawText(
            x + 14, y + 10,
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

        # Engine credit
        painter.setPen(QColor(255, 255, 255, 60))
        painter.setFont(engine_font)
        painter.drawText(
            x + 14, y + 14 + title_rect.height() + subtitle_rect.height() + 2,
            block_w - 14, engine_rect.height() + 4,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self.engine_text
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
