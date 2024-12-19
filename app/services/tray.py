from PySide6.QtCore import QObject
from PySide6.QtWidgets import QSystemTrayIcon
from PySide6.QtGui import QIcon

from app.config import config
from app.ui import TrayMenu


class Tray(QObject):
    def __init__(self) -> None:
        super().__init__()

        self.icon = QSystemTrayIcon(QIcon(config.icons.tray_inactive), self)
        self.icon.setToolTip(config.tray_title)
        self.menu = TrayMenu()
        self.icon.setContextMenu(self.menu)
        self.icon.show()
