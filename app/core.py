from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSystemTrayIcon,
)
from PySide6.QtGui import QIcon

from .config import config
from .ui import UIContainer
from .schemas import TimeInterval
from .services import Countdown, Tray


class EyeReminder(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.configure()

        self.countdown = Countdown()
        self.connect_countdown()

        self.tray = Tray()
        self.connect_tray()

        self.ui = UIContainer()
        self.connect_ui()

        self.update_timer_displayer(self.countdown.remaining_seconds)

    def configure(self) -> None:
        self.setWindowTitle(config.app_title)
        self.setWindowIcon(QIcon(config.icons.settings))
        self.resize(*config.config_window_size)
        self.center_window()

    def center_window(self) -> None:
        frame_geometry = self.frameGeometry()
        screen_center = QApplication.primaryScreen().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())

    @Slot()
    def save_preferences(self) -> None:
        config.persistent.timer_seconds = self.countdown.interval.total_seconds
        config.persistent.notification_title = self.ui.title_editor.text()
        config.persistent.notification_text = self.ui.text_editor.toPlainText()
        config.save()

    def connect_countdown(self) -> None:
        self.countdown.started.connect(self.countdown_started)
        self.countdown.expired.connect(self.countdown_expired)
        self.countdown.updated.connect(self.countdown_updated)
        self.countdown.paused.connect(self.countdown_paused)
        self.countdown.stopped.connect(self.countdown_stopped)

    def connect_controller(self) -> None:
        self.ui.timer_controller.start.connect(self.countdown.on_start)
        self.ui.timer_controller.pause.connect(self.countdown.on_pause)
        self.ui.timer_controller.stop.connect(self.countdown.on_stop)

    def connect_adjuster(self) -> None:
        self.ui.timer_adjuster.set_initial_time(self.countdown.interval)
        self.ui.timer_adjuster.seconds_updated.connect(self.countdown.set_interval)
        self.ui.timer_adjuster.seconds_updated.connect(self.update_timer_displayer)

    def connect_tray(self) -> None:
        self.tray.icon.activated.connect(self.tray_icon_activated)
        self.tray.menu.settings_action.triggered.connect(self.show)
        self.tray.menu.timer_controller.start.connect(self.countdown.on_start)
        self.tray.menu.timer_controller.pause.connect(self.countdown.on_pause)
        self.tray.menu.timer_controller.stop.connect(self.countdown.on_stop)
        self.tray.menu.exit_action.triggered.connect(self.exit_app)

    def connect_ui(self) -> None:
        self.ui.save_button.clicked.connect(self.save_preferences)
        self.connect_controller()
        self.connect_adjuster()
        self.setCentralWidget(self.ui)

    @Slot()
    def countdown_started(self) -> None:
        self.tray.icon.setIcon(QIcon(config.icons.tray_active))
        self.ui.timer_adjuster.disable()
        self.ui.timer_displayer.set_active(True)

    @Slot()
    def countdown_expired(self) -> None:
        self.notify()

    @Slot(int)
    def countdown_updated(self, seconds_left: int) -> None:
        self.update_timer_displayer(seconds_left)
        self.update_tray_tooltip(seconds_left)

    @Slot()
    def countdown_paused(self) -> None:
        self.tray.icon.setIcon(QIcon(config.icons.tray_message))
        self.ui.timer_displayer.set_active(False)

    @Slot()
    def countdown_stopped(self) -> None:
        self.tray.icon.setIcon(QIcon(config.icons.tray_inactive))
        self.update_timer_displayer(self.countdown.interval.total_seconds)
        self.update_tray_tooltip(-1)
        self.ui.timer_displayer.set_active(False)
        self.ui.timer_adjuster.enable()

    @Slot(int)
    def update_timer_displayer(self, seconds_left: int) -> None:
        remains = TimeInterval.from_seconds(seconds_left)
        self.ui.timer_displayer.display(remains.string)
        self.tray.menu.timer_displayer.display(remains.string)

    @Slot(int)
    def update_tray_tooltip(self, seconds_left: int) -> None:
        """
        Обновляет тултип иконки трея для отображения оставшегося времени
        :param seconds_left: передать ``-1`` - вернуть тултип по умолчанию
        """
        if seconds_left < 0:
            self.tray.icon.setToolTip(config.tooltips.tray_default)
            return

        remains = TimeInterval.from_seconds(seconds_left)
        if remains.minutes > 0:
            tooltip = f'Осталось {remains.minutes} мин.'
        else:
            tooltip = 'Осталось менее 1 минуты'

        self.tray.icon.setToolTip(tooltip)

    def notify(self) -> None:
        self.tray.icon.showMessage(
            self.ui.title_editor.text(),
            self.ui.text_editor.toPlainText(),
            QIcon(config.icons.tray_message),
            3000,
        )

    def tray_icon_activated(self, reason: str) -> None:
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()

    @Slot()
    def exit_app(self):
        self.tray.icon.hide()
        QApplication.quit()
