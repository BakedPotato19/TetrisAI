from abc import ABC, abstractmethod
import typing

class Observer:
    @abstractmethod
    def notification(self, msg: str, data):
        raise NotImplementedError
    
class Subject(ABC):

    @property
    def _observers(self):
        raise NotImplementedError

    def subscribe(self, observer : Observer):
        self._observers.append(observer)

    def unsubscribe(self, observer : Observer):
        self._observers.remove(observer)

    def notify(self, msg : str, data):
        for obs in self._observers:
            obs.notification(msg, data)
