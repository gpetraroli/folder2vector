import os
from typing import Callable
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent, FileDeletedEvent, FileMovedEvent

class MarkdownWatcher(FileSystemEventHandler):

    def __init__(self, process_file: Callable[[str], None]):
        self.process_file = process_file

    def on_created(self, event: FileCreatedEvent):
        if event.is_directory or self.is_temporary_file(event.src_path):
            return
        
        if os.path.getsize(event.src_path) == 0:
            return

        self.process_file(event.src_path)

    def on_modified(self, event):
        if event.is_directory or self.is_temporary_file(event.src_path):
            return

        self.process_file(event.src_path)

    def on_deleted(self, event):
        if event.is_directory or self.is_temporary_file(event.src_path):
            return

        print(f"Deleted file: {event.src_path}")

    def on_moved(self, event):
        # TODO: Handle moved files
        print(f"Moved file: {event.src_path}")
        return

    def is_temporary_file(self, file_path: str) -> bool:
        temp_suffixes = (".part", ".tmp", ".crdownload", ".download", ".swp", ".kate-swp")

        name = os.path.basename(file_path)
        if name.startswith(".") or name.startswith("~$"):
            return True
        
        return name.endswith(temp_suffixes)
