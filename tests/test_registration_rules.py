"""Unit tests for the registration business rules (component level, black-box design).

Test case IDs (TCxx) match the test design table in the report.
"""
import unittest

from app.registration import RegistrationError, RegistrationSystem, seed_demo_data


def fresh_system(open_period=True):
    system = seed_demo_data(RegistrationSystem())
    if open_period:
        system.open_registration()
    return system


class CreditLimitTests(unittest.TestCase):
    """Boundary value analysis on the 1..21 credit range."""

    def setUp(self):
        self.s = fresh_system()
        # 6 + 5 + 3 + 6 = 20 credits
        for code in ("SOFT211", "MATH101", "ENG102", "CS301"):
            self.s.register("S1002", code)

    def test_TC01_twenty_credits_is_accepted(self):
        self.assertEqual(self.s.total_credits("S1002"), 20)

    def test_TC02_exactly_21_credits_is_accepted(self):
        result = self.s.register("S1002", "PE100")  # +1
        self.assertEqual(result["total_credits"], 21)

    def test_TC03_22_credits_is_rejected(self):
        with self.assertRaises(RegistrationError) as ctx:
            self.s.register("S1002", "HIST100")  # +2 -> 22
        self.assertEqual(ctx.exception.code, "CREDIT_LIMIT")
        self.assertEqual(self.s.total_credits("S1002"), 20)  # nothing changed

    def test_TC04_dropping_last_course_below_1_credit_is_rejected(self):
        s = fresh_system()
        s.register("S1002", "PE100")  # 1 credit only
        with self.assertRaises(RegistrationError) as ctx:
            s.drop("S1002", "PE100")
        self.assertEqual(ctx.exception.code, "MIN_CREDITS")

    def test_TC19_dropping_down_to_exactly_1_credit_is_allowed(self):
        # Added after mutation testing: changing "<" to "<=" in drop() survived
        # every other test, so the lower boundary itself was never checked.
        s = fresh_system()
        s.register("S1002", "PE100")    # 1 credit
        s.register("S1002", "HIST100")  # 2 credits -> total 3
        result = s.drop("S1002", "HIST100")
        self.assertEqual(result["total_credits"], 1)


class CapacityTests(unittest.TestCase):
    """BVA on course capacity. SOFT411 has capacity = 2."""

    def test_TC05_last_seat_can_be_taken_and_next_student_is_rejected(self):
        s = fresh_system()
        s.register("S1001", "SOFT411")             # seat 1
        s.register("S1003", "SOFT411")             # seat 2 = capacity (boundary)
        with self.assertRaises(RegistrationError) as ctx:
            s.register("S1004", "SOFT411")         # capacity + 1
        self.assertEqual(ctx.exception.code, "COURSE_FULL")
        self.assertEqual(len(s.courses["SOFT411"]["enrolled"]), 2)

    def test_TC06_seat_is_freed_after_drop(self):
        s = fresh_system()
        s.register("S1001", "MATH101")             # keep min credits
        s.register("S1001", "SOFT411")
        s.register("S1003", "SOFT411")
        s.drop("S1001", "SOFT411")
        s.register("S1004", "SOFT411")             # should now succeed
        self.assertIn("S1004", s.courses["SOFT411"]["enrolled"])


class DecisionTableTests(unittest.TestCase):
    """Decision table: prerequisite passed? x seat available? x already registered?"""

    def test_TC07_prerequisite_missing_is_rejected(self):
        s = fresh_system()
        with self.assertRaises(RegistrationError) as ctx:
            s.register("S1002", "SOFT411")         # Ali has not passed SOFT211
        self.assertEqual(ctx.exception.code, "PREREQ_MISSING")

    def test_TC08_all_conditions_true_registration_succeeds(self):
        s = fresh_system()
        result = s.register("S1001", "SOFT411")
        self.assertEqual(result["courses"], ["SOFT411"])
        self.assertEqual(result["total_credits"], 6)

    def test_TC09_duplicate_registration_is_rejected(self):
        s = fresh_system()
        s.register("S1001", "CS301")
        with self.assertRaises(RegistrationError) as ctx:
            s.register("S1001", "CS301")
        self.assertEqual(ctx.exception.code, "DUPLICATE")
        self.assertEqual(s.total_credits("S1001"), 6)  # not counted twice


class RegistrationPeriodStateTests(unittest.TestCase):
    """State transition testing: NOT_OPEN -> OPEN -> CLOSED."""

    def test_TC10_register_before_period_opens_is_rejected(self):
        s = fresh_system(open_period=False)
        with self.assertRaises(RegistrationError) as ctx:
            s.register("S1001", "CS301")
        self.assertEqual(ctx.exception.code, "PERIOD_CLOSED")

    def test_TC11_register_after_period_closes_is_rejected(self):
        s = fresh_system()
        s.close_registration()
        with self.assertRaises(RegistrationError) as ctx:
            s.register("S1001", "CS301")
        self.assertEqual(ctx.exception.code, "PERIOD_CLOSED")

    def test_TC12_invalid_transitions_are_rejected(self):
        s = fresh_system(open_period=False)
        with self.assertRaises(RegistrationError):
            s.close_registration()                 # NOT_OPEN -> CLOSED not allowed
        s.open_registration()
        s.close_registration()
        with self.assertRaises(RegistrationError):
            s.open_registration()                  # CLOSED -> OPEN not allowed
        self.assertEqual(s.period, "CLOSED")


if __name__ == "__main__":
    unittest.main()
