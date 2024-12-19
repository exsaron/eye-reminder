from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .context import Countdown


class State(ABC):
    """
    Реализация паттерна State.
    Без ``@abstractmethod``, чтобы не нарушать принцип разделения интерфейсов.
    """

    def __init__(self) -> None:
        self._context = None

    @property
    def context(self) -> 'Countdown':
        return self._context

    @context.setter
    def context(self, context: 'Countdown'):
        self._context = context

    def on_start(self) -> None:
        """ По умолчанию не делает ничего """
        pass

    def on_pause(self) -> None:
        """ По умолчанию не делает ничего """
        pass

    def on_stop(self) -> None:
        """ По умолчанию не делает ничего """
        pass

    def on_update(self) -> None:
        """ По умолчанию не делает ничего """
        pass


class Stopped(State):
    """ Таймер не запущен. Состояние по умолчанию """

    def on_start(self) -> None:
        """ Запускает таймер, меняет состояние на Pending """
        self.context.timer.start(1000)
        self.context.set_state(Pending())
        self.context.started.emit()


class Pending(State):
    """ Таймер запущен и обновляется каждую секунду """

    def on_pause(self) -> None:
        """ Ставит таймер на паузу, меняет состояние на Paused """
        self.context.timer.stop()
        self.context.set_state(Paused())
        self.context.paused.emit()

    def on_stop(self) -> None:
        """ Обнуляет и останавливает таймер, меняет состояние на Stopped """
        self.context.timer.stop()
        self.context.set_interval()
        self.context.set_state(Stopped())
        self.context.stopped.emit()

    def on_update(self) -> None:
        """ Обновляет обратный отсчет """
        self.context.remaining_seconds -= 1
        self.context.updated.emit(self.context.remaining_seconds)
        if self.context.remaining_seconds <= 0:
            self.context.expired.emit()
            self.context.set_state(Refreshing())


class Paused(State):
    """ Таймер не обновляется """

    def on_start(self) -> None:
        """ Продолжает обратный отсчет с места остановки """
        self.context.timer.start(1000)
        self.context.set_state(Pending())
        self.context.started.emit()

    def on_stop(self) -> None:
        """ Обнуляет и останавливает таймер """
        self.context.timer.stop()
        self.context.set_interval()
        self.context.set_state(Stopped())
        self.context.stopped.emit()


class Refreshing(State):
    """ Таймер в процессе перезапуска. Состояние длится 1 интервал обновления (1 секунду) """

    def on_stop(self) -> None:
        """ Обнуляет и останавливает таймер """
        self.context.timer.stop()
        self.context.set_interval()
        self.context.set_state(Stopped())
        self.context.stopped.emit()

    def on_update(self) -> None:
        """ Останавливает таймер и запускает снова """
        self.context.on_stop()
        self.context.on_start()
