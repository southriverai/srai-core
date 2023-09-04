from abc import ABC, abstractmethod


class BaseCommandHandler:
    def __init__(self):
        pass

    @abstractmethod
    def execute(self, command: str) -> None:
        raise NotImplementedError()
