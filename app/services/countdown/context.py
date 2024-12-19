from PySide6.QtCore import QTimer, Signal, Slot, QObject

from app.config import config
from app.schemas import TimeInterval
from .states import State, Stopped


class Countdown(QObject):
    """ Управляет обратным отсчетом. Реализует паттерн **State** """

    started = Signal()
    expired = Signal()
    updated = Signal(int)
    paused = Signal()
    stopped = Signal()

    # Текущее состояние. Обработчики команд делегируют работу ему
    _state: State = None

    def __init__(self) -> None:
        super().__init__()

        self.timer = QTimer()
        self.timer.timeout.connect(self.on_update)
        self.interval = TimeInterval.from_seconds(config.persistent.timer_seconds)
        self.remaining_seconds = self.interval.total_seconds
        self.set_state(Stopped())

    def set_state(self, state: State) -> None:
        self._state = state
        self._state.context = self

    @Slot(int)
    def set_interval(self, seconds: int | None = None) -> None:
        if seconds is not None:
            self.interval = TimeInterval.from_seconds(seconds)
        self.remaining_seconds = self.interval.total_seconds

    @Slot()
    def on_start(self) -> None:
        self._state.on_start()

    @Slot()
    def on_pause(self) -> None:
        self._state.on_pause()

    @Slot()
    def on_stop(self) -> None:
        self._state.on_stop()

    @Slot()
    def on_update(self) -> None:
        self._state.on_update()
