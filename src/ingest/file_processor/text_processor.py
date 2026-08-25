from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ...config import DB_CONNECTION, EMBEDDING_MODEL, OLLAMA_URL
from .file_processor_interface import FileProcessorInterface


class TextProcessor(FileProcessorInterface):
    def process(self, file_path: str) -> None:
        splits = self.split_text_document(file_path)

        self.embed_documents(splits)

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

    def embed_documents(self, documents: list[Document]):
        embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_URL)

        vector_store = PGVector(
            embeddings=embeddings,
            collection_name="documents",
            connection=DB_CONNECTION,
            use_jsonb=True,
        )

        vector_store.add_documents(documents)
