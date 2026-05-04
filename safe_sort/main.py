from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from categories import CATEGORY_FOLDERS
from scanner import scan_folder
from sorter import MovePlan, MoveResult, category_counts, execute_moves, export_report, plan_moves, undo_moves
from utils import setup_logging


class SafeSortApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("SafeSort")
        self.geometry("1120x740")
        self.minsize(920, 600)
        self.configure(bg="#f7f2ea")

        self.logger = setup_logging()
        self.selected_folder = tk.StringVar()
        self.include_subfolders = tk.BooleanVar(value=False)
        self.summary_text = tk.StringVar(value="Choose a folder, then scan to preview what SafeSort will move.")
        self.safety_text = tk.StringVar(value="SafeSort never deletes files and never overwrites existing files.")

        self.plans: list[MovePlan] = []
        self.last_results: list[MoveResult] = []

        self._configure_style()
        self._build_ui()
        self._set_initial_quick_folder()

    def _configure_style(self) -> None:
        self.colors = {
            "bg": "#f7f2ea",
            "panel": "#fffaf2",
            "panel_alt": "#fdf4e7",
            "ink": "#24312f",
            "muted": "#64716d",
            "line": "#e7d9c7",
            "teal": "#147d75",
            "teal_dark": "#0f625c",
            "coral": "#d65f4c",
            "coral_dark": "#b94939",
            "gold": "#e7b95b",
            "table": "#fffdf8",
            "table_alt": "#f8efe1",
            "select": "#d7eee9",
        }

        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(".", background=self.colors["bg"], foreground=self.colors["ink"], font=("Segoe UI", 10))
        style.configure("App.TFrame", background=self.colors["bg"])
        style.configure("Panel.TFrame", background=self.colors["panel"], relief="flat", borderwidth=1)
        style.configure("Header.TFrame", background=self.colors["teal"])
        style.configure("HeaderTitle.TLabel", background=self.colors["teal"], foreground="#fffdf8", font=("Segoe UI", 25, "bold"))
        style.configure("HeaderSubtitle.TLabel", background=self.colors["teal"], foreground="#d8f2ed", font=("Segoe UI", 11))
        style.configure("Body.TLabel", background=self.colors["bg"], foreground=self.colors["ink"])
        style.configure("Muted.TLabel", background=self.colors["panel"], foreground=self.colors["muted"])
        style.configure("PanelTitle.TLabel", background=self.colors["panel"], foreground=self.colors["ink"], font=("Segoe UI", 11, "bold"))
        style.configure("Summary.TLabel", background=self.colors["panel"], foreground=self.colors["ink"], font=("Segoe UI", 10, "bold"))
        style.configure("Safety.TLabel", background=self.colors["panel_alt"], foreground=self.colors["teal_dark"], font=("Segoe UI", 10, "bold"))

        style.configure(
            "Primary.TButton",
            background=self.colors["coral"],
            foreground="#fffdf8",
            bordercolor=self.colors["coral"],
            focusthickness=0,
            padding=(14, 8),
            font=("Segoe UI", 10, "bold"),
        )
        style.map("Primary.TButton", background=[("active", self.colors["coral_dark"]), ("disabled", "#d7c5bb")])
        style.configure(
            "Action.TButton",
            background=self.colors["teal"],
            foreground="#fffdf8",
            bordercolor=self.colors["teal"],
            focusthickness=0,
            padding=(12, 7),
            font=("Segoe UI", 10, "bold"),
        )
        style.map("Action.TButton", background=[("active", self.colors["teal_dark"]), ("disabled", "#aebdb9")])
        style.configure(
            "Soft.TButton",
            background="#eadbc7",
            foreground=self.colors["ink"],
            bordercolor="#eadbc7",
            focusthickness=0,
            padding=(11, 7),
        )
        style.map("Soft.TButton", background=[("active", "#dcc9af")])
        style.configure(
            "Quick.TButton",
            background="#fff5e5",
            foreground=self.colors["teal_dark"],
            bordercolor=self.colors["line"],
            focusthickness=0,
            padding=(10, 5),
        )
        style.map("Quick.TButton", background=[("active", "#f4e4cb")])

        style.configure(
            "TEntry",
            fieldbackground="#fffdf8",
            bordercolor=self.colors["line"],
            lightcolor=self.colors["line"],
            darkcolor=self.colors["line"],
            padding=6,
        )
        style.configure("TCheckbutton", background=self.colors["bg"], foreground=self.colors["ink"])
        style.map("TCheckbutton", background=[("active", self.colors["bg"])])

        style.configure(
            "Treeview",
            background=self.colors["table"],
            fieldbackground=self.colors["table"],
            foreground=self.colors["ink"],
            rowheight=30,
            bordercolor=self.colors["line"],
            lightcolor=self.colors["line"],
            darkcolor=self.colors["line"],
        )
        style.configure(
            "Treeview.Heading",
            background="#e8f1ec",
            foreground=self.colors["teal_dark"],
            relief="flat",
            padding=(8, 7),
            font=("Segoe UI", 10, "bold"),
        )
        style.map("Treeview", background=[("selected", self.colors["select"])], foreground=[("selected", self.colors["ink"])])
        style.configure("Vertical.TScrollbar", background="#eadbc7", troughcolor=self.colors["panel"], bordercolor=self.colors["line"])

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        header = ttk.Frame(self, padding=(24, 22, 24, 18), style="Header.TFrame")
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)

        ttk.Label(header, text="SafeSort", style="HeaderTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="Organise messy folders safely.", style="HeaderSubtitle.TLabel").grid(row=1, column=0, sticky="w", pady=(2, 0))
        ttk.Label(
            header,
            text="Preview first. Move safely. Undo when needed.",
            style="HeaderSubtitle.TLabel",
        ).grid(row=0, column=1, rowspan=2, sticky="e")

        controls = ttk.Frame(self, padding=(18, 16), style="Panel.TFrame")
        controls.grid(row=1, column=0, sticky="ew")
        controls.columnconfigure(1, weight=1)

        ttk.Button(controls, text="Choose Folder", command=self.choose_folder, style="Soft.TButton").grid(row=0, column=0, padx=(0, 10), pady=4)
        ttk.Entry(controls, textvariable=self.selected_folder).grid(row=0, column=1, sticky="ew", pady=4)
        ttk.Checkbutton(controls, text="Include subfolders", variable=self.include_subfolders).grid(row=0, column=2, padx=8)
        ttk.Button(controls, text="Scan Folder", command=self.scan, style="Action.TButton").grid(row=0, column=3, padx=4)
        ttk.Button(controls, text="Sort This Folder", command=self.sort_folder, style="Primary.TButton").grid(row=0, column=4, padx=4)
        self.undo_button = ttk.Button(controls, text="Undo Last Sort", command=self.undo_last_sort, state="disabled", style="Soft.TButton")
        self.undo_button.grid(row=0, column=5, padx=4)
        ttk.Button(controls, text="Export Report", command=self.export, style="Soft.TButton").grid(row=0, column=6, padx=(4, 0))

        quick = ttk.Frame(self, padding=(20, 12, 20, 10), style="App.TFrame")
        quick.grid(row=2, column=0, sticky="ew")
        ttk.Label(quick, text="Quick folders:", style="Body.TLabel").pack(side="left")
        for label, folder in self.quick_folders().items():
            ttk.Button(quick, text=label, command=lambda p=folder: self.set_folder(p), style="Quick.TButton").pack(side="left", padx=5)

        main = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 14))

        left = ttk.Frame(main, padding=(16, 16), style="Panel.TFrame")
        right = ttk.Frame(main, padding=(16, 16), style="Panel.TFrame")
        main.add(left, weight=1)
        main.add(right, weight=4)

        ttk.Label(left, text="Folder snapshot", style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(left, textvariable=self.summary_text, wraplength=260, style="Summary.TLabel").pack(anchor="w", pady=(8, 14))
        self.counts_tree = ttk.Treeview(left, columns=("count",), show="headings", height=12)
        self.counts_tree.heading("count", text="Files")
        self.counts_tree.column("count", width=80, anchor="center")
        self.counts_tree.pack(fill="both", expand=True)
        self.counts_tree["displaycolumns"] = ("count",)
        self.counts_tree.configure(show="tree headings")
        self.counts_tree.heading("#0", text="Category")
        self.counts_tree.column("#0", width=160, anchor="w")

        ttk.Label(right, text="Preview of planned moves", style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(right, text="Nothing moves until you press Sort This Folder and confirm.", style="Muted.TLabel").pack(anchor="w", pady=(2, 8))
        table_frame = ttk.Frame(right, style="Panel.TFrame")
        table_frame.pack(fill="both", expand=True, pady=(4, 0))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("original", "category", "destination")
        self.preview_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.preview_tree.heading("original", text="Original file path")
        self.preview_tree.heading("category", text="Category")
        self.preview_tree.heading("destination", text="Destination path")
        self.preview_tree.column("original", width=360)
        self.preview_tree.column("category", width=110, anchor="center")
        self.preview_tree.column("destination", width=360)
        self.preview_tree.grid(row=0, column=0, sticky="nsew")

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.preview_tree.yview)
        scroll_y.grid(row=0, column=1, sticky="ns")
        self.preview_tree.configure(yscrollcommand=scroll_y.set)

        footer = ttk.Frame(self, padding=(20, 12, 20, 18), style="Panel.TFrame")
        footer.grid(row=4, column=0, sticky="ew")
        ttk.Label(footer, textvariable=self.safety_text, style="Safety.TLabel").pack(anchor="w")

    @staticmethod
    def quick_folders() -> dict[str, Path]:
        home = Path.home()
        return {
            "Downloads": home / "Downloads",
            "Desktop": home / "Desktop",
            "Documents": home / "Documents",
            "Pictures": home / "Pictures",
        }

    def _set_initial_quick_folder(self) -> None:
        downloads = self.quick_folders()["Downloads"]
        if downloads.exists():
            self.selected_folder.set(str(downloads))

    def set_folder(self, folder: Path) -> None:
        self.selected_folder.set(str(folder))

    def choose_folder(self) -> None:
        folder = filedialog.askdirectory(title="Choose a folder to organise")
        if folder:
            self.selected_folder.set(folder)

    def scan(self) -> None:
        folder = self._validated_folder()
        if folder is None:
            return
        result = scan_folder(folder, self.include_subfolders.get())
        self.plans = plan_moves(result.files, result.folder)
        self.last_results = []
        self.undo_button.configure(state="disabled")
        self.refresh_preview(result.skipped)

    def refresh_preview(self, skipped: list[tuple[Path, str]] | None = None) -> None:
        skipped = skipped or []
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        for item in self.counts_tree.get_children():
            self.counts_tree.delete(item)

        counts = category_counts(self.plans)
        for category in CATEGORY_FOLDERS:
            self.counts_tree.insert("", "end", text=category, values=(counts.get(category, 0),), tags=("count_row",))

        self.counts_tree.tag_configure("count_row", background=self.colors["table"])

        for index, plan in enumerate(self.plans):
            self.preview_tree.insert(
                "",
                "end",
                values=(str(plan.original_path), plan.category, str(plan.destination_path)),
                tags=("even" if index % 2 == 0 else "odd",),
            )
        self.preview_tree.tag_configure("even", background=self.colors["table"])
        self.preview_tree.tag_configure("odd", background=self.colors["table_alt"])

        files_found = len(self.plans) + len(skipped)
        self.summary_text.set(
            f"Total files found: {files_found}\n"
            f"Files planned to move: {len(self.plans)}\n"
            f"Skipped safely: {len(skipped)}\n"
            f"Destination folders: {', '.join(CATEGORY_FOLDERS)}"
        )

    def sort_folder(self) -> None:
        if not self.plans:
            messagebox.showinfo("SafeSort", "Scan a folder first so you can preview the moves.")
            return
        confirmed = messagebox.askyesno(
            "Confirm sort",
            f"This will move {len(self.plans)} files into organised subfolders.\n\n"
            "Nothing will be deleted or overwritten.",
        )
        if not confirmed:
            return
        self.last_results = execute_moves(self.plans)
        moved = sum(result.moved for result in self.last_results)
        failed = len(self.last_results) - moved
        self.undo_button.configure(state="normal" if moved else "disabled")
        self.summary_text.set(f"Sort complete.\nMoved: {moved}\nFailed: {failed}\nYou can undo the last sort in this session.")
        if failed:
            messagebox.showwarning("SafeSort", f"Moved {moved} files. {failed} files could not be moved.")
        else:
            messagebox.showinfo("SafeSort", f"Moved {moved} files safely.")

    def undo_last_sort(self) -> None:
        if not self.last_results:
            messagebox.showinfo("SafeSort", "There is no sort operation to undo.")
            return
        result = undo_moves(self.last_results)
        self.undo_button.configure(state="disabled")
        self.summary_text.set(f"Undo complete.\nRestored: {result.restored}\nFailed: {result.failed}")
        if result.failed:
            messagebox.showwarning("SafeSort", f"Restored {result.restored} files. {result.failed} files could not be restored.")
        else:
            messagebox.showinfo("SafeSort", f"Restored {result.restored} files.")

    def export(self) -> None:
        if not self.plans:
            messagebox.showinfo("SafeSort", "Scan a folder first so there is a report to export.")
            return
        path = filedialog.asksaveasfilename(
            title="Export SafeSort report",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not path:
            return
        try:
            export_report(Path(path), self.plans, self.last_results)
            messagebox.showinfo("SafeSort", f"Report exported to:\n{path}")
        except Exception as exc:
            messagebox.showerror("SafeSort", f"Could not export report:\n{exc}")

    def _validated_folder(self) -> Path | None:
        value = self.selected_folder.get().strip()
        if not value:
            messagebox.showinfo("SafeSort", "Choose a folder first.")
            return None
        folder = Path(value)
        if not folder.exists() or not folder.is_dir():
            messagebox.showerror("SafeSort", "That folder does not exist.")
            return None
        return folder


def main() -> None:
    app = SafeSortApp()
    app.mainloop()


if __name__ == "__main__":
    main()
