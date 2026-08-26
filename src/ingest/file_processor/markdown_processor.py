from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, MarkdownTextSplitter

from folder2vector.config import CHUNK_OVERLAP, CHUNK_SIZE

from .file_processor_interface import FileProcessorInterface


class MarkdownProcessor(FileProcessorInterface):
    def __str__(self) -> str:
        return "MarkdownProcessor"

    def process(self, file_path: str) -> None:
        splits = self.split_markdown_document(file_path)

        self.embed_documents(file_path, splits)

    def split_markdown_document(self, file_path: str) -> list[Document]:
        loader = TextLoader(file_path)
        docs = loader.load()

        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]

        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on,
            strip_headers=False
        )

        header_splits = []
        for doc in docs:
            splits = markdown_splitter.split_text(doc.page_content)
            for split in splits:
                split.metadata = {**doc.metadata, **split.metadata}

            header_splits.extend(splits)
            
        text_splitter = MarkdownTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )

        return text_splitter.split_documents(header_splits)
