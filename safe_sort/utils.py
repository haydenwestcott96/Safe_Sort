from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from categories import CATEGORY_FOLDERS


def app_root() -> Path:
    return Path(__file__).resolve().parent


def logs_dir() -> Path:
    folder = app_root() / "logs"
    folder.mkdir(exist_ok=True)
    return folder


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("safe_sort")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if logger.handlers:
        return logger

    log_file = logs_dir() / f"safesort-{datetime.now():%Y%m%d}.log"
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger


def is_hidden_or_system(path: Path) -> bool:
    """Best-effort hidden/system detection using names and Windows attributes."""
    name = path.name
    if name.startswith("."):
        return True

    try:
        import ctypes

        attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
        if attrs == -1:
            return False
        hidden = bool(attrs & 0x2)
        system = bool(attrs & 0x4)
        return hidden or system
    except Exception:
        return False


def is_safesort_folder(path: Path) -> bool:
    return path.is_dir() and path.name in CATEGORY_FOLDERS
