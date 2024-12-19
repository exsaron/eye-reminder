from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QIcon, Qt

from app.schemas import TimeInterval
from app.config import config
from app.ui.controls import HoldableButton


class TimePartialAdjuster(QWidget):
    changed = Signal(int)

    def __init__(self, label_text: str):
        super().__init__()

        layout = QHBoxLayout()

        self.label = QLabel(label_text)
        self.label.setMaximumWidth(25)
        self.label.setAlignment(Qt.AlignVCenter)
        layout.addWidget(self.label)

        self.decrement_btn = HoldableButton()
        self.decrement_btn.setIcon(QIcon(config.icons.minus))
        self.decrement_btn.setMaximumWidth(35)
        self.decrement_btn.clicked.connect(self.decrement)
        layout.addWidget(self.decrement_btn)

        self.increment_btn = HoldableButton()
        self.increment_btn.setIcon(QIcon(config.icons.plus))
        self.increment_btn.setMaximumWidth(35)
        self.increment_btn.clicked.connect(self.increment)
        layout.addWidget(self.increment_btn)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

    @Slot()
    def decrement(self) -> None:
        self.changed.emit(-1)

    @Slot()
    def increment(self) -> None:
        self.changed.emit(1)


class TimerAdjuster(QWidget):
    """ Виджет для настройки интервала таймера """

    seconds_updated = Signal(int)

    def __init__(self, initial_time: TimeInterval | None = None):
        super().__init__()

        self.interval: TimeInterval | None = initial_time

        layout = QHBoxLayout()

        self.hours_adjuster = TimePartialAdjuster('ЧЧ:')
        self.hours_adjuster.changed.connect(self.update_hours)
        layout.addWidget(self.hours_adjuster)

        self.minutes_adjuster = TimePartialAdjuster('ММ:')
        self.minutes_adjuster.changed.connect(self.update_minutes)
        layout.addWidget(self.minutes_adjuster)

        self.seconds_adjuster = TimePartialAdjuster('СС:')
        self.seconds_adjuster.changed.connect(self.update_seconds)
        layout.addWidget(self.seconds_adjuster)

        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def set_initial_time(self, interval: TimeInterval) -> None:
        self.interval = interval

    def disable(self) -> None:
        """ Блокирует кнопки контроля таймера """
        for t_adj in (self.hours_adjuster, self.minutes_adjuster, self.seconds_adjuster):
            t_adj.decrement_btn.setEnabled(False)
            t_adj.increment_btn.setEnabled(False)

    def enable(self) -> None:
        """ Деблокирует кнопки контроля таймера """
        for t_adj in (self.hours_adjuster, self.minutes_adjuster, self.seconds_adjuster):
            t_adj.decrement_btn.setEnabled(True)
            t_adj.increment_btn.setEnabled(True)

    @Slot(int)
    def update_hours(self, delta: int) -> None:
        self.interval.hours = (self.interval.hours + delta) % 100
        self.emit_time()

    @Slot(int)
    def update_minutes(self, delta: int) -> None:
        self.interval.minutes = (self.interval.minutes + delta) % 60
        self.emit_time()

    @Slot(int)
    def update_seconds(self, delta: int) -> None:
        self.interval.seconds = (self.interval.seconds + delta) % 60
        self.emit_time()

    def emit_time(self) -> None:
        self.seconds_updated.emit(self.interval.total_seconds)
