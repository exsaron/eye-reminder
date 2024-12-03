import sys
from PySide6.QtWidgets import QApplication

from app.core import EyeReminder


if __name__ == "__main__":
    try:
        from ctypes import windll
        myappid = 'mycustomwindowsapps.eyereminder'
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        windll = None

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    window = EyeReminder()
    window.show()

    sys.exit(app.exec())
