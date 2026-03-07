"""Timer module — countdown timer and stopwatch."""

import time
import threading


# ── countdown timer ───────────────────────────────────────────────────────────

def _parse_duration(raw):
    """
    Accept plain seconds or HH:MM:SS / MM:SS / SS.
    Returns total seconds as int, or None on parse failure.
    """
    raw = raw.strip()
    parts = raw.split(":")
    try:
        if len(parts) == 1:
            return int(parts[0])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except ValueError:
        pass
    return None


def _fmt(seconds):
    """Format seconds as HH:MM:SS."""
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h:02}:{m:02}:{s:02}"


def _countdown(total):
    """Run countdown in current thread, printing each tick."""
    print()
    try:
        for remaining in range(total, 0, -1):
            print(f"\r  ⏳ {_fmt(remaining)} remaining ", end="", flush=True)
            time.sleep(1)
        print("\r  ✓ Time's up!                    ")
    except KeyboardInterrupt:
        print("\n  ! Timer interrupted.")


# ── stopwatch ─────────────────────────────────────────────────────────────────

class Stopwatch:
    def __init__(self):
        self._start = None
        self._running = False
        self._elapsed = 0.0
        self._laps = []

    def start(self):
        if not self._running:
            self._start = time.time()
            self._running = True

    def stop(self):
        if self._running:
            self._elapsed += time.time() - self._start
            self._running = False

    def lap(self):
        if self._running:
            total = self._elapsed + (time.time() - self._start)
            self._laps.append(total)
            return total
        return None

    def reset(self):
        self._start = None
        self._running = False
        self._elapsed = 0.0
        self._laps = []

    def is_running(self):
        return self._running

    def elapsed(self):
        if self._running:
            return self._elapsed + (time.time() - self._start)
        return self._elapsed

    def laps(self):
        return list(self._laps)


def _run_stopwatch():
    """Interactive stopwatch session."""
    sw = Stopwatch()
    print("\n  STOPWATCH")
    print("  Commands: start  stop  lap  reset  back")

    while True:
        cmd = input("  > ").strip().lower()
        if cmd == "start":
            if not sw.is_running():
                sw.start()
                print("  ▶ Started.")
            else:
                print("  Already running.")
        elif cmd == "stop":
            sw.stop()
            print(f"  ■ Stopped at {_fmt(sw.elapsed())}.")
        elif cmd == "lap":
            t = sw.lap()
            if t is None:
                print("  ! Start the stopwatch first.")
            else:
                print(f"  🏁 Lap {len(sw.laps())}: {_fmt(t)}")
        elif cmd == "reset":
            sw.reset()
            print("  ↺ Reset.")
        elif cmd in ("back", "b"):
            break
        else:
            print("  ! Unknown command.")

    if sw.laps():
        print("\n  Lap summary:")
        for i, t in enumerate(sw.laps(), 1):
            print(f"    Lap {i}: {_fmt(t)}")
    print()


# ── interactive session ───────────────────────────────────────────────────────

def run():
    """Interactive timer/stopwatch loop."""
    while True:
        print("\n  TIMER & STOPWATCH")
        print("  " + "-" * 36)
        print("  1. Countdown timer")
        print("  2. Stopwatch")
        print("  3. Back to main menu")
        choice = input("\n  Choice: ").strip()

        if choice == "1":
            raw = input("  Duration (e.g. 90  or  1:30  or  0:01:30): ").strip()
            total = _parse_duration(raw)
            if total is None or total <= 0:
                print("  ! Enter a positive duration.")
                continue
            _countdown(total)

        elif choice == "2":
            _run_stopwatch()

        elif choice == "3":
            break
        else:
            print("  ! Invalid choice.")
