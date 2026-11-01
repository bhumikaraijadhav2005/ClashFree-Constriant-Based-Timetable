"""Focused regression tests for scope propagation and scheduler constraint selection."""

import sys
import io
from pathlib import Path

import pytest
import openpyxl

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

import app
import db
import excel_reader
import scheduler


def test_mrv_counts_domains_with_the_assignment_validator(monkeypatch):
    sessions = [
        {"id": "wide", "is_lab": False},
        {"id": "narrow", "is_lab": False},
    ]
    domains = {
        "wide": [("valid-1", {}, {}), ("valid-3", {}, {}), ("invalid", {}, {})],
        "narrow": [("valid-2", {}, {})],
    }
    checked = []

    def validity(session, slot, room, faculty, assignment):
        checked.append((session["id"], slot))
        return slot != "invalid", None

    monkeypatch.setattr(scheduler, "_is_valid", validity)
    selected, remaining = scheduler._pick_next_session(sessions, {}, domains)

    assert selected["id"] == "narrow"
    assert remaining == 1
    assert len(checked) == 4


def test_generated_sessions_keep_academic_scope():
    requirement = {
        "year": "Third Year",
        "semester": "Semester V",
        "academic_year": "2026-2027",
        "division": "C",
        "subject": "Networks",
        "subject_code": "NET301",
        "type": "Lecture",
        "sessions_week": 1,
    }

    sessions = scheduler._build_sessions([], [], [], "ECE", [requirement])

    assert len(sessions) == 1
    assert sessions[0]["year"] == "Third Year"
    assert sessions[0]["semester"] == "Semester V"
    assert sessions[0]["academic_year"] == "2026-2027"
    assert sessions[0]["department"] == "ECE"


def test_scheduler_generates_for_non_cse_context():
    success, message, rows, conflicts, _ = scheduler.generate_timetable(
        faculty_list=[{
            "name": "Electronics Faculty",
            "code": "FAC-E",
            "department": "ECE",
            "subjects": ["Signals"],
            "available_from": "09:00",
            "available_to": "12:00",
        }],
        room_list=[{
            "name": "ECE-CR-1",
            "type": "Classroom",
            "capacity": 60,
            "department": "ECE",
            "is_active": True,
        }],
        subject_list=[],
        division_list=[],
        batch_list=[],
        time_slots=[{
            "period": "9:00 AM - 10:00 AM",
            "type": "TEACHING",
            "is_teaching": True,
            "is_morning": True,
        }],
        department="ECE",
        days=["Monday"],
        requirements=[{
            "department": "ECE",
            "year": "Second Year",
            "semester": "Semester III",
            "academic_year": "2026-2027",
            "division": "A",
            "subject": "Signals",
            "subject_code": "SIG201",
            "type": "Lecture",
            "sessions_week": 1,
            "duration": "1 hr",
            "strength": 40,
            "capacity_required": 40,
            "faculty_name": "Electronics Faculty",
            "faculty_code": "FAC-E",
        }],
    )

    assert success, f"{message}: {conflicts}"
    assert len(rows) == 1
    assert rows[0]["department"] == "ECE"
    assert rows[0]["faculty_code"] == "FAC-E"
    assert rows[0]["room"] == "ECE-CR-1"


def test_timetable_api_filters_year_and_semester_using_normalized_values(monkeypatch):
    rows = [
        {"department": "ECE", "year": "Year 2", "semester": "Semester III", "section": "A"},
        {"department": "ECE", "year": "Third Year", "semester": "Semester V", "section": "A"},
    ]
    monkeypatch.setattr(db, "get_timetable", lambda **kwargs: rows)

    response = app.app.test_client().get(
        "/api/timetable?department=ECE&year=Second%20Year&semester=Semester%20III"
    )

    assert response.status_code == 200
    assert response.get_json() == [rows[0]]


def test_academic_filter_endpoints_return_only_configured_values(monkeypatch):
    monkeypatch.setattr(db, "get_all_divisions", lambda department: [
        {"department_code": department, "year": "Year 5"},
        {"department_code": department, "year": "Year 2"},
    ])
    monkeypatch.setattr(db, "get_all_subjects", lambda department: [
        {"year": "Year 2", "semester": "Semester IX"},
        {"year": "Year 2", "semester": "Semester IV"},
    ])

    client = app.app.test_client()
    assert client.get("/api/academic-years?department=ECE").get_json() == ["Year 2", "Year 5"]
    assert client.get("/api/semesters?department=ECE&year=Year%202").get_json() == ["Semester IV", "Semester IX"]


