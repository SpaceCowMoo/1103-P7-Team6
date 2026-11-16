
from abc import ABC, abstractmethod


class AIClient(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def generate(self, prompt):
        pass
