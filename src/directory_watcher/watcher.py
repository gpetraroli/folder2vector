import os
from typing import Callable
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent, FileDeletedEvent, FileMovedEvent

class MarkdownWatcher(FileSystemEventHandler):

    def __init__(self, process_file: Callable[[str], None]):
        self.process_file = process_file


    def on_created(self, event: FileCreatedEvent):
        if event.is_directory:
            return
                    
        if os.path.getsize(event.src_path) == 0:
            return

        self.process_file(event.src_path)

    def on_modified(self, event):
        # TODO: Handle modified files
        return

    def on_deleted(self, event):
        # TODO: Handle deleted files
        return

    def on_moved(self, event):
        # TODO: Handle moved files
        return
