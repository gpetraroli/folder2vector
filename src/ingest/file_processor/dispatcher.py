import os
from pathlib import Path

from repository.pgvector_repository import PGVectorRepository

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
        repository = PGVectorRepository()
        repository.delete_existing_chunks(file_path)
        print(f"Deleted existing chunks for file: {file_path}")
        return

    extension = Path(file_path).suffix.lower()
    processor = PROCESSORS.get(extension)
    
    if processor is None:
        print(f"Skipping unsupported file type: {file_path}")
        return

    processor.process(file_path)

    print(f"File processed: {file_path}")
