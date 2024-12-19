from PySide6.QtWidgets import QWidget, QLCDNumber
from PySide6.QtGui import QPalette, QColor

from app.schemas import TimeInterval


class TimerDisplayer(QLCDNumber):
    """ Виджет для отображения оставшегося времени """

    def __init__(self, parent: QWidget | None = None, min_height: int = 100) -> None:
        super().__init__(parent)
        self.setSegmentStyle(QLCDNumber.Filled)
        self.set_active(False)
        self.setDigitCount(8)
        self.setMinimumHeight(min_height)
        self.display(TimeInterval.from_seconds(0).string)

    def set_active(self, is_active: bool) -> None:
        color = QColor(0, 0, 0) if is_active else QColor(100, 100, 100)
        palette = QPalette()
        palette.setColor(QPalette.Active, QPalette.WindowText, color)
        self.setPalette(palette)
