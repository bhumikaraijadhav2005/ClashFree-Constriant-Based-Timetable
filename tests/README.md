# Tests

Run automated tests from the project root with `pytest -q`.

`manual/enterprise_scenarios.py` is an older end-to-end acceptance flow. It imports, generates, restores, and writes timetable state, so run it only with a disposable local store and valid synthetic data. Pytest does not collect this manual script.
