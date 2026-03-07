"""Personal Productivity Suite — main entry point."""

from modules.calculator import Calculator
from modules.notes_manager import NotesManager
import modules.calculator as calc_module
import modules.notes_manager as notes_module
import modules.timer as timer_module


BANNER = """
  ╔══════════════════════════════════════╗
  ║    PERSONAL PRODUCTIVITY SUITE       ║
  ╚══════════════════════════════════════╝
"""

MENU = """
  MAIN MENU
  -----------------------------------------
  1. Calculator
  2. Notes Manager
  3. Timer & Stopwatch
  4. Exit
  -----------------------------------------"""


def main():
    print(BANNER)
    calc = Calculator()
    notes = NotesManager()

    while True:
        print(MENU)
        choice = input("  Choice: ").strip()

        if choice == "1":
            calc_module.run(calc)
        elif choice == "2":
            notes_module.run(notes)
        elif choice == "3":
            timer_module.run()
        elif choice == "4":
            print("\n  Goodbye!\n")
            break
        else:
            print("  ! Enter a number between 1 and 4.")


if __name__ == "__main__":
    main()
