from PySide6.QtWidgets import QMenu, QWidgetAction
from PySide6.QtGui import QIcon

from app.ui import TimerDisplayer, TimerController
from app.config import config


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

        self.timer_controller = TimerController()
        self.__init_timer_controller_ui()

        self.addSeparator()

        self.exit_action = self.addAction('ВЫХОД')
        self.exit_action.setIcon(QIcon(config.icons.shutdown))

    def __init_timer_controller_ui(self) -> None:
        for idx, action in enumerate(self.timer_controller.tray_ui, start=1):
            action_name = f'action_{idx}'
            setattr(self, action_name, action)
            self.addAction(getattr(self, action_name))
