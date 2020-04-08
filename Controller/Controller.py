from abc import ABC, abstractmethod


class Controller(ABC):

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def setFrame(self, frame):
        pass
