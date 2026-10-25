"""Lab Task 4 - execute every designed test case and record Expected vs Actual."""
from grade_calculator import calculate_grade

# (id, mark, attendance, expected, reason)
TEST_CASES = [
    ("TC01", -1, 80, "Invalid mark", "Invalid lower boundary"),
    ("TC02", 101, 80, "Invalid mark", "Invalid upper boundary"),
    ("TC03", 60, -1, "Invalid attendance", "Invalid attendance (lower)"),
    ("TC04", 60, 101, "Invalid attendance", "Invalid attendance (upper)"),
    ("TC05", 80, 70, "Fail - Low Attendance", "Attendance branch"),
    ("TC06", 75, 80, "A", "Grade A"),
    ("TC07", 65, 80, "B", "Grade B"),
    ("TC08", 55, 80, "C", "Grade C"),
    ("TC09", 45, 80, "D", "Grade D"),
    ("TC10", 35, 80, "F", "Grade F"),
    # boundary values
    ("TC11", 0, 80, "F", "Lowest valid mark"),
    ("TC12", 100, 80, "A", "Highest valid mark"),
    ("TC13", 39, 80, "F", "D/F boundary (below)"),
    ("TC14", 40, 80, "D", "D/F boundary (on)"),
    ("TC15", 49, 80, "D", "C/D boundary (below)"),
    ("TC16", 50, 80, "C", "C/D boundary (on)"),
    ("TC17", 59, 80, "C", "B/C boundary (below)"),
    ("TC18", 60, 80, "B", "B/C boundary (on)"),
    ("TC19", 69, 80, "B", "A/B boundary (below)"),
    ("TC20", 70, 80, "A", "A/B boundary (on)"),
    ("TC21", 80, 74, "Fail - Low Attendance", "Attendance boundary (below)"),
    ("TC22", 80, 75, "A", "Attendance boundary (on)"),
    ("TC23", 80, 100, "A", "Highest valid attendance"),
    ("TC24", 80, 0, "Fail - Low Attendance", "Lowest valid attendance"),
    ("TC25", -1, -1, "Invalid mark", "Both invalid - mark is checked first"),
    ("TC26", 69.5, 80, "B", "Decimal mark just under 70"),
]

if __name__ == "__main__":
    passed = 0
    print(f"{'ID':<5} {'Mark':>5} {'Att':>5}  {'Expected':<22} {'Actual':<22} Result")
    print("-" * 75)
    for tid, mark, att, expected, _reason in TEST_CASES:
        actual = calculate_grade(mark, att)
        ok = actual == expected
        passed += ok
        print(f"{tid:<5} {mark:>5} {att:>5}  {expected:<22} {actual:<22} {'PASS' if ok else 'FAIL'}")
    print("-" * 75)
    print(f"{passed}/{len(TEST_CASES)} passed")
