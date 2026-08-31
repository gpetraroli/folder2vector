import argparse
import os
import time
from pathlib import Path

from langchain_ollama import OllamaEmbeddings
from watchdog.observers import Observer

from directory_watcher.utils import is_temporary_file
from directory_watcher.watcher import Watcher
from folder2vector.config import (
    COLLECTION_NAME,
    DB_CONNECTION,
    EMBEDDING_MODEL,
    OLLAMA_URL,
)
from ingest.file_processor import process_file
from ingest.file_processor.dispatcher import PROCESSORS
from pgvector_repository import PGVectorRepository

from .config import SETTLE_SECONDS, WATCH_PATH


def run():
    os.makedirs(WATCH_PATH, exist_ok=True)

    print(f"Starting file watcher on: {WATCH_PATH}")
    print("Press Ctrl+C to stop.")

    event_handler = Watcher()
    observer = Observer()
    observer.schedule(event_handler, WATCH_PATH, recursive=True)
    observer.start()

    try:
        while True:
            try:
                for path in event_handler.pop_ready(SETTLE_SECONDS):
                    process_file(path)

            except Exception as e:
                print(f"Error processing file: {e}")

            finally:
                time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("🛑 File watcher stopped.")

    observer.join()


def init() -> None:
    os.makedirs(WATCH_PATH, exist_ok=True)

    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_URL)
    PGVectorRepository(
        connection_string=DB_CONNECTION,
        collection_name=COLLECTION_NAME,
        embeddings=embeddings
    ).reset_collection()

    for file_path in iter_supported_files(WATCH_PATH):
        try:
            process_file(file_path)
        except Exception as e:
            print(f"Failed: {file_path}: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="folder2vector")
    sub = parser.add_subparsers(dest="command", required=True)

    init_parser = sub.add_parser(
        "init", 
        help="Create/empty the collection and ingest all files"
    )
    init_parser.add_argument("--force", action="store_true")

    sub.add_parser("watch", help="Watch watch_path for changes")

    args = parser.parse_args()
    if args.command == "init":
        if not args.force:
            answer = input(
                "This deletes all embeddings in the collection. Continue? [y/N] "
            )
            if answer.lower() != "y":
                return
        init()
    elif args.command == "watch":
        run()


def iter_supported_files(root: str):
    root_path = Path(root).resolve()
    for path in root_path.rglob("*"):
        if not path.is_file():
            continue
        if is_temporary_file(str(path)):
            continue
        if any(part.startswith(".") for part in path.relative_to(root_path).parts):
            continue
        if path.suffix.lower() not in PROCESSORS:
            continue
        yield str(path)


if __name__ == "__main__":
    run()
