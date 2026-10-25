# Course Registration API – SOFT411 Testing Assignment

Small Flask REST API for a campus portal registration feature, used as the
system under test for the *Modern Testing Strategy & Prototype* assignment.

## Rules implemented
- 1–21 credits per semester
- course capacity (no overbooking)
- prerequisites (e.g. SOFT411 needs SOFT211)
- no duplicate registration
- registration period state: NOT_OPEN → OPEN → CLOSED

## Endpoints
| Method | Path | Description |
|---|---|---|
| GET | `/health` | health check |
| GET | `/courses` | list courses with seats left |
| GET | `/students/<id>/schedule` | student schedule + total credits |
| POST | `/register` | body `{"student_id": "S1001", "course_code": "SOFT411"}` |
| POST | `/drop` | same body as register |

## Running
```bash
pip install -r requirements.txt
python -m app.api                 # starts on http://127.0.0.1:5000
python -m pytest tests -v         # 19 automated tests (unittest also works:
                                  # python -m unittest discover -s tests -v)
python -m tests.perf_smoke        # performance smoke test
bandit -r app -ll                 # static security scan
```

## Structure
```
app/registration.py   business rules
app/api.py            Flask API + input validation
tests/test_registration_rules.py   TC01–TC12, TC19 (unit / component)
tests/test_api.py                  TC13–TC18 (API + security)
tests/perf_smoke.py                performance smoke check
.github/workflows/tests.yml        CI pipeline
reports/                           saved test output
```
