import typing
from abc import ABC
from .GameState import *


class StateStack:
    stack = []
    StateChangedBeforeLastRead = False

    @staticmethod
    def push(state: GameState) -> None:
        StateStack.stack.append(state)
        StateStack.StateChangedBeforeLastRead = True

    @staticmethod
    def pop() -> GameState:
        StateStack.StateChangedBeforeLastRead = True
        return StateStack.stack.pop()

    @staticmethod
    def update(dt) -> None:
        StateStack.stack[-1].update(dt)

    @staticmethod
    def render(screen) -> None:
        StateStack.stack[-1].render(screen)

    @staticmethod
    def events(ev) -> None:
        StateStack.stack[-1].events(ev)

    @staticmethod
    def windowsize() -> tuple:
        return StateStack.stack[-1].windowsize

    @staticmethod
    def readstate() -> bool:
        if StateStack.StateChangedBeforeLastRead:
            StateStack.StateChangedBeforeLastRead = False
            return True
        return False
    
