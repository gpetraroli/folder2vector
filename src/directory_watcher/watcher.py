import os
import threading
import time
from dataclasses import dataclass

from watchdog.events import FileSystemEventHandler

from .utils import is_temporary_file


@dataclass
class PendingEvent:
    path: str
    is_directory: bool
    touched_at: float

class Watcher(FileSystemEventHandler):
    def __init__(self):
        self._lock = threading.Lock()
        self._pending_files: dict[str, PendingEvent] = {}

    def on_created(self, event):
        if event.is_directory or is_temporary_file(event.src_path):
            return

        self.mark_touched(event.src_path)

    def on_modified(self, event):
        if event.is_directory or is_temporary_file(event.src_path):
            return

        self.mark_touched(event.src_path)

    def on_deleted(self, event):
        if is_temporary_file(event.src_path):
            return

        self.mark_touched(event.src_path, is_directory=event.is_directory)

    def on_moved(self, event):
        if not is_temporary_file(event.src_path):
            self.mark_touched(event.src_path, is_directory=event.is_directory)

        if not is_temporary_file(event.dest_path):
            self.mark_touched(event.dest_path, is_directory=event.is_directory)

    def mark_touched(self, file_path: str, is_directory: bool = False) -> None:
        path = os.path.abspath(file_path)
        with self._lock:
            self._pending_files[path] = PendingEvent(
                path=path,
                is_directory=is_directory,
                touched_at=time.monotonic(),
            )

    def pop_ready(self, settle_seconds: float) -> list[PendingEvent]:
        now = time.monotonic()
        files_ready_to_be_processed: list[PendingEvent] = []

        with self._lock:
            for path, pending_event in list(self._pending_files.items()):
                if now - pending_event.touched_at >= settle_seconds:
                    files_ready_to_be_processed.append(pending_event)
                    del self._pending_files[path]

        return files_ready_to_be_processed
    