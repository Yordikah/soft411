"""Lab Task 6 - automated tests (pytest)."""
import pytest

from grade_calculator import calculate_grade


# ---- the four tests given in the lab sheet ----
def test_grade_a():
    assert calculate_grade(75, 80) == "A"


def test_grade_b():
    assert calculate_grade(65, 80) == "B"


def test_low_attendance():
    assert calculate_grade(80, 70) == "Fail - Low Attendance"


def test_invalid_mark():
    assert calculate_grade(101, 80) == "Invalid mark"


# ---- my extra tests: remaining branches + boundary values ----
def test_invalid_attendance():
    assert calculate_grade(60, -1) == "Invalid attendance"
    assert calculate_grade(60, 101) == "Invalid attendance"


@pytest.mark.parametrize(
    "mark, expected",
    [
        (39, "F"), (40, "D"),
        (49, "D"), (50, "C"),
        (59, "C"), (60, "B"),
        (69, "B"), (70, "A"),
        (0, "F"), (100, "A"),
    ],
)
def test_grade_boundaries(mark, expected):
    assert calculate_grade(mark, 80) == expected


@pytest.mark.parametrize("attendance, expected", [(74, "Fail - Low Attendance"), (75, "A")])
def test_attendance_boundary(attendance, expected):
    assert calculate_grade(80, attendance) == expected
