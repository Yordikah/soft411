# SFWE411 – Lab 2: White-Box Testing (Student Grade Calculator)

| File | What it is |
|---|---|
| `grade_calculator.py` | System under test (copied exactly from the lab sheet) |
| `run_manual_tests.py` | Lab Task 4 – runs all 26 designed test cases and prints Expected vs Actual |
| `test_grade_calculator.py` | Lab Task 6 – 17 automated pytest tests (4 from the sheet + boundaries) |
| `manual_results.txt` | Output of the manual test run (26/26 passed) |
| `pytest_results.txt` | Output of `pytest -v` (17 passed) |
| `exploratory_results.txt` | Extra "weird input" tests that found BUG-001 and BUG-002 |

## Run it
```bash
cd lab2-white-box
python run_manual_tests.py
python -m pytest -v
```

## Defects found
- **BUG-001 (High):** `calculate_grade(75, float("nan"))` returns `"A"` instead of `"Invalid attendance"`.
- **BUG-002 (Medium):** `calculate_grade("75", 80)` crashes with `TypeError`.
