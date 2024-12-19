from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
)
from PySide6.QtGui import QIcon

from app.config import config
from app.ui import TimerDisplayer, TimerAdjuster, TimerController


class UIContainer(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.timer_displayer = TimerDisplayer(parent=self)
        layout.addWidget(self.timer_displayer)

        self.timer_adjuster = TimerAdjuster()
        layout.addWidget(self.timer_adjuster)

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

        self.timer_controller = TimerController()
        layout.addWidget(self.timer_controller.window_ui)

        self.setLayout(layout)
