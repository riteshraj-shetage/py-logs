# User Guide — Personal Productivity Suite (Basic)

A CLI tool with three modules: **Calculator**, **Notes Manager**, and **Timer & Stopwatch**.

---

## Starting the app

```bash
python main.py
```

You will see the main menu. Type the number for the tool you want and press Enter.

---

## 1. Calculator

Enter any arithmetic expression in the form:

```
<number> <operator> <number>
```

Supported operators: `+` `-` `*` `/`

| Command  | What it does                     |
| -------- | -------------------------------- |
| `12 * 3` | Calculates and prints the result |
| `h`      | Shows the last 20 calculations   |
| `b`      | Returns to main menu             |

Division by zero is handled — you will see an error message instead of a crash.

---

## 2. Notes Manager

| Menu option       | What it does                                    |
| ----------------- | ----------------------------------------------- |
| 1. View all notes | Lists every saved note with ID, title, and date |
| 2. Add note       | Prompts for a title and content, then saves     |
| 3. Search notes   | Searches titles and content for a keyword       |
| 4. Edit note      | Updates title and/or content by note ID         |
| 5. Delete note    | Removes a note by ID permanently                |
| 6. Back           | Returns to main menu                            |

Notes are saved to `data/notes.json` automatically after every change.

---

## 3. Timer & Stopwatch

### Countdown timer

Enter a duration in any of these formats:

| Input     | Means               |
| --------- | ------------------- |
| `90`      | 90 seconds          |
| `1:30`    | 1 minute 30 seconds |
| `0:01:30` | 1 minute 30 seconds |

The timer counts down on screen. Press `Ctrl+C` to cancel early.

### Stopwatch

| Command | What it does                                 |
| ------- | -------------------------------------------- |
| `start` | Begins the stopwatch                         |
| `stop`  | Pauses and shows elapsed time                |
| `lap`   | Records a lap time (stopwatch keeps running) |
| `reset` | Clears all times                             |
| `back`  | Returns to Timer menu (shows lap summary)    |

---

## Data storage

Notes are stored in `data/notes.json` inside the project folder. No other external files are created.

---

## Troubleshooting

| Problem                        | Fix                                                                                |
| ------------------------------ | ---------------------------------------------------------------------------------- |
| `ModuleNotFoundError`          | Make sure you run `python main.py` from inside `complete-tasks/m1/`                |
| Notes not saving               | Check that the `data/` folder exists (it is created automatically on first use)    |
| Timer shows garbage characters | Your terminal may not support Unicode — the symbols `⏳ ✓ ▶ ■` are decorative only |
