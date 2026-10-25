"""Flask REST API for the course registration feature."""
import re

from flask import Flask, jsonify, request

from app.registration import RegistrationError, RegistrationSystem, seed_demo_data

STUDENT_ID_PATTERN = re.compile(r"^S\d{4}$")
COURSE_CODE_PATTERN = re.compile(r"^[A-Z]{2,5}\d{3}$")

STATUS_FOR_CODE = {
    "UNKNOWN_STUDENT": 404,
    "UNKNOWN_COURSE": 404,
    "DUPLICATE": 409,
    "COURSE_FULL": 409,
    "PREREQ_MISSING": 422,
    "CREDIT_LIMIT": 422,
    "MIN_CREDITS": 422,
    "NOT_REGISTERED": 409,
    "PERIOD_CLOSED": 403,
}


def create_app(system=None):
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 2 * 1024  # 2 KB is plenty for our JSON bodies
    if system is None:
        system = seed_demo_data(RegistrationSystem())
        system.open_registration()
    app.config["SYSTEM"] = system

    def error(code, message, status):
        return jsonify({"error": code, "message": message}), status

    def read_body():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return None, error("BAD_REQUEST", "JSON body required", 400)
        student_id = data.get("student_id")
        course_code = data.get("course_code")
        if not isinstance(student_id, str) or not STUDENT_ID_PATTERN.match(student_id):
            return None, error("BAD_REQUEST", "Invalid student_id", 400)
        if not isinstance(course_code, str) or not COURSE_CODE_PATTERN.match(course_code):
            return None, error("BAD_REQUEST", "Invalid course_code", 400)
        return (student_id, course_code), None

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/courses")
    def list_courses():
        out = []
        for c in system.courses.values():
            out.append({
                "code": c["code"],
                "title": c["title"],
                "credits": c["credits"],
                "capacity": c["capacity"],
                "seats_left": c["capacity"] - len(c["enrolled"]),
                "prereq": c["prereq"],
            })
        return jsonify(out)

    @app.get("/students/<student_id>/schedule")
    def get_schedule(student_id):
        try:
            return jsonify(system.schedule(student_id))
        except RegistrationError as e:
            return error(e.code, e.message, STATUS_FOR_CODE.get(e.code, 400))

    @app.post("/register")
    def register():
        parsed, err = read_body()
        if err:
            return err
        try:
            return jsonify(system.register(*parsed)), 201
        except RegistrationError as e:
            return error(e.code, e.message, STATUS_FOR_CODE.get(e.code, 400))

    @app.post("/drop")
    def drop():
        parsed, err = read_body()
        if err:
            return err
        try:
            return jsonify(system.drop(*parsed)), 200
        except RegistrationError as e:
            return error(e.code, e.message, STATUS_FOR_CODE.get(e.code, 400))

    @app.errorhandler(413)
    def too_large(_e):
        return error("PAYLOAD_TOO_LARGE", "Request body too large", 413)

    @app.errorhandler(404)
    def not_found(_e):
        return error("NOT_FOUND", "Endpoint not found", 404)

    return app


if __name__ == "__main__":
    # debug is off on purpose (bandit B201)
    create_app().run(host="127.0.0.1", port=5000, debug=False)
