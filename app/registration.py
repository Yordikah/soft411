"""Business logic for the course registration feature.

Kept separate from the Flask layer so it can be unit tested directly.
"""

MIN_CREDITS = 1
MAX_CREDITS = 21

# Registration period states: NOT_OPEN -> OPEN -> CLOSED
VALID_PERIOD_STATES = ("NOT_OPEN", "OPEN", "CLOSED")


class RegistrationError(Exception):
    """Raised when a registration rule is broken."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


class RegistrationSystem:
    def __init__(self):
        self.period = "NOT_OPEN"
        self.courses = {}    # code -> {title, credits, capacity, prereq, enrolled:set}
        self.students = {}   # id -> {name, passed:set, registered:set}

    # ---- setup helpers -------------------------------------------------
    def add_course(self, code, title, credits, capacity, prereq=None):
        self.courses[code] = {
            "code": code,
            "title": title,
            "credits": credits,
            "capacity": capacity,
            "prereq": prereq,
            "enrolled": set(),
        }

    def add_student(self, student_id, name, passed=None):
        self.students[student_id] = {
            "id": student_id,
            "name": name,
            "passed": set(passed or []),
            "registered": set(),
        }

    # ---- registration period (state machine) ---------------------------
    def open_registration(self):
        if self.period != "NOT_OPEN":
            raise RegistrationError("BAD_TRANSITION", f"Cannot open from {self.period}")
        self.period = "OPEN"

    def close_registration(self):
        if self.period != "OPEN":
            raise RegistrationError("BAD_TRANSITION", f"Cannot close from {self.period}")
        self.period = "CLOSED"

    # ---- queries -------------------------------------------------------
    def total_credits(self, student_id):
        student = self._get_student(student_id)
        return sum(self.courses[c]["credits"] for c in student["registered"])

    def schedule(self, student_id):
        student = self._get_student(student_id)
        return {
            "student_id": student_id,
            "courses": sorted(student["registered"]),
            "total_credits": self.total_credits(student_id),
        }

    # ---- commands ------------------------------------------------------
    def register(self, student_id, course_code):
        if self.period != "OPEN":
            raise RegistrationError("PERIOD_CLOSED", "Registration period is not open")
        student = self._get_student(student_id)
        course = self._get_course(course_code)

        if course_code in student["registered"]:
            raise RegistrationError("DUPLICATE", "Already registered for this course")
        if course["prereq"] and course["prereq"] not in student["passed"]:
            raise RegistrationError(
                "PREREQ_MISSING", f"Prerequisite {course['prereq']} not passed"
            )
        if len(course["enrolled"]) >= course["capacity"]:
            raise RegistrationError("COURSE_FULL", "Course is full")
        new_total = self.total_credits(student_id) + course["credits"]
        if new_total > MAX_CREDITS:
            raise RegistrationError(
                "CREDIT_LIMIT", f"Credit limit exceeded ({new_total} > {MAX_CREDITS})"
            )

        student["registered"].add(course_code)
        course["enrolled"].add(student_id)
        return self.schedule(student_id)

    def drop(self, student_id, course_code):
        if self.period != "OPEN":
            raise RegistrationError("PERIOD_CLOSED", "Registration period is not open")
        student = self._get_student(student_id)
        self._get_course(course_code)
        if course_code not in student["registered"]:
            raise RegistrationError("NOT_REGISTERED", "Student is not registered for this course")
        if self.total_credits(student_id) - self.courses[course_code]["credits"] < MIN_CREDITS:
            raise RegistrationError(
                "MIN_CREDITS", f"Must keep at least {MIN_CREDITS} credit (contact advisor)"
            )
        student["registered"].remove(course_code)
        self.courses[course_code]["enrolled"].remove(student_id)
        return self.schedule(student_id)

    # ---- internal ------------------------------------------------------
    def _get_student(self, student_id):
        if student_id not in self.students:
            raise RegistrationError("UNKNOWN_STUDENT", "Student not found")
        return self.students[student_id]

    def _get_course(self, course_code):
        if course_code not in self.courses:
            raise RegistrationError("UNKNOWN_COURSE", "Course not found")
        return self.courses[course_code]


def seed_demo_data(system):
    """Demo data used by the API and the tests."""
    system.add_course("SOFT211", "Software Engineering I", 6, 40)
    system.add_course("SOFT411", "Software Validation & Testing", 6, 2, prereq="SOFT211")
    system.add_course("MATH101", "Calculus I", 5, 50)
    system.add_course("ENG102", "Academic English", 3, 30)
    system.add_course("CS301", "Databases", 6, 35)
    system.add_course("HIST100", "World History", 2, 60)
    system.add_course("PE100", "Physical Education", 1, 100)
    system.add_student("S1001", "Yordanos", passed=["SOFT211"])
    system.add_student("S1002", "Ali", passed=[])
    system.add_student("S1003", "Maria", passed=["SOFT211"])
    system.add_student("S1004", "John", passed=["SOFT211"])
    return system
