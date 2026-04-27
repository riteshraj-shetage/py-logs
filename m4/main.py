#!/usr/bin/env python3
"""
Automation Suite — Basic Version (m4)
======================================
CLI entry point.  Run with:

    python main.py          # interactive menu
    python main.py --help   # see argparse sub-commands
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Logging — writes to both stdout and logs/automation.log
# ---------------------------------------------------------------------------
LOG_FILE = Path(__file__).parent / "logs" / "automation.log"
LOG_FILE.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("automation_suite")

# ---------------------------------------------------------------------------
# Lazy imports so the menu still shows even if deps are missing
# ---------------------------------------------------------------------------
try:
    from modules.file_organizer import FileOrganizer
    from modules.scraper import WebScraper
    _MODULES_OK = True
except ImportError as _imp_err:  # pragma: no cover
    _MODULES_OK = False
    _IMPORT_ERROR = _imp_err


# ---------------------------------------------------------------------------
# Helper — load settings
# ---------------------------------------------------------------------------
_SETTINGS_PATH = Path(__file__).parent / "config" / "settings.json"


def _load_settings() -> dict:
    try:
        return json.loads(_SETTINGS_PATH.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Could not load settings.json: %s — using defaults", exc)
        return {}


# ---------------------------------------------------------------------------
# File Organizer menu
# ---------------------------------------------------------------------------

def _run_file_organizer(settings: dict) -> None:
    """Interactive sub-menu for the File Organizer."""
    print("\n" + "=" * 40)
    print("  FILE ORGANIZER")
    print("=" * 40)
    source = input("  Source folder path: ").strip()
    if not source:
        print("  [!] No path entered.")
        return

    dest_input = input("  Destination folder [leave blank for default]: ").strip()
    dest = dest_input if dest_input else None

    try:
        organizer = FileOrganizer(source, dest)
    except Exception as exc:
        print(f"  [!] Error: {exc}")
        return

    print("\n  What would you like to do?")
    print("    1. Preview (no changes)")
    print("    2. Organize files")
    print("    3. Undo last run")
    print("    4. Show statistics")
    print("    5. Back")
    choice = input("  Choice: ").strip()

    if choice == "1":
        organizer.preview()
    elif choice == "2":
        print("\n  Organizing…")
        try:
            result = organizer.organize()
            cats: dict = result.pop("categories", {})
            print(f"\n  Done! Moved {result['moved']} file(s), {result['errors']} error(s).")
            if cats:
                for cat, count in sorted(cats.items()):
                    print(f"    {cat}: {count}")
        except ValueError as exc:
            print(f"  [!] {exc}")
    elif choice == "3":
        result = organizer.undo_last_run()
        print(f"\n  Restored {result['restored']} file(s), {result['errors']} error(s).")
    elif choice == "4":
        stats = organizer.get_statistics()
        if stats:
            print("\n  Files currently in destination:")
            for cat, count in sorted(stats.items()):
                print(f"    {cat}: {count}")
        else:
            print("  (destination is empty or does not exist)")
    elif choice == "5":
        return
    else:
        print("  [!] Invalid choice.")


# ---------------------------------------------------------------------------
# Web Scraper menu
# ---------------------------------------------------------------------------

def _run_scraper(settings: dict) -> None:
    """Interactive sub-menu for the Web Scraper."""
    if not _MODULES_OK:
        print(f"  [!] Module import failed: {_IMPORT_ERROR}")
        return

    print("\n" + "=" * 40)
    print("  WEB SCRAPER")
    print("=" * 40)
    url = input("  Target URL (e.g. https://example.com): ").strip()
    if not url:
        print("  [!] No URL entered.")
        return
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    scraper_cfg = settings.get("scraper", {})
    delay = float(scraper_cfg.get("default_delay", 1.0))
    timeout = int(scraper_cfg.get("timeout", 10))
    max_retries = int(scraper_cfg.get("max_retries", 3))

    try:
        scraper = WebScraper(url, delay=delay, timeout=timeout, max_retries=max_retries)
    except RuntimeError as exc:
        print(f"  [!] {exc}")
        return

    print("\n  What would you like to scrape?")
    print("    1. Links")
    print("    2. Paragraph text")
    print("    3. Headings (h1/h2/h3)")
    print("    4. Images")
    print("    5. Back")
    choice = input("  Choice: ").strip()

    scrape_map = {
        "1": ("links",     scraper.scrape_links,    "links"),
        "2": ("text",      scraper.scrape_text,     "paragraphs"),
        "3": ("headings",  scraper.scrape_headings, "headings"),
        "4": ("images",    scraper.scrape_images,   "images"),
    }

    if choice == "5":
        return
    if choice not in scrape_map:
        print("  [!] Invalid choice.")
        return

    label, method, key = scrape_map[choice]
    print(f"\n  Scraping {label} from {url} …")
    result = method(url)

    if "error" in result:
        print(f"  [!] {result['error']}")
        return

    items = result.get(key, [])
    print(f"\n  Found {result['count']} {label}:")
    for item in items[:20]:  # cap display at 20
        print(f"    {item}")
    if result["count"] > 20:
        print(f"    … and {result['count'] - 20} more.")

    save = input("\n  Save results to file? [y/N]: ").strip().lower()
    if save == "y":
        out_name = input("  Filename [scrape_results.json]: ").strip() or "scrape_results.json"
        path = scraper.save_results(result, out_name)
        print(f"  Saved → {path}")


# ---------------------------------------------------------------------------
# Interactive menu
# ---------------------------------------------------------------------------

def interactive_menu() -> None:
    """Run the main interactive menu loop."""
    settings = _load_settings()

    while True:
        print("\n" + "=" * 40)
        print("  AUTOMATION SUITE")
        print("=" * 40)
        print("  1. File Organizer")
        print("  2. Web Scraper")
        print("  3. Exit")
        print("=" * 40)
        choice = input("  Choose an option: ").strip()

        if choice == "1":
            if not _MODULES_OK:
                print(f"  [!] Modules unavailable: {_IMPORT_ERROR}")
            else:
                _run_file_organizer(settings)
        elif choice == "2":
            _run_scraper(settings)
        elif choice == "3":
            print("\n  Goodbye!\n")
            sys.exit(0)
        else:
            print("  [!] Invalid option, please try again.")


# ---------------------------------------------------------------------------
# argparse CLI (non-interactive mode)
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Automation Suite — File Organizer & Web Scraper",
    )
    sub = parser.add_subparsers(dest="command")

    # -- organize ---------------------------------------------------------
    org = sub.add_parser("organize", help="Organize files in a folder")
    org.add_argument("source", help="Source folder to organize")
    org.add_argument("--dest", default=None, help="Destination root (default: source/Organized)")
    org.add_argument("--preview", action="store_true", help="Preview only, no file moves")
    org.add_argument("--undo", action="store_true", help="Undo the last organize run")
    org.add_argument("--stats", action="store_true", help="Show current statistics")

    # -- scrape -----------------------------------------------------------
    sc = sub.add_parser("scrape", help="Scrape a web page")
    sc.add_argument("url", help="URL to scrape")
    sc.add_argument(
        "--mode",
        choices=["links", "text", "headings", "images"],
        default="links",
        help="What to scrape (default: links)",
    )
    sc.add_argument("--save", metavar="FILE", help="Save JSON results to FILE")
    sc.add_argument("--delay", type=float, default=1.0, help="Delay between requests (s)")

    return parser


def run_cli(args: argparse.Namespace) -> None:
    """Execute a parsed argparse command."""
    settings = _load_settings()

    if args.command == "organize":
        organizer = FileOrganizer(args.source, args.dest)
        if args.preview:
            organizer.preview()
        elif args.undo:
            r = organizer.undo_last_run()
            print(f"Restored {r['restored']} file(s), {r['errors']} error(s).")
        elif args.stats:
            stats = organizer.get_statistics()
            for cat, count in sorted(stats.items()):
                print(f"  {cat}: {count}")
        else:
            result = organizer.organize()
            cats = result.pop("categories", {})
            print(f"Moved {result['moved']} file(s). Errors: {result['errors']}")
            for cat, count in sorted(cats.items()):
                print(f"  {cat}: {count}")

    elif args.command == "scrape":
        scraper = WebScraper(args.url, delay=args.delay)
        dispatch = {
            "links":    (scraper.scrape_links,    "links"),
            "text":     (scraper.scrape_text,     "paragraphs"),
            "headings": (scraper.scrape_headings, "headings"),
            "images":   (scraper.scrape_images,   "images"),
        }
        method, key = dispatch[args.mode]
        result = method(args.url)
        if "error" in result:
            print(f"[!] {result['error']}")
            sys.exit(1)
        for item in result.get(key, []):
            print(item)
        if args.save:
            path = scraper.save_results(result, args.save)
            print(f"\nSaved → {path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = build_parser()
    if len(sys.argv) > 1:
        parsed = parser.parse_args()
        try:
            run_cli(parsed)
        except (ValueError, RuntimeError) as exc:
            print(f"[!] Error: {exc}")
            sys.exit(1)
    else:
        interactive_menu()
