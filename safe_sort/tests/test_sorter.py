from pathlib import Path

from scanner import scan_folder
from sorter import execute_moves, export_report, plan_moves, safe_destination_path, undo_moves


def test_safe_destination_path_adds_number_for_duplicate(tmp_path):
    destination = tmp_path / "Images" / "photo.jpg"
    destination.parent.mkdir()
    destination.write_text("first")
    (destination.parent / "photo (1).jpg").write_text("second")

    assert safe_destination_path(destination) == destination.parent / "photo (2).jpg"


def test_move_planning_does_not_execute(tmp_path):
    source = tmp_path / "report.pdf"
    source.write_text("hello")

    plans = plan_moves([source], tmp_path)

    assert source.exists()
    assert len(plans) == 1
    assert plans[0].destination_path == tmp_path / "Documents" / "report.pdf"
    assert not plans[0].destination_path.exists()


def test_sorting_files_into_correct_folders(tmp_path):
    image = tmp_path / "photo.png"
    document = tmp_path / "paper.pdf"
    screenshot = tmp_path / "screenshot one.jpg"
    image.write_text("image")
    document.write_text("doc")
    screenshot.write_text("shot")

    plans = plan_moves([image, document, screenshot], tmp_path)
    results = execute_moves(plans)

    assert all(result.moved for result in results)
    assert (tmp_path / "Images" / "photo.png").exists()
    assert (tmp_path / "Documents" / "paper.pdf").exists()
    assert (tmp_path / "Screenshots" / "screenshot one.jpg").exists()
    assert not image.exists()


def test_sorting_never_overwrites_existing_destination(tmp_path):
    source = tmp_path / "photo.jpg"
    source.write_text("new")
    destination = tmp_path / "Images" / "photo.jpg"
    destination.parent.mkdir()
    destination.write_text("existing")

    results = execute_moves(plan_moves([source], tmp_path))

    assert results[0].moved
    assert destination.read_text() == "existing"
    assert (tmp_path / "Images" / "photo (1).jpg").read_text() == "new"


def test_scan_ignores_safesort_folders_and_subfolders_by_default(tmp_path):
    root_file = tmp_path / "root.pdf"
    nested = tmp_path / "nested"
    safe_folder = tmp_path / "Images"
    root_file.write_text("root")
    nested.mkdir()
    safe_folder.mkdir()
    (nested / "nested.pdf").write_text("nested")
    (safe_folder / "already.png").write_text("already")

    result = scan_folder(tmp_path, include_subfolders=False)

    assert result.files == [root_file]


def test_scan_can_include_subfolders(tmp_path):
    nested = tmp_path / "nested"
    nested.mkdir()
    file_path = nested / "nested.pdf"
    file_path.write_text("nested")

    result = scan_folder(tmp_path, include_subfolders=True)

    assert file_path in result.files


def test_undo_moves_files_back_without_overwriting(tmp_path):
    source = tmp_path / "paper.pdf"
    source.write_text("original")
    results = execute_moves(plan_moves([source], tmp_path))
    source.write_text("new file at original path")

    undo = undo_moves(results)

    assert undo.restored == 1
    assert undo.failed == 0
    assert source.read_text() == "new file at original path"
    assert (tmp_path / "paper (1).pdf").read_text() == "original"


def test_export_report_writes_csv(tmp_path):
    source = tmp_path / "paper.pdf"
    source.write_text("original")
    plans = plan_moves([source], tmp_path)
    report = tmp_path / "report.csv"

    export_report(report, plans)

    text = report.read_text(encoding="utf-8")
    assert "original_path,destination_path,category,moved,error" in text
    assert "Documents" in text