def test_batches_are_scoped_by_department_even_when_division_names_repeat(monkeypatch):
    monkeypatch.setattr(db, "get_client", lambda: None)
    monkeypatch.setattr(db, "_memory_store", {
        "divisions": [
            {"name": "A", "department_code": "CSE"},
            {"name": "A", "department_code": "ECE"},
        ],
        "batches": [
            {"division_name": "A", "department_code": "CSE", "name": "A1"},
            {"division_name": "A", "department_code": "ECE", "name": "A1"},
            {"division_name": "A", "name": "A2"},
        ],
    })

    assert [b["department_code"] for b in db.get_all_batches(department_code="CSE")] == ["CSE"]
    assert [b["department_code"] for b in db.get_all_batches(department_code="ECE")] == ["ECE"]


def test_department_time_slots_remain_separate(monkeypatch):
    store = {"time_slots": [{"period": "9:00 AM - 10:00 AM", "type": "TEACHING", "order_index": 1}],
             "time_slots_by_department": {}}
    monkeypatch.setattr(db, "get_client", lambda: None)
    monkeypatch.setattr(db, "_memory_store", store)
    monkeypatch.setattr(db, "_save_local_store", lambda value: None)

    cse_slots = [
        {"day": "Monday", "period": "9:00 AM - 10:00 AM", "type": "TEACHING", "order_index": 1},
        {"day": "Tuesday", "period": "9:00 AM - 10:00 AM", "type": "TEACHING", "order_index": 1},
    ]
    ece_slots = [
        {"day": "Monday", "period": "10:00 AM - 11:00 AM", "type": "TEACHING", "order_index": 1},
    ]
    db.save_time_slots(cse_slots, department="CSE")
    db.save_time_slots(ece_slots, department="ECE")

    assert len(db.get_time_slots("CSE")) == 2
    assert db.get_time_slots("ECE")[0]["period"] == "10:00 AM - 11:00 AM"
    assert db.get_time_slots("MECH")[0]["period"] == "9:00 AM - 10:00 AM"


def test_time_slot_schema_check_happens_before_existing_schedule_delete(monkeypatch):
    calls = []

    class MissingColumnsQuery:
        def select(self, columns):
            calls.append(("select", columns))
            return self

        def limit(self, count):
            calls.append(("limit", count))
            return self

        def execute(self):
            raise RuntimeError("column day does not exist")

    class FakeClient:
        def table(self, table_name):
            calls.append(("table", table_name))
            return MissingColumnsQuery()

    monkeypatch.setattr(db, "get_client", lambda: FakeClient())

    with pytest.raises(RuntimeError, match="Could not save time slots to Supabase"):
        db.save_time_slots(
            [{"day": "Monday", "period": "9:00 AM - 10:00 AM", "type": "TEACHING"}],
            department="ECE",
        )

    assert ("select", "department_code,day,is_teaching") in calls
    assert not any(call[0] == "delete" for call in calls)


def test_workbook_parser_does_not_emit_a_cse_department_record():
    workbook_path = PROJECT_ROOT / "assets" / "templates" / "CLASHFREE_Input_Template.xlsx"
    valid, errors, _, _, data = excel_reader.validate_excel_data(
        str(workbook_path), department="ECE", academic_year="2026-2027", semester="Semester V"
    )

    assert valid, errors
    assert data["departments"] == []
    assert all(row["department"] == "ECE" for row in data["requirements"])


def test_workbook_rejects_incomplete_explicit_lab_batch_coverage():
    workbook_path = PROJECT_ROOT / "assets" / "templates" / "CLASHFREE_Input_Template.xlsx"
    workbook = openpyxl.load_workbook(workbook_path)
    year_two = workbook["Year 2"]
    year_two["D6"] = "A1"
    year_two["E6"] = 20
    parsed, errors, _, _ = excel_reader.parse_multisheet_workbook(
        workbook, context_dept="ECE", context_academic_year="2026-2027"
    )

    assert parsed is not None
    assert any("batch strengths total 20" in error for error in errors)


def test_template_download_uses_multi_year_setup_layout():
    response = app.app.test_client().get("/api/download-template")
    assert response.status_code == 200
    workbook = openpyxl.load_workbook(io.BytesIO(response.data), read_only=True)
    assert workbook.sheetnames == ["Instructions", "Faculty", "Year 1", "Year 2", "Year 3", "Year Template", "Resources", "Time Slots"]
    assert workbook["Year 2"]["A4"].value == "Semester"


def test_multi_year_template_accepts_years_above_three():
    workbook = openpyxl.load_workbook(PROJECT_ROOT / "assets" / "templates" / "CLASHFREE_Input_Template.xlsx")
    year_five = workbook.copy_worksheet(workbook["Year Template"])
    year_five.title = "Year 5"
    values = ["Semester IX", "Z", 40, "", "", "MAT501", "Advanced Mathematics", "Lecture", 1, 1,
              "FAC004", "Classroom", "Projector"]
    for column, value in enumerate(values, 1):
        year_five.cell(5, column, value)
    parsed, errors, _, _ = excel_reader.parse_multisheet_workbook(
        workbook, context_dept="ECE", context_academic_year="2026-2027"
    )

    assert not errors, errors
    assert any(division["year"] == "Year 5" for division in parsed["divisions"])


