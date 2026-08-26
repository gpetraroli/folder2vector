import os


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
