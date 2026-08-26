from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from folder2vector.config import CHUNK_OVERLAP, CHUNK_SIZE

from .file_processor_interface import FileProcessorInterface


class PDFProcessor(FileProcessorInterface):
    def __str__(self) -> str:
        return "PDFProcessor"

    def process(self, file_path: str) -> None:
        splits = self.split_pdf_document(file_path)

        self.embed_documents(file_path, splits)

    def split_pdf_document(self, file_path: str) -> list[Document]:
        loader = PyPDFLoader(file_path)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        return text_splitter.split_documents(loader.load())
