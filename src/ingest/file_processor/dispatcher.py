import os
from pathlib import Path

from langchain_ollama import OllamaEmbeddings

from folder2vector.config import (
    COLLECTION_NAME,
    DB_CONNECTION,
    EMBEDDING_MODEL,
    OLLAMA_URL,
    get_source_path_to_store,
)
from pgvector_repository import PGVectorRepository

from .markdown_processor import MarkdownProcessor
from .pdf_processor import PDFProcessor
from .text_processor import TextProcessor

PROCESSORS = {
    ".md": MarkdownProcessor(),
    ".markdown": MarkdownProcessor(),
    ".txt": TextProcessor(),
    ".pdf": PDFProcessor(),
}




def process_file(file_path: str) -> None:
    if not os.path.isfile(file_path):
        source_path = get_source_path_to_store(file_path)

        embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_URL)
        repository = PGVectorRepository(
            connection_string=DB_CONNECTION,
            collection_name=COLLECTION_NAME,
            embeddings=embeddings
        )
        repository.delete_by_metadata({"source": source_path})
        print(f"Deleted existing chunks for file: {file_path}")
        return

    extension = Path(file_path).suffix.lower()
    processor = PROCESSORS.get(extension)
    
    if processor is None:
        print(f"Skipping unsupported file type: {file_path}")
        return

    processor.process(file_path)

    print(f"File processed: {file_path}")
