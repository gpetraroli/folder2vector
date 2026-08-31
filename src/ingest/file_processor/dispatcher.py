import os
from pathlib import Path

from folder2vector.config import get_source_path_to_store
from pgvector_repository import PGVectorRepository

from .markdown_processor import MarkdownProcessor
from .pdf_processor import PDFProcessor
from .text_processor import TextProcessor

PROCESSORS = {
    ".md": MarkdownProcessor,
    ".markdown": MarkdownProcessor,
    ".txt": TextProcessor,
    ".pdf": PDFProcessor,
}


def process_directory(
    directory_path: str,
    pgvector_repository: PGVectorRepository
) -> None:
    if os.path.isdir(directory_path):
        return

    source_path = get_source_path_to_store(directory_path)

    pgvector_repository.delete_by_source_prefix(source_path)
    print(f"Deleted existing chunks for directory: {directory_path}")


def process_file(file_path: str, pgvector_repository: PGVectorRepository) -> None:
    if not os.path.isfile(file_path):
        source_path = get_source_path_to_store(file_path)

        pgvector_repository.delete_by_metadata({"source": source_path})
        print(f"Deleted existing chunks for file: {file_path}")
        return

    extension = Path(file_path).suffix.lower()
    processor_class = PROCESSORS.get(extension)
    
    if processor_class is None:
        print(f"Skipping unsupported file type: {file_path}")
        return

    processor = PROCESSORS.get(extension)(pgvector_repository)
    processor.process(file_path)

    print(f"File processed: {file_path}")
