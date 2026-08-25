from abc import ABC, abstractmethod


class FileProcessorInterface(ABC):
    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def process(self, file_path: str) -> None:
        pass
