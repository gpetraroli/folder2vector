from pathlib import Path

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
    extension = Path(file_path).suffix.lower()
    processor = PROCESSORS.get(extension)
    
    print(f"Processing file: {file_path} with {processor}")

    if processor is None:
        print(f"Skipping unsupported file type: {file_path}")
        return

    processor.process(file_path)

    print(f"File processed: {file_path}")
