from pathlib import Path

from categories import categorize_file, is_screenshot


def test_category_detection_by_extension():
    examples = {
        "photo.jpg": "Images",
        "report.pdf": "Documents",
        "budget.xlsx": "Spreadsheets",
        "pitch.pptx": "Presentations",
        "movie.mp4": "Videos",
        "song.flac": "Audio",
        "backup.zip": "Archives",
        "setup.msi": "Installers",
        "script.py": "Code",
        "unknown.bin": "Other",
    }

    for filename, category in examples.items():
        assert categorize_file(Path(filename)) == category


def test_screenshot_detection_requires_image_extension():
    assert is_screenshot(Path("Screenshot 2026-05-04.png"))
    assert is_screenshot(Path("screen shot final.JPG"))
    assert is_screenshot(Path("quick-snip.webp"))
    assert categorize_file(Path("capture.jpeg")) == "Screenshots"
    assert not is_screenshot(Path("screenshot-notes.txt"))
    assert categorize_file(Path("screenshot-notes.txt")) == "Documents"
