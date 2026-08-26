import os
import threading
import time

from watchdog.events import FileSystemEventHandler

from .utils import is_temporary_file


class Watcher(FileSystemEventHandler):
    def __init__(self):
        self._lock = threading.Lock()
        self._pending_files: dict[str, float] = {}

    def on_created(self, event):
        if event.is_directory or is_temporary_file(event.src_path):
            return

        self.mark_touched(event.src_path)

    def on_modified(self, event):
        if event.is_directory or is_temporary_file(event.src_path):
            return

        self.mark_touched(event.src_path)

    def on_deleted(self, event):
        if event.is_directory or is_temporary_file(event.src_path):
            return

        self.mark_touched(event.src_path)

    def on_moved(self, event):
        if event.is_directory:
            return

        if not is_temporary_file(event.src_path):
            self.mark_touched(event.src_path)

        if not is_temporary_file(event.dest_path):
            self.mark_touched(event.dest_path)

    def mark_touched(self, file_path: str) -> None:
        path = os.path.abspath(file_path)
        with self._lock:
            self._pending_files[path] = time.monotonic()

    def pop_ready(self, settle_seconds: float) -> list[str]:
        now = time.monotonic()
        files_ready_to_be_processed: list[str] = []

        with self._lock:
            for path, touched_at in list(self._pending_files.items()):
                if now - touched_at >= settle_seconds:
                    files_ready_to_be_processed.append(path)
                    del self._pending_files[path]

        return files_ready_to_be_processed
    