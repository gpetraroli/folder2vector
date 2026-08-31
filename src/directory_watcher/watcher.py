import os
import threading
import time
from collections.abc import Collection
from dataclasses import dataclass

from watchdog.events import FileSystemEventHandler

from .utils import should_process


@dataclass
class PendingEvent:
    path: str
    is_directory: bool
    touched_at: float


class Watcher(FileSystemEventHandler):
    def __init__(self, root: str, supported_suffixes: Collection[str]):
        self._root = root
        self._supported_suffixes = supported_suffixes
        self._lock = threading.Lock()
        self._pending_files: dict[str, PendingEvent] = {}

    def _should_handle(self, path: str, *, is_directory: bool) -> bool:
        return should_process(
            path,
            self._root,
            is_directory=is_directory,
            supported_suffixes=self._supported_suffixes,
        )

    def on_created(self, event):
        if event.is_directory or not self._should_handle(
            event.src_path, is_directory=False
        ):
            return

        self.mark_touched(event.src_path)

    def on_modified(self, event):
        if event.is_directory or not self._should_handle(
            event.src_path, is_directory=False
        ):
            return

        self.mark_touched(event.src_path)

    def on_deleted(self, event):
        if not self._should_handle(
            event.src_path, is_directory=event.is_directory
        ):
            return

        self.mark_touched(event.src_path, is_directory=event.is_directory)

    def on_moved(self, event):
        if self._should_handle(event.src_path, is_directory=event.is_directory):
            self.mark_touched(event.src_path, is_directory=event.is_directory)

        if self._should_handle(event.dest_path, is_directory=event.is_directory):
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
    