from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
)
from PySide6.QtCore import QTimer


class HoldableButton(QPushButton):
    """
    Кнопка с поддержкой удержания.

    При удержании каждые ``delay`` мс выдает сигнал ``clicked``.
    """
    def __init__(
            self,
            label: str = '',
            delay: int = 100,
            parent: QWidget | None = None,
    ) -> None:
        super().__init__(label, parent=parent)

        self._timer = QTimer(self)
        self._timer.setInterval(delay)
        self._timer.timeout.connect(self.clicked)

        self.pressed.connect(self.start_holding)
        self.released.connect(self.stop_holding)

    def start_holding(self) -> None:
        self._timer.start()

    def stop_holding(self) -> None:
        self._timer.stop()
