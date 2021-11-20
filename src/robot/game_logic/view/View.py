from abc import ABC, abstractmethod

class View(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def redraw(self):
        pass