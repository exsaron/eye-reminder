from typing import Literal, Type

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QMenu
from PySide6.QtCore import Signal, QObject
from PySide6.QtGui import QIcon, QAction

from app.config import config


class TimerController(QObject):
    """ Конструктор виджетов для управления таймером """

    start = Signal()
    pause = Signal()
    stop = Signal()

    @staticmethod
    def __get_signal(widget: QPushButton | QAction) -> Signal:
        match widget:
            case QPushButton():
                return widget.clicked
            case QAction():
                return widget.triggered
            case _:
                raise TypeError(f'Неподдериваемый тип виджета: {type(widget)}')

    def __init_button[T: (QPushButton, QAction)](
            self,
            action_class: Type[T],
            action_key: Literal['start', 'pause', 'stop'],
    ) -> T:
        """ Создает кнопку заданного класса и привязывает ее к сигналу """

        config_field = f'timer_{action_key}'
        btn = action_class(getattr(config.labels, config_field))
        btn.setIcon(QIcon(getattr(config.icons, config_field)))
        btn.setToolTip(getattr(config.tooltips, config_field))
        self.__get_signal(btn).connect(getattr(self, action_key))
        return btn

    @property
    def window_ui(self) -> QWidget:
        """ Создает виджет для отображения в окне """

        widget = QWidget()
        layout = QHBoxLayout()

        widget.start_btn = self.__init_button(QPushButton, 'start')
        widget.pause_btn = self.__init_button(QPushButton, 'pause')
        widget.stop_btn = self.__init_button(QPushButton, 'stop')

        for btn in (widget.start_btn, widget.pause_btn, widget.stop_btn):
            layout.addWidget(btn)

        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)
        return widget

    @property
    def tray_ui(self) -> tuple[QAction, QAction, QAction]:
        """ Создает набор действий для ``QMenu`` в трее """

        return (
            self.__init_button(QAction, 'start'),
            self.__init_button(QAction, 'pause'),
            self.__init_button(QAction, 'stop'),
        )
