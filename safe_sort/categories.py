from __future__ import annotations

from pathlib import Path


CATEGORY_FOLDERS = (
    "Images",
    "Screenshots",
    "Documents",
    "Spreadsheets",
    "Presentations",
    "Videos",
    "Audio",
    "Archives",
    "Installers",
    "Code",
    "Other",
)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".heic"}
SCREENSHOT_MARKERS = ("screenshot", "screen shot", "snip", "capture")

EXTENSION_CATEGORIES = {
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt"},
    "Spreadsheets": {".xls", ".xlsx", ".csv", ".ods"},
    "Presentations": {".ppt", ".pptx", ".odp"},
    "Videos": {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".webm"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".m4a"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Installers": {".exe", ".msi", ".dmg", ".pkg"},
    "Code": {
        ".py",
        ".js",
        ".html",
        ".css",
        ".json",
        ".xml",
        ".sql",
        ".cpp",
        ".c",
        ".cs",
        ".java",
        ".php",
        ".ts",
        ".tsx",
        ".jsx",
    },
}


def is_screenshot(path: Path) -> bool:
    """Return True when an image filename looks like a screenshot."""
    suffix = path.suffix.lower()
    if suffix not in IMAGE_EXTENSIONS:
        return False
    name = path.stem.lower()
    return any(marker in name for marker in SCREENSHOT_MARKERS)


def categorize_file(path: Path) -> str:
    """Map a file path to one of SafeSort's destination folder categories."""
    suffix = path.suffix.lower()
    if is_screenshot(path):
        return "Screenshots"
    if suffix in IMAGE_EXTENSIONS:
        return "Images"
    for category, extensions in EXTENSION_CATEGORIES.items():
        if suffix in extensions:
            return category
    return "Other"
