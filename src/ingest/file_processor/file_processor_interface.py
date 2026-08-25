from abc import ABC, abstractmethod

from repository.pgvector_repository import PGVectorRepository


class FileProcessorInterface(ABC):
    def __init__(self):
        self.pgvector_repository = PGVectorRepository()

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def process(self, file_path: str) -> None:
        pass
