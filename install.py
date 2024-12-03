import PyInstaller.__main__
from pathlib import Path


MAIN_DIR = Path(__file__).parent.absolute()
MAIN_SCRIPT = MAIN_DIR / 'main.py'


def install() -> None:
    PyInstaller.__main__.run([
        str(MAIN_SCRIPT),
        '--onefile',
        '--name=EyeReminder',
        '--noconsole',
        f'--icon={MAIN_DIR / "icons" / "er_desktop.ico"}',
        '--add-data=icons:icons',
    ])


if __name__ == '__main__':
    install()
