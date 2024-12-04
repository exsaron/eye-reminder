from PySide6.QtWidgets import (
    QMenu,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QLineEdit,
    QLCDNumber,
    QWidgetAction,
)
from PySide6.QtGui import QIcon, Qt, QPalette, QColor
from PySide6.QtCore import Signal, Slot

from .config import config
from .schemas import TimeInterval


class TimeAdjuster(QHBoxLayout):
    changed = Signal(int)

    def __init__(self, label_text: str):
        super().__init__()
        self.label = QLabel(label_text)
        self.label.setMaximumWidth(25)
        self.label.setAlignment(Qt.AlignRight)
        self.addWidget(self.label)

        self.decrement_btn = QPushButton()
        self.decrement_btn.setIcon(QIcon(config.icons.minus))
        self.decrement_btn.setMaximumWidth(35)
        self.decrement_btn.pressed.connect(self.decrement)
        self.addWidget(self.decrement_btn)

        self.increment_btn = QPushButton()
        self.increment_btn.setIcon(QIcon(config.icons.plus))
        self.increment_btn.setMaximumWidth(35)
        self.increment_btn.pressed.connect(self.increment)
        self.addWidget(self.increment_btn)

    @Slot()
    def decrement(self) -> None:
        self.changed.emit(-1)

    @Slot()
    def increment(self) -> None:
        self.changed.emit(1)


class TimerController(QHBoxLayout):
    seconds_updated = Signal(int)

    def __init__(self, initial_time: TimeInterval | None = None):
        super().__init__()

        self.interval: TimeInterval | None = initial_time

        self.hours_adjuster = TimeAdjuster('ЧЧ:')
        self.addLayout(self.hours_adjuster)
        self.hours_adjuster.changed.connect(self.update_hours)

        self.minutes_adjuster = TimeAdjuster('ММ:')
        self.addLayout(self.minutes_adjuster)
        self.minutes_adjuster.changed.connect(self.update_minutes)

        self.seconds_adjuster = TimeAdjuster('СС:')
        self.addLayout(self.seconds_adjuster)
        self.seconds_adjuster.changed.connect(self.update_seconds)

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


class TimerDisplayer(QLCDNumber):
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


class UIContainer(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        controls_layout = QHBoxLayout()

        self.timer_displayer = TimerDisplayer(parent=self)
        layout.addWidget(self.timer_displayer)

        self.timer_controller = TimerController()
        layout.addLayout(self.timer_controller)

        self.title_editor_label = QLabel('Заголовок уведомления:')
        self.title_editor = QLineEdit()
        self.title_editor.setMaxLength(40)
        self.title_editor.setText(config.persistent.notification_title)
        self.title_editor_label.setBuddy(self.title_editor)
        layout.addWidget(self.title_editor_label)
        layout.addWidget(self.title_editor)

        self.text_editor_label = QLabel('Текст уведомления:')
        self.text_editor = QPlainTextEdit()
        self.text_editor.setPlainText(config.persistent.notification_text)
        self.text_editor_label.setBuddy(self.text_editor)
        layout.addWidget(self.text_editor_label)
        layout.addWidget(self.text_editor)

        self.save_button = QPushButton('Сохранить')
        self.save_button.setIcon(QIcon(config.icons.save))
        self.save_button.setToolTip(config.tooltips.save)
        layout.addWidget(self.save_button)

        self.start_button = QPushButton('Старт')
        self.start_button.setIcon(QIcon(config.icons.timer_start))
        self.start_button.setToolTip(config.tooltips.timer_start)

        self.pause_button = QPushButton('Пауза')
        self.pause_button.setIcon(QIcon(config.icons.timer_pause))
        self.pause_button.setToolTip(config.tooltips.timer_pause)

        self.stop_button = QPushButton('Стоп')
        self.stop_button.setIcon(QIcon(config.icons.timer_stop))
        self.stop_button.setToolTip(config.tooltips.timer_stop)

        for btn in [self.start_button, self.pause_button, self.stop_button]:
            controls_layout.addWidget(btn)

        layout.addLayout(controls_layout)
        self.setLayout(layout)


class TrayMenu(QMenu):
    def __init__(self):
        super().__init__()

        self.timer_displayer = TimerDisplayer(parent=self, min_height=45)
        timer_displayer_action = QWidgetAction(self)
        timer_displayer_action.setDefaultWidget(self.timer_displayer)
        self.addAction(timer_displayer_action)

        self.addSeparator()

        self.settings_action = self.addAction('НАСТРОЙКИ')
        self.settings_action.setIcon(QIcon(config.icons.settings))

        self.addSeparator()

        self.start_action = self.addAction('СТАРТ')
        self.start_action.setIcon(QIcon(config.icons.timer_start))

        self.pause_action = self.addAction('ПАУЗА')
        self.pause_action.setIcon(QIcon(config.icons.timer_pause))

        self.stop_action = self.addAction('СТОП')
        self.stop_action.setIcon(QIcon(config.icons.timer_stop))

        self.addSeparator()

        self.exit_action = self.addAction('ВЫХОД')
        self.exit_action.setIcon(QIcon(config.icons.shutdown))
