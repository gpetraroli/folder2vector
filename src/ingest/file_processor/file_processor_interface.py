from abc import ABC, abstractmethod


class FileProcessorInterface(ABC):
    @abstractmethod
    def process(self, file_path: str) -> None:
        pass
