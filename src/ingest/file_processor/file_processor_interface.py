from abc import ABC, abstractmethod

from langchain_core.documents import Document

from folder2vector.config import get_source_path_to_store
from pgvector_repository import PGVectorRepository


class FileProcessorInterface(ABC):
    def __init__(self, pgvector_repository: PGVectorRepository):
        self.pgvector_repository = pgvector_repository

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def process(self, file_path: str) -> None:
        pass

    def embed_documents(self, file_path: str, documents: list[Document]) -> None:
        # TODO: insert new chuncks before deleting.
        
        source_path = get_source_path_to_store(file_path)
        
        self.pgvector_repository.delete_by_metadata({"source": source_path})

        # Remove empty documents
        documents_to_embed = [doc for doc in documents if doc.page_content.strip()]
        if not documents_to_embed:
            return

        for doc in documents_to_embed:
            doc.metadata["source"] = source_path

        self.pgvector_repository.embed_documents(documents_to_embed)
