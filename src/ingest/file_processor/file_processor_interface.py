from abc import ABC, abstractmethod

from langchain_core.documents import Document

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

    def embed_documents(self, file_path: str, documents: list[Document]) -> None:
        self.pgvector_repository.delete_existing_chunks(file_path)
        self.pgvector_repository.embed_documents(documents)
