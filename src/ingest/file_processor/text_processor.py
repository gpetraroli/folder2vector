from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from repository.pgvector_repository import PGVectorRepository

from .file_processor_interface import FileProcessorInterface


class TextProcessor(FileProcessorInterface):
    def __init__(self):
        self.pgvector_repository = PGVectorRepository()

    def process(self, file_path: str) -> None:
        splits = self.split_text_document(file_path)

        self.embed_documents(file_path, splits)

    def split_text_document(self, file_path: str) -> list[Document]:
        """Split a text document into chunks"""

        loader = TextLoader(file_path)
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )

        splits = text_splitter.split_documents(docs)

        return splits

    def embed_documents(self, file_path: str, documents: list[Document]):
        self.pgvector_repository.delete_existing_chunks(file_path)
        self.pgvector_repository.embed_documents(documents)