def test_invalid_import_does_not_call_persistence(monkeypatch):
    monkeypatch.setattr(
        excel_reader,
        "validate_excel_data",
        lambda *args, **kwargs: (False, ["Invalid workbook"], [], {}, {}),
    )
    writes = []
    monkeypatch.setattr(db, "insert_faculty", lambda *args, **kwargs: writes.append("faculty"))

    response = app.app.test_client().post(
        "/api/import-excel",
        data={"file": (io.BytesIO(b"invalid"), "invalid.xlsx"), "department": "ECE"},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert writes == []


def test_import_persistence_exception_is_not_reported_as_success(monkeypatch):
    monkeypatch.setattr(
        excel_reader,
        "validate_excel_data",
        lambda *args, **kwargs: (
            True,
            [],
            [],
            {},
            {"faculty": [{"name": "Faculty"}], "rooms": [], "subjects": [], "divisions": [], "batches": []},
        ),
    )

    def fail_write(*args, **kwargs):
        raise RuntimeError("persistence unavailable")

    monkeypatch.setattr(db, "insert_faculty", fail_write)
    response = app.app.test_client().post(
        "/api/import-excel",
        data={"file": (io.BytesIO(b"valid"), "valid.xlsx"), "department": "ECE"},
        content_type="multipart/form-data",
    )

    assert response.status_code == 500
    assert response.get_json()["success"] is False


def test_import_checks_time_slot_schema_before_any_sheet_writes(monkeypatch):
    monkeypatch.setattr(
        excel_reader,
        "validate_excel_data",
        lambda *args, **kwargs: (
            True,
            [],
            [],
            {},
            {
                "faculty": [{"name": "Faculty"}],
                "rooms": [],
                "subjects": [],
                "divisions": [],
                "batches": [],
                "time_slots": [{"day": "Monday", "period": "9:00 AM - 10:00 AM"}],
            },
        ),
    )
    writes = []
    monkeypatch.setattr(
        db,
        "validate_time_slots_schema",
        lambda: (_ for _ in ()).throw(RuntimeError("Could not save time slots to Supabase; missing columns")),
    )
    monkeypatch.setattr(db, "insert_faculty", lambda *args, **kwargs: writes.append("faculty"))

    response = app.app.test_client().post(
        "/api/import-excel",
        data={"file": (io.BytesIO(b"valid"), "valid.xlsx"), "department": "ECE"},
        content_type="multipart/form-data",
    )

    assert response.status_code == 503
    assert "No workbook sheets were written" in response.get_json()["error"]
    assert writes == []


def test_template_import_succeeds_with_department_scoped_slot_schema(monkeypatch):
    saved = []
    monkeypatch.setattr(db, "validate_time_slots_schema", lambda: None)
    for name in ("insert_faculty", "insert_rooms", "insert_subjects", "insert_divisions", "insert_batches", "save_requirements"):
        monkeypatch.setattr(db, name, lambda rows, *args, _name=name, **kwargs: saved.append((_name, rows)))
    monkeypatch.setattr(
        db,
        "save_time_slots",
        lambda rows, department=None: saved.append(("save_time_slots", department, rows)),
    )

    template = PROJECT_ROOT / "assets" / "templates" / "CLASHFREE_Input_Template.xlsx"
    response = app.app.test_client().post(
        "/api/import-excel",
        data={"file": (template.open("rb"), "template.xlsx"), "department": "ECE"},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200, response.get_json()
    assert response.get_json()["success"] is True
    _, department, saved_slots = next(item for item in saved if item[0] == "save_time_slots")
    assert department == "ECE"
    assert saved_slots


def test_contiguous_blocks_do_not_skip_a_break():
    original_order = scheduler._period_order_map
    try:
        scheduler._period_order_map = {"9:00 AM - 10:00 AM": 0, "11:00 AM - 12:00 PM": 2}
        slots = [
            ("Monday", "9:00 AM - 10:00 AM", True),
            ("Monday", "11:00 AM - 12:00 PM", True),
        ]
        assert scheduler._build_contiguous_blocks(slots, 2) == []
    finally:
        scheduler._period_order_map = original_order


def test_contiguous_blocks_reject_clock_gaps():
    original_order = scheduler._period_order_map
    try:
        first = "9:00 AM - 9:50 AM"
        second = "10:00 AM - 11:00 AM"
        scheduler._period_order_map = {first: 0, second: 1}
        assert scheduler._build_contiguous_blocks(
            [("Monday", first, True), ("Monday", second, True)], 2
        ) == []
    finally:
        scheduler._period_order_map = original_order
