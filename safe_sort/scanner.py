from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from utils import is_hidden_or_system, is_safesort_folder, setup_logging


@dataclass
class ScanResult:
    folder: Path
    files: list[Path] = field(default_factory=list)
    skipped: list[tuple[Path, str]] = field(default_factory=list)


def _iter_children(folder: Path) -> Iterable[Path]:
    try:
        yield from folder.iterdir()
    except PermissionError:
        return
    except OSError:
        return


def scan_folder(folder: Path, include_subfolders: bool = False) -> ScanResult:
    logger = setup_logging()
    folder = folder.expanduser().resolve()
    result = ScanResult(folder=folder)
    logger.info("scan start folder=%s include_subfolders=%s", folder, include_subfolders)

    def visit(current: Path) -> None:
        for item in _iter_children(current):
            try:
                if item.is_symlink():
                    result.skipped.append((item, "symlink"))
                    logger.info("skipped symlink path=%s", item)
                    continue
                if is_hidden_or_system(item):
                    result.skipped.append((item, "hidden_or_system"))
                    logger.info("skipped hidden/system path=%s", item)
                    continue
                if item.is_dir():
                    if is_safesort_folder(item):
                        result.skipped.append((item, "safesort_folder"))
                        logger.info("skipped safesort folder path=%s", item)
                        continue
                    if include_subfolders:
                        visit(item)
                    continue
                if item.is_file():
                    result.files.append(item)
            except PermissionError:
                result.skipped.append((item, "permission_denied"))
                logger.warning("permission denied path=%s", item)
            except OSError as exc:
                result.skipped.append((item, str(exc)))
                logger.warning("skipped path=%s error=%s", item, exc)

    visit(folder)
    logger.info("scan end folder=%s files_found=%s skipped=%s", folder, len(result.files), len(result.skipped))
    return result
