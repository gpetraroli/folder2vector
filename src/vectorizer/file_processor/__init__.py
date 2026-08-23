from pathlib import Path

from .markdown_processor import MarkdownProcessor
from .text_processor import TextProcessor

PROCESSORS = {
    ".md": MarkdownProcessor(),
    ".markdown": MarkdownProcessor(),
    ".txt": TextProcessor(),
}


def process_file(file_path: str) -> None:
    extension = Path(file_path).suffix.lower()
    processor = PROCESSORS.get(extension)

    if processor is None:
        print(f"Skipping unsupported file type: {file_path}")
        return

    processor.process(file_path)
