[README.md](https://github.com/user-attachments/files/27328797/README.md)
# SafeSort

SafeSort is a simple Windows desktop app that turns a messy folder into organised subfolders in one click.

It is designed for normal Windows users who want to clean up folders like Downloads, Desktop, Documents, Pictures, or a random dump folder without worrying that files will be deleted or overwritten.

## What SafeSort Does

SafeSort scans one selected folder, previews the changes, then moves files into clear category folders:

- Images
- Screenshots
- Documents
- Spreadsheets
- Presentations
- Videos
- Audio
- Archives
- Installers
- Code
- Other

## Safety Rules

SafeSort V1 follows these rules:

- It never deletes files.
- It never overwrites files.
- It always shows a preview before moving anything.
- If a destination filename already exists, SafeSort creates a safe name such as `filename (1).ext`.
- Undo is available for the last sort operation in the current app session.
- Symlinks, hidden/system files, permission errors, and SafeSort-created category folders are skipped where practical.

## Install

Install Python 3 first. Then open PowerShell in the `safe_sort` folder and run:

```powershell
pip install -r requirements.txt
```

## Run

From the `safe_sort` folder:

```powershell
python main.py
```

## Package For Windows

From the `safe_sort` folder:

```powershell
pip install -r requirements.txt
pyinstaller --onefile --windowed --name SafeSort main.py
```

The packaged app will be created under `dist\SafeSort.exe`.

## Run Tests

From the `safe_sort` folder:

```powershell
python -m pytest tests
```

## Limitations In V1

- Undo only remembers the most recent sort operation while the app is open.
- SafeSort categorises by filename and extension, not by reading file contents.
- It does not detect duplicates.
- It does not sort the whole PC by default.
- It does not run in the background.
- It does not delete junk files.

## Next Feature Ideas

- Save sort history to disk so undo can survive app restarts.
- Add a clearer skipped-files panel.
- Add custom category rules.
- Add date-based folders such as Images\2026.
- Add a safer review step for very large folders.
