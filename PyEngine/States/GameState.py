from abc import ABC, abstractmethod

class GameState:
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def render(self, screen):
        raise NotImplementedError

    @abstractmethod
    def update(self, dt):
        raise NotImplementedError

    @abstractmethod
    def events(self, events):
        raise NotImplementedError

    @property
    def windowsize(self):
        raise NotImplementedError


