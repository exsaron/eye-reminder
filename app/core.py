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

        self.update_timer_displayer()

    def configure(self) -> None:
        self.setWindowTitle(config.app_title)
        self.setWindowIcon(QIcon(config.icons.app))
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

    def connect_tray(self) -> None:
        self.tray.icon.activated.connect(self.tray_icon_activated)
        self.tray.menu.start_action.triggered.connect(self.countdown.start)
        self.tray.menu.stop_action.triggered.connect(self.countdown.stop)
        self.tray.menu.exit_action.triggered.connect(self.exit_app)

    def connect_ui(self) -> None:
        self.ui.save_button.clicked.connect(self.save_preferences)
        self.ui.start_button.clicked.connect(self.countdown.start)
        self.ui.pause_button.clicked.connect(self.countdown.pause)
        self.ui.stop_button.clicked.connect(self.countdown.stop)
        self.ui.timer_controller.set_initial_time(self.countdown.interval)
        self.ui.timer_controller.seconds_updated.connect(self.countdown.set_interval)
        self.ui.timer_controller.seconds_updated.connect(self.update_timer_displayer)
        self.setCentralWidget(self.ui)

    @Slot()
    def countdown_started(self) -> None:
        self.tray.icon.setIcon(QIcon(config.icons.tray_active))
        self.ui.timer_controller.disable()

    @Slot()
    def countdown_expired(self) -> None:
        self.notify()

    @Slot()
    def countdown_updated(self) -> None:
        self.update_timer_displayer()

    @Slot()
    def countdown_paused(self) -> None:
        pass

    @Slot()
    def countdown_stopped(self) -> None:
        self.tray.icon.setIcon(QIcon(config.icons.tray_inactive))
        self.update_timer_displayer()
        self.ui.timer_controller.enable()

    def update_timer_displayer(self) -> None:
        remains = TimeInterval.from_seconds(self.countdown.remaining_seconds)
        self.ui.timer_displayer.display(remains.string)

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
