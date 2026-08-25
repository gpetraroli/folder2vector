import os
import time

from watchdog.observers import Observer

from directory_watcher.watcher import MarkdownWatcher
from ingest.file_processor import process_file

from .config import SETTLE_SECONDS, WATCH_PATH


def run():
    os.makedirs(WATCH_PATH, exist_ok=True)

    print(f"Starting file watcher on: {WATCH_PATH}")
    print("Press Ctrl+C to stop.")

    event_handler = MarkdownWatcher()
    observer = Observer()
    observer.schedule(event_handler, WATCH_PATH, recursive=True)
    observer.start()

    try:
        while True:
            for path in event_handler.pop_ready(SETTLE_SECONDS):
                if not os.path.isfile(path) or os.path.getsize(path) == 0:
                    continue

                process_file(path)

            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("🛑 File watcher stopped.")

    observer.join()


if __name__ == "__main__":
    run()
