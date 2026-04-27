"""
File Organizer Module
=====================
Organizes files in a folder into category subfolders based on file extension.
"""

import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Default category → extension mapping
DEFAULT_CATEGORIES: dict[str, list[str]] = {
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".xlsx", ".csv", ".pptx"],
    "Images":    [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    "Videos":    [".mp4", ".avi", ".mov", ".wmv", ".mkv"],
    "Music":     [".mp3", ".wav", ".aac", ".flac", ".ogg"],
    "Archives":  [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Code":      [".py", ".js", ".html", ".css", ".java", ".cpp", ".ts"],
}


class FileOrganizer:
    """Organize files in a source folder into categorized subfolders.

    Parameters
    ----------
    source_folder:
        The folder whose loose files will be organized.
    dest_folder:
        Root destination for category subfolders.  Defaults to
        ``<source_folder>/Organized/`` when *None*.
    """

    UNDO_LOG_NAME = ".organizer_undo.json"

    def __init__(self, source_folder: str, dest_folder: str | None = None) -> None:
        self.source = Path(source_folder)
        self.dest = Path(dest_folder) if dest_folder else self.source / "Organized"

        # Build extension → category lookup
        self.file_categories: dict[str, list[str]] = dict(DEFAULT_CATEGORIES)
        self._ext_map: dict[str, str] = {}
        self._rebuild_ext_map()

        self._undo_log: list[dict[str, str]] = []

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def _rebuild_ext_map(self) -> None:
        """Refresh the extension → category reverse-lookup dict."""
        self._ext_map = {}
        for category, exts in self.file_categories.items():
            for ext in exts:
                self._ext_map[ext.lower()] = category

    def _category_for(self, path: Path) -> str:
        """Return the category name for *path* based on its extension."""
        return self._ext_map.get(path.suffix.lower(), "Others")

    def _unique_dest(self, dest_path: Path) -> Path:
        """Return a unique destination path, appending a timestamp if needed."""
        if not dest_path.exists():
            return dest_path
        stem = dest_path.stem
        suffix = dest_path.suffix
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return dest_path.with_name(f"{stem}_{ts}{suffix}")

    def _validate_source(self) -> None:
        """Raise ValueError with a helpful message if source folder is invalid."""
        if not self.source.exists():
            raise ValueError(
                f"Source folder does not exist: {self.source}\n"
                "Please provide the path to an existing directory."
            )
        if not self.source.is_dir():
            raise ValueError(f"Source path is not a directory: {self.source}")

    def _iter_source_files(self) -> list[Path]:
        """Return all direct-child files in the source folder (non-recursive)."""
        return [
            p for p in self.source.iterdir()
            if p.is_file() and not p.name.startswith(".")
            and p.name != self.UNDO_LOG_NAME
        ]

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def preview(self) -> dict[str, list[str]]:
        """Show what WOULD be moved without touching the filesystem.

        Returns
        -------
        dict
            ``{category: [list of filenames]}``
        """
        self._validate_source()
        plan: dict[str, list[str]] = {}
        for file in self._iter_source_files():
            cat = self._category_for(file)
            plan.setdefault(cat, []).append(file.name)

        if not plan:
            print("  (no files to organize)")
        else:
            print(f"\n  Preview — source: {self.source}")
            print(f"  Destination root: {self.dest}\n")
            for cat, names in sorted(plan.items()):
                print(f"  [{cat}]")
                for name in names:
                    print(f"    {name}")
        return plan

    def organize(self) -> dict[str, int]:
        """Move files from source into categorized subfolders under dest.

        Returns
        -------
        dict
            ``{"moved": n, "skipped": n, "errors": n, "categories": {cat: count}}``
        """
        self._validate_source()
        self.dest.mkdir(parents=True, exist_ok=True)

        summary: dict[str, int] = {"moved": 0, "skipped": 0, "errors": 0}
        category_counts: dict[str, int] = {}
        self._undo_log = []

        for file in self._iter_source_files():
            cat = self._category_for(file)
            cat_dir = self.dest / cat
            cat_dir.mkdir(parents=True, exist_ok=True)
            target = self._unique_dest(cat_dir / file.name)
            try:
                shutil.move(str(file), str(target))
                self._undo_log.append({"from": str(target), "to": str(file)})
                category_counts[cat] = category_counts.get(cat, 0) + 1
                summary["moved"] += 1
                logger.info("Moved %s → %s", file.name, target)
            except Exception as exc:  # pragma: no cover
                summary["errors"] += 1
                logger.error("Failed to move %s: %s", file.name, exc)

        summary["categories"] = category_counts  # type: ignore[assignment]

        # Persist undo log next to the dest folder
        undo_path = self.dest / self.UNDO_LOG_NAME
        try:
            undo_path.write_text(json.dumps(self._undo_log, indent=2))
        except OSError as exc:
            logger.warning("Could not write undo log: %s", exc)

        logger.info(
            "organize() complete — moved=%d skipped=%d errors=%d",
            summary["moved"], summary["skipped"], summary["errors"],
        )
        return summary

    def undo_last_run(self) -> dict[str, int]:
        """Reverse the last organize() run by reading the undo log.

        Returns
        -------
        dict
            ``{"restored": n, "errors": n}``
        """
        undo_path = self.dest / self.UNDO_LOG_NAME
        if not undo_path.exists():
            print("  No undo log found — nothing to reverse.")
            return {"restored": 0, "errors": 0}

        try:
            entries: list[dict[str, str]] = json.loads(undo_path.read_text())
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Could not read undo log: %s", exc)
            return {"restored": 0, "errors": 1}

        restored = errors = 0
        for entry in entries:
            src, dst = Path(entry["from"]), Path(entry["to"])
            if not src.exists():
                logger.warning("Undo source missing, skipping: %s", src)
                errors += 1
                continue
            try:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
                restored += 1
                logger.info("Restored %s → %s", src.name, dst)
            except Exception as exc:  # pragma: no cover
                errors += 1
                logger.error("Failed to restore %s: %s", src.name, exc)

        undo_path.unlink(missing_ok=True)
        logger.info("undo_last_run() — restored=%d errors=%d", restored, errors)
        return {"restored": restored, "errors": errors}

    def get_statistics(self) -> dict[str, int]:
        """Return file counts per category currently inside dest.

        Returns
        -------
        dict
            ``{category: file_count}``
        """
        if not self.dest.exists():
            return {}
        stats: dict[str, int] = {}
        for cat_dir in sorted(self.dest.iterdir()):
            if cat_dir.is_dir():
                count = sum(1 for p in cat_dir.iterdir() if p.is_file())
                if count:
                    stats[cat_dir.name] = count
        return stats
