# Personal Productivity Suite — Basic Version (m1)

A simple, menu-driven CLI app built with Python's standard library.  
Covers three tools: **Calculator**, **Notes Manager**, and **Timer & Stopwatch**.

---

## Project structure

```
main.py               entry point — run this to start the app
requirements.txt      no external dependencies
modules/
    calculator.py     arithmetic with session history
    notes_manager.py  add / view / search / edit / delete notes
    timer.py          countdown timer and stopwatch
data/
    notes.json        auto-created on first note save
docs/
    user_guide.md     full usage reference
```

---

## Setup & run

Python 3.8+ required. No packages to install.

```bash
python main.py
```

---

## Features

### Calculator

- Four basic operators: `+  -  *  /`
- Keeps a session history of the last 20 calculations (type `h`)
- Graceful error for division by zero

### Notes Manager

- Add notes with a title and free-text content
- View, search (by keyword), edit, and delete
- Notes persist between sessions in `data/notes.json`

### Timer & Stopwatch

- **Countdown timer** — accepts seconds or `MM:SS` / `HH:MM:SS`
- **Stopwatch** — start, stop, lap, reset with a lap summary at the end

---

## Usage example

```
  MAIN MENU
  1. Calculator
  2. Notes Manager
  3. Timer & Stopwatch
  4. Exit

  Choice: 1

  CALCULATOR
  Operators: +  -  *  /
  Expression (e.g. 12 * 3): 25 / 4
  = 6.25
```

See `docs/user_guide.md` for the full reference.
