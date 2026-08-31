import os
from collections.abc import Collection
from pathlib import Path


def is_temporary_file(file_path: str) -> bool:
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


def should_process(
    path: str,
    root: str,
    *,
    is_directory: bool = False,
    supported_suffixes: Collection[str],
) -> bool:
    if is_temporary_file(path):
        return False

    resolved = Path(path).resolve()
    root_resolved = Path(root).resolve()
    try:
        relative = resolved.relative_to(root_resolved)
    except ValueError:
        return False

    if any(part.startswith(".") for part in relative.parts):
        return False

    if not is_directory and resolved.suffix.lower() not in supported_suffixes:
        return False

    return True
