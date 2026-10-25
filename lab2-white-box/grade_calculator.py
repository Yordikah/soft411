def calculate_grade(mark, attendance):

    if mark < 0 or mark > 100:
        return "Invalid mark"

    if attendance < 0 or attendance > 100:
        return "Invalid attendance"

    if attendance < 75:
        return "Fail - Low Attendance"

    if mark >= 70:
        return "A"

    elif mark >= 60:
        return "B"

    elif mark >= 50:
        return "C"

    elif mark >= 40:
        return "D"

    else:
        return "F"
