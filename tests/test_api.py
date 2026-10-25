"""API (service-level) tests using Flask's test client.

Includes input-validation equivalence partitions and basic security checks.
"""
import json
import unittest

from app.api import create_app


class ApiTestBase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def post(self, path, body):
        return self.client.post(path, data=json.dumps(body), content_type="application/json")


class FunctionalApiTests(ApiTestBase):
    def test_TC13_register_via_api_returns_201_and_updates_schedule(self):
        r = self.post("/register", {"student_id": "S1001", "course_code": "SOFT411"})
        self.assertEqual(r.status_code, 201)
        sched = self.client.get("/students/S1001/schedule").get_json()
        self.assertEqual(sched["courses"], ["SOFT411"])
        seats = {c["code"]: c["seats_left"] for c in self.client.get("/courses").get_json()}
        self.assertEqual(seats["SOFT411"], 1)

    def test_TC14_unknown_course_and_student_return_404(self):
        r1 = self.post("/register", {"student_id": "S1001", "course_code": "XYZ999"})
        r2 = self.client.get("/students/S9999/schedule")
        self.assertEqual(r1.status_code, 404)
        self.assertEqual(r1.get_json()["error"], "UNKNOWN_COURSE")
        self.assertEqual(r2.status_code, 404)

    def test_TC15_invalid_input_partitions_return_400(self):
        invalid_bodies = [
            {},                                             # missing fields
            {"student_id": "1001", "course_code": "CS301"},  # wrong id format
            {"student_id": "S1001", "course_code": "cs301"}, # lowercase code
            {"student_id": "S1001"},                         # missing course
            {"student_id": 1001, "course_code": "CS301"},    # wrong type
        ]
        for body in invalid_bodies:
            with self.subTest(body=body):
                r = self.post("/register", body)
                self.assertEqual(r.status_code, 400)
        r = self.client.post("/register", data="not json", content_type="application/json")
        self.assertEqual(r.status_code, 400)


class SecurityApiTests(ApiTestBase):
    """Basic security checks (OWASP WSTG input validation ideas)."""

    def test_TC16_injection_style_input_is_rejected(self):
        attacks = [
            "S1001' OR '1'='1",
            "S1001; DROP TABLE students",
            "<script>alert(1)</script>",
            "../../etc/passwd",
        ]
        for value in attacks:
            with self.subTest(value=value):
                r = self.post("/register", {"student_id": value, "course_code": "CS301"})
                self.assertEqual(r.status_code, 400)
                self.assertNotIn("<script>", r.get_data(as_text=True))

    def test_TC17_oversized_payload_is_rejected_with_413(self):
        big = {"student_id": "S1001", "course_code": "CS301", "junk": "A" * 10_000}
        r = self.post("/register", big)
        self.assertEqual(r.status_code, 413)

    def test_TC18_errors_do_not_leak_stack_traces(self):
        r = self.client.get("/does-not-exist")
        body = r.get_data(as_text=True)
        self.assertEqual(r.status_code, 404)
        self.assertNotIn("Traceback", body)
        self.assertEqual(r.get_json()["error"], "NOT_FOUND")


if __name__ == "__main__":
    unittest.main()
