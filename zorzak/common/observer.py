import abc
import typing


# Observer
class BaseSubscriber(abc.ABC):
    @abc.abstractmethod
    def update(self, message: typing.Any) -> None:
        pass


# Subject
class BasePublisher(abc.ABC):
    def __init__(self) -> None:
        self._subscribers: list[BaseSubscriber] = []

    @abc.abstractmethod
    def attach(self, subscriber: BaseSubscriber) -> None:
        pass

    @abc.abstractmethod
    def detach(self, subscriber: BaseSubscriber) -> None:
        pass

    @abc.abstractmethod
    def publish(self, content: typing.Any) -> None:
        pass


class SimplePublisher(BasePublisher):
    def __init__(self) -> None:
        super().__init__()
        self._data: list[typing.Any] = []

    def attach(self, subscriber: BaseSubscriber) -> None:
        self._subscribers.append(subscriber)

    def detach(self, subscriber: BaseSubscriber) -> None:
        self._subscribers.remove(subscriber)

    def get_all_data(self):
        return self._data

    def publish(self, content: typing.Any) -> None:
        self._data.append(content)
        for subscriber in self._subscribers:
            subscriber.update(self._data[-1])
