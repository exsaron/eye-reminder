import json
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(getattr(sys, '_MEIPASS'))
    CONFIG_DIR = Path(sys.executable).parent / 'config'
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    CONFIG_DIR = BASE_DIR / 'config'

APP_NAME = 'EyeReminder'
CONFIG_DIR.mkdir(exist_ok=True)


@dataclass
class PersistentSettings:
    timer_seconds: int = 3000       # 50 минут
    notification_title: str = 'ВНИМАНИЕ'
    notification_text: str = 'Время истекло'


@dataclass(frozen=True)
class Tooltips:
    timer_start: str = 'Запуск таймера с текущей отметки'
    timer_pause: str = 'Остановка таймера с сохранением текущего значения'
    timer_stop: str = 'Остановка и обнуление таймера'
    save: str = 'Сохранить текущие настройки'
    tray_default: str = APP_NAME


@dataclass(frozen=True)
class IconPaths:
    app: str
    tray_inactive: str
    tray_active: str
    tray_message: str
    save: str
    shutdown: str
    timer_start: str
    timer_pause: str
    timer_stop: str
    plus: str
    minus: str
    settings: str


def load_icon(dir_path: Path, name: str) -> str:
    return (dir_path / name).as_posix()


def get_icon_paths(dir_path: Path) -> IconPaths:
    return IconPaths(
        app=load_icon(dir_path, 'er_app.png'),
        tray_inactive=load_icon(dir_path, 'er_tray_inactive.png'),
        tray_active=load_icon(dir_path, 'er_tray_active.png'),
        tray_message=load_icon(dir_path, 'er_tray_message.png'),
        save=load_icon(dir_path, 'save.png'),
        shutdown=load_icon(dir_path, 'shutdown.png'),
        timer_start=load_icon(dir_path, 'timer_start.png'),
        timer_pause=load_icon(dir_path, 'timer_pause.png'),
        timer_stop=load_icon(dir_path, 'timer_stop.png'),
        plus=load_icon(dir_path, 'plus.png'),
        minus=load_icon(dir_path, 'minus.png'),
        settings=load_icon(dir_path, 'settings.png'),
    )


@dataclass
class Config:
    base_dir: Path = BASE_DIR
    config_filename: str = 'config.json'
    app_title: str = f'Настройки {APP_NAME}'
    tray_title: str = APP_NAME
    config_window_size: tuple[int, int] = (400, 300)

    persistent: PersistentSettings = field(default_factory=PersistentSettings)
    icons: IconPaths | None = None
    tooltips: Tooltips = Tooltips()

    @property
    def config_file(self) -> Path:
        return CONFIG_DIR / self.config_filename

    @property
    def icons_dir(self) -> Path:
        return self.base_dir / 'icons'

    def save(self) -> None:
        """ Сохраняет текущую конфигурацию в файл """
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.persistent), f, ensure_ascii=False, indent=4)

    def load(self) -> None:
        """ Загружает конфигурацию из файла. Если файла нет - создает его и заполняет текущими значениями """

        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.persistent = PersistentSettings(**json.load(f))
        else:
            self.save()


config: Config = Config()
config.load()
config.icons = get_icon_paths(config.icons_dir)
