from PySide6.QtCore import QTimer, Signal, Slot, QObject
from PySide6.QtWidgets import QSystemTrayIcon
from PySide6.QtGui import QIcon

from .config import config
from .schemas import TimeInterval
from .ui import TrayMenu


class Countdown(QObject):
    started = Signal()
    expired = Signal()
    updated = Signal(int)
    paused = Signal()
    stopped = Signal()

    def __init__(self) -> None:
        super().__init__()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.interval = TimeInterval.from_seconds(config.persistent.timer_seconds)
        self.remaining_seconds = self.interval.total_seconds

    @Slot(int)
    def set_interval(self, seconds: int | None = None) -> None:
        if seconds is not None:
            self.interval = TimeInterval.from_seconds(seconds)
        self.remaining_seconds = self.interval.total_seconds

    @Slot()
    def start(self, silent: bool = False) -> None:
        self.timer.start(1000)
        if not silent:
            self.started.emit()

    @Slot()
    def restart(self) -> None:
        self.stop(silent=True)
        self.expired.emit()
        self.start(silent=True)

    @Slot()
    def update(self) -> None:
        self.remaining_seconds -= 1
        self.updated.emit(self.remaining_seconds)

        if self.remaining_seconds <= 0:
            self.restart()

    @Slot()
    def pause(self) -> None:
        self.timer.stop()
        self.paused.emit()

    @Slot()
    def stop(self, silent: bool = False) -> None:
        self.timer.stop()
        self.set_interval()
        if not silent:
            self.stopped.emit()


class Tray(QObject):
    def __init__(self) -> None:
        super().__init__()

        self.icon = QSystemTrayIcon(QIcon(config.icons.tray_inactive), self)
        self.icon.setToolTip(config.tray_title)
        self.menu = TrayMenu()
        self.icon.setContextMenu(self.menu)
        self.icon.show()
