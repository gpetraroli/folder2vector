from abc import ABC, abstractmethod

from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings

from folder2vector.config import (
    COLLECTION_NAME,
    DB_CONNECTION,
    EMBEDDING_MODEL,
    OLLAMA_URL,
    get_source_path_to_store,
)
from pgvector_repository import PGVectorRepository


class FileProcessorInterface(ABC):
    def __init__(self):
        embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_URL)
        self.pgvector_repository = PGVectorRepository(
            connection_string=DB_CONNECTION,
            collection_name=COLLECTION_NAME,
            embeddings=embeddings,
        )

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def process(self, file_path: str) -> None:
        pass

    def embed_documents(self, file_path: str, documents: list[Document]) -> None:
        source_path = get_source_path_to_store(file_path)
        
        self.pgvector_repository.delete_by_metadata({"source": source_path})

        # Remove empty documents
        documents_to_embed = [doc for doc in documents if doc.page_content.strip()]
        if not documents_to_embed:
            return

        for doc in documents_to_embed:
            doc.metadata["source"] = source_path

        self.pgvector_repository.embed_documents(documents_to_embed)
