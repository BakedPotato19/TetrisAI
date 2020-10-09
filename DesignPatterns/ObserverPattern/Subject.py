from abc import ABC, abstractmethod
import typing
import Observer

class Subject(ABC):

    @abstractmethod
    @property
    def _observers(self):
        raise NotImplementedError

    def subscribe(self, observer : Observer):
        self._observers.append(observer)

    def unsubscribe(self, observer : Observer):
        self._observers.remove(observer)

    def notify(self, msg : str):
        for obs in self._observers:
            obs.notification(msg)




