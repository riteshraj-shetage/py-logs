"""Notes manager module — add, view, search, edit, delete; persists to JSON."""

import json
import os
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "notes.json")


class NotesManager:
    def __init__(self):
        self.notes = []
        self._load()

    # ── persistence ───────────────────────────────────────────────────────────

    def _load(self):
        try:
            with open(DATA_FILE, "r") as f:
                self.notes = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.notes = []

    def _save(self):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w") as f:
            json.dump(self.notes, f, indent=2)

    # ── operations ────────────────────────────────────────────────────────────

    def _next_id(self):
        return max((n["id"] for n in self.notes), default=0) + 1

    def add(self, title, content):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        note = {"id": self._next_id(), "title": title, "content": content,
                "created": now, "modified": now}
        self.notes.append(note)
        self._save()
        return note

    def all_notes(self):
        return list(self.notes)

    def search(self, keyword):
        kw = keyword.lower()
        return [n for n in self.notes
                if kw in n["title"].lower() or kw in n["content"].lower()]

    def get(self, note_id):
        for n in self.notes:
            if n["id"] == note_id:
                return n
        return None

    def edit(self, note_id, title=None, content=None):
        note = self.get(note_id)
        if note is None:
            return False
        if title is not None:
            note["title"] = title
        if content is not None:
            note["content"] = content
        note["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        self._save()
        return True

    def delete(self, note_id):
        before = len(self.notes)
        self.notes = [n for n in self.notes if n["id"] != note_id]
        if len(self.notes) < before:
            self._save()
            return True
        return False


# ── display helpers ───────────────────────────────────────────────────────────

def _print_note(note):
    print(f"\n  [{note['id']}] {note['title']}")
    print(f"  Created: {note['created']}  |  Modified: {note['modified']}")
    print(f"  {'-' * 36}")
    print(f"  {note['content']}")


def _print_list(notes):
    if not notes:
        print("  No notes found.")
        return
    for n in notes:
        print(f"  [{n['id']:>3}]  {n['title']:<30}  {n['created']}")


# ── interactive session ───────────────────────────────────────────────────────

def run(manager: NotesManager):
    """Interactive notes loop."""
    while True:
        print("\n  NOTES MANAGER")
        print("  " + "-" * 36)
        print("  1. View all notes")
        print("  2. Add note")
        print("  3. Search notes")
        print("  4. Edit note")
        print("  5. Delete note")
        print("  6. Back to main menu")
        choice = input("\n  Choice: ").strip()

        if choice == "1":
            print()
            _print_list(manager.all_notes())

        elif choice == "2":
            title = input("  Title: ").strip()
            if not title:
                print("  ! Title cannot be empty.")
                continue
            content = input("  Content: ").strip()
            note = manager.add(title, content)
            print(f"  ✓ Note #{note['id']} saved.")

        elif choice == "3":
            kw = input("  Search keyword: ").strip()
            results = manager.search(kw)
            print()
            _print_list(results)

        elif choice == "4":
            try:
                nid = int(input("  Note ID to edit: ").strip())
            except ValueError:
                print("  ! Enter a valid number.")
                continue
            note = manager.get(nid)
            if note is None:
                print("  ! Note not found.")
                continue
            _print_note(note)
            new_title = input("  New title (Enter to keep): ").strip()
            new_content = input("  New content (Enter to keep): ").strip()
            manager.edit(nid, new_title or None, new_content or None)
            print("  ✓ Note updated.")

        elif choice == "5":
            try:
                nid = int(input("  Note ID to delete: ").strip())
            except ValueError:
                print("  ! Enter a valid number.")
                continue
            if manager.delete(nid):
                print("  ✓ Note deleted.")
            else:
                print("  ! Note not found.")

        elif choice == "6":
            break
        else:
            print("  ! Invalid choice.")
