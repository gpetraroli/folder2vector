import os
import threading
import time

from watchdog.events import FileSystemEventHandler


class MarkdownWatcher(FileSystemEventHandler):
    def __init__(self):
        self._lock = threading.Lock()
        self._pending_files: dict[str, float] = {}

    def on_created(self, event):
        if event.is_directory or self.is_temporary_file(event.src_path):
            return

        self.mark_touched(event.src_path)

    def on_modified(self, event):
        if event.is_directory or self.is_temporary_file(event.src_path):
            return

        self.mark_touched(event.src_path)

    def on_deleted(self, event):
        if event.is_directory or self.is_temporary_file(event.src_path):
            return

        self.unmark_touched(event.src_path)

    def on_moved(self, event):
        if event.is_directory:
            return

        self.unmark_touched(event.src_path)
        if not self.is_temporary_file(event.dest_path):
            self.mark_touched(event.dest_path)

    def mark_touched(self, file_path: str) -> None:
        path = os.path.abspath(file_path)
        with self._lock:
            self._pending_files[path] = time.monotonic()

    def unmark_touched(self, file_path: str) -> None:
        path = os.path.abspath(file_path)
        with self._lock:
            self._pending_files.pop(path, None)

    def pop_ready(self, settle_seconds: float) -> list[str]:
        now = time.monotonic()
        files_ready_to_be_processed: list[str] = []

        with self._lock:
            for path, touched_at in self._pending_files.items():
                if now - touched_at >= settle_seconds:
                    files_ready_to_be_processed.append(path)
                    del self._pending_files[path]

        return files_ready_to_be_processed

    def is_temporary_file(self, file_path: str) -> bool:
        temp_suffixes = (
            ".part",
            ".tmp",
            ".crdownload",
            ".download",
            ".swp",
            ".kate-swp",
        )

        name = os.path.basename(file_path)
        if name.startswith(".") or name.startswith("~$"):
            return True

        return name.endswith(temp_suffixes)
