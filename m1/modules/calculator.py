"""Calculator module — basic arithmetic with session history."""

HISTORY_LIMIT = 20


class Calculator:
    def __init__(self):
        self.history = []

    # ── core operations ──────────────────────────────────────────────────────

    def calculate(self, a, op, b):
        """Perform a single operation and return the result."""
        if op == "+":
            result = a + b
        elif op == "-":
            result = a - b
        elif op == "*":
            result = a * b
        elif op == "/":
            if b == 0:
                raise ZeroDivisionError("Cannot divide by zero.")
            result = a / b
        else:
            raise ValueError(f"Unknown operator: {op}")

        entry = f"{a} {op} {b} = {result}"
        self.history.append(entry)
        if len(self.history) > HISTORY_LIMIT:
            self.history.pop(0)
        return result

    # ── display helpers ───────────────────────────────────────────────────────

    def show_history(self):
        if not self.history:
            print("  No calculations yet.")
        else:
            for i, entry in enumerate(self.history, 1):
                print(f"  {i:>2}. {entry}")


# ── interactive session ───────────────────────────────────────────────────────

def run(calc: Calculator):
    """Interactive calculator loop."""
    print("\n  CALCULATOR")
    print("  " + "-" * 36)
    print("  Operators: +  -  *  /")
    print("  Type 'h' for history, 'b' to go back.\n")

    while True:
        raw = input("  Expression (e.g. 12 * 3): ").strip()

        if raw.lower() == "b":
            break
        if raw.lower() == "h":
            calc.show_history()
            continue
        if not raw:
            continue

        # parse "a op b"
        parts = raw.split()
        if len(parts) != 3:
            print("  ! Enter expression as:  <number> <operator> <number>")
            continue

        try:
            a = float(parts[0])
            op = parts[1]
            b = float(parts[2])
        except ValueError:
            print("  ! Invalid number. Try again.")
            continue

        try:
            result = calc.calculate(a, op, b)
            # show as int when result is a whole number
            display = int(result) if result.is_integer() else result
            print(f"  = {display}\n")
        except (ZeroDivisionError, ValueError) as e:
            print(f"  ! {e}\n")
