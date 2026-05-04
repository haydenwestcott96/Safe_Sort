from __future__ import annotations

import csv
import shutil
from dataclasses import dataclass
from pathlib import Path

from categories import CATEGORY_FOLDERS, categorize_file
from utils import setup_logging


@dataclass
class MovePlan:
    original_path: Path
    destination_path: Path
    category: str


@dataclass
class MoveResult:
    plan: MovePlan
    moved: bool = False
    final_path: Path | None = None
    error: str = ""


@dataclass
class UndoResult:
    restored: int = 0
    failed: int = 0
    errors: list[str] | None = None

    def __post_init__(self) -> None:
        if self.errors is None:
            self.errors = []


def safe_destination_path(destination: Path) -> Path:
    """Return a non-existing path by appending ' (n)' before the extension."""
    if not destination.exists():
        return destination

    parent = destination.parent
    stem = destination.stem
    suffix = destination.suffix
    counter = 1
    while True:
        candidate = parent / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def plan_moves(files: list[Path], root_folder: Path) -> list[MovePlan]:
    logger = setup_logging()
    root_folder = root_folder.expanduser().resolve()
    plans: list[MovePlan] = []
    for file_path in files:
        original = file_path.expanduser().resolve()
        category = categorize_file(original)
        destination = root_folder / category / original.name
        plans.append(MovePlan(original_path=original, destination_path=destination, category=category))
    logger.info("planned moves count=%s", len(plans))
    return plans


def category_counts(plans: list[MovePlan]) -> dict[str, int]:
    counts = {category: 0 for category in CATEGORY_FOLDERS}
    for plan in plans:
        counts[plan.category] = counts.get(plan.category, 0) + 1
    return counts


def execute_moves(plans: list[MovePlan]) -> list[MoveResult]:
    logger = setup_logging()
    results: list[MoveResult] = []
    for plan in plans:
        try:
            if not plan.original_path.exists():
                raise FileNotFoundError(f"Original file no longer exists: {plan.original_path}")
            plan.destination_path.parent.mkdir(parents=True, exist_ok=True)
            final_path = safe_destination_path(plan.destination_path)
            shutil.move(str(plan.original_path), str(final_path))
            results.append(MoveResult(plan=plan, moved=True, final_path=final_path))
            logger.info("moved original=%s destination=%s category=%s", plan.original_path, final_path, plan.category)
        except Exception as exc:
            results.append(MoveResult(plan=plan, moved=False, error=str(exc)))
            logger.error("move failed original=%s destination=%s error=%s", plan.original_path, plan.destination_path, exc)
    logger.info("completed moves moved=%s failed=%s", sum(r.moved for r in results), sum(not r.moved for r in results))
    return results


def undo_moves(results: list[MoveResult]) -> UndoResult:
    logger = setup_logging()
    undo = UndoResult()
    for result in reversed(results):
        if not result.moved or result.final_path is None:
            continue
        try:
            if not result.final_path.exists():
                raise FileNotFoundError(f"Moved file no longer exists: {result.final_path}")
            result.plan.original_path.parent.mkdir(parents=True, exist_ok=True)
            restore_path = safe_destination_path(result.plan.original_path)
            shutil.move(str(result.final_path), str(restore_path))
            undo.restored += 1
            logger.info("undo restored from=%s to=%s", result.final_path, restore_path)
        except Exception as exc:
            undo.failed += 1
            undo.errors.append(str(exc))
            logger.error("undo failed from=%s to=%s error=%s", result.final_path, result.plan.original_path, exc)
    logger.info("undo complete restored=%s failed=%s", undo.restored, undo.failed)
    return undo


def export_report(path: Path, plans: list[MovePlan], results: list[MoveResult] | None = None) -> None:
    results_by_original = {}
    if results:
        results_by_original = {result.plan.original_path: result for result in results}

    with path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=["original_path", "destination_path", "category", "moved", "error"],
        )
        writer.writeheader()
        for plan in plans:
            result = results_by_original.get(plan.original_path)
            writer.writerow(
                {
                    "original_path": str(plan.original_path),
                    "destination_path": str(result.final_path if result and result.final_path else plan.destination_path),
                    "category": plan.category,
                    "moved": "yes" if result and result.moved else "no",
                    "error": result.error if result else "",
                }
            )
