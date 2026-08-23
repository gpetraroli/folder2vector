import os
import time
from watchdog.observers import Observer

from config import WATCH_PATH
from watcher import MarkdownWatcher

def run():
    os.makedirs(WATCH_PATH, exist_ok=True)

    print(f"Starting file watcher on: {WATCH_PATH}")
    print("Press Ctrl+C to stop.")

    def test(a: str):
        print("process file")

    event_handler = MarkdownWatcher(test)
    observer = Observer()
    observer.schedule(event_handler, WATCH_PATH, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("🛑 File watcher stopped.")
        
    observer.join()

if __name__ == "__main__":
    run()