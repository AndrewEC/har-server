from pathlib import Path


_root_path: Path | None = None


def set_root_path(path: Path | None):
    global _root_path
    _root_path = path


def get_root_path() -> Path:
    global _root_path
    return _root_path  # type: ignore
