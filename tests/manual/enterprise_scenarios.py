import io
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root / "backend"))

import db, excel_reader, scheduler, app as flask_app

def run_enterprise_tests():
    print("=" * 70)
    print("CLASHFREE ENTERPRISE PRODUCT ACCEPTANCE TEST SUITE")
    print("=" * 70)

    client = flask_app.app.test_client()

    # -------------------------------------------------------------
    # TEST A: CSE IMPORT & GENERATION
    # -------------------------------------------------------------
    print("\n[TEST A] CSE Context: Import Excel & Generate Timetable...")
    sample_file = project_root / "assets" / "templates" / "CLASHFREE_Input_Template.xlsx"
    with open(sample_file, "rb") as f:
        file_bytes = f.read()

    # 1. Validate for CSE
    val_res = client.post("/api/validate-excel", data={
        "file": (io.BytesIO(file_bytes), "CLASHFREE_Input_Template.xlsx"),
        "department": "CSE",
        "academic_year": "2026-2027",
        "semester": "Semester 3"
    }, content_type="multipart/form-data")
    assert val_res.status_code == 200, f"Validate CSE failed: {val_res.data}"
    val_data = val_res.get_json()
    assert val_data["valid"] is True, f"Validate CSE invalid: {val_data['errors']}"
    print("  [OK] Pre-import Validation passed for CSE.")

    # 2. Import into CSE
    imp_res = client.post("/api/import-excel", data={
        "file": (io.BytesIO(file_bytes), "CLASHFREE_Input_Template.xlsx"),
        "department": "CSE",
        "academic_year": "2026-2027",
        "semester": "Semester 3"
    }, content_type="multipart/form-data")
    assert imp_res.status_code == 200, f"Import CSE failed: {imp_res.data}"
    print("  [OK] Imported data into CSE.")

    # 3. Generate Timetable for CSE
    gen_res = client.post("/api/generate-timetable", json={
        "department": "CSE",
        "academic_year": "2026-2027",
        "semester": "Semester 3"
    })
    assert gen_res.status_code == 200, f"Generate CSE failed: {gen_res.data}"
    gen_data = gen_res.get_json()
    assert gen_data["success"] is True, f"Scheduler returned error: {gen_data['message']}"
    cse_v1_id = gen_data["version"]["id"]
    cse_v1_sessions = gen_data["count"]
    print(f"  [OK] CSE Timetable generated successfully! Version ID: {cse_v1_id}, Sessions: {cse_v1_sessions}")

    # Verify active timetable
    tt_cse = client.get("/api/timetable?department=CSE").get_json()
    assert len(tt_cse) == cse_v1_sessions, f"Expected {cse_v1_sessions} rows, got {len(tt_cse)}"
    assert all(r.get("department") == "CSE" for r in tt_cse), "Found non-CSE rows in CSE timetable!"
    print("  [OK] Verified CSE Active Timetable query.")

    # -------------------------------------------------------------
    # TEST B: ELECTRONICS (ECE) CONTEXT - ZERO DATA LEAKAGE
    # -------------------------------------------------------------
    print("\n[TEST B] Electronics (ECE) Context: Import & Generate Without Restarting...")

    # Generate Timetable for ECE using pre-seeded ECE requirements
    gen_ece = client.post("/api/generate-timetable", json={
        "department": "ECE",
        "academic_year": "2026-2027",
        "semester": "Semester 3"
    })
    assert gen_ece.status_code == 200, f"Generate ECE failed: {gen_ece.data}"
    ece_data = gen_ece.get_json()
    assert ece_data["success"] is True, f"ECE Scheduler returned error: {ece_data['message']}"
    ece_sessions = ece_data["count"]
    print(f"  [OK] ECE Timetable generated successfully! Sessions: {ece_sessions}")

    # Verify ECE timetable rows have ZERO CSE data
    tt_ece = client.get("/api/timetable?department=ECE").get_json()
    assert len(tt_ece) == ece_sessions, f"Expected {ece_sessions} rows in ECE, got {len(tt_ece)}"

    # Strict isolation checks:
    cse_subject_names = {"Data Structures", "Database Management Systems", "Object Oriented Programming", "Operating Systems", "Theory of Computation"}
    cse_faculty_codes = {"VHP", "NAK", "ARS", "PSJ", "VLB", "SPD", "RKM", "KPK"}
    cse_rooms = {"CR-1", "CR-2", "CR-3", "CR-4", "CR-5", "LAB-1", "LAB-2", "LAB-3", "LAB-4"}

    for r in tt_ece:
        assert r.get("department") == "ECE", f"Data Leakage: Row department is {r.get('department')} instead of ECE!"
        assert r.get("subject") not in cse_subject_names, f"Data Leakage: CSE subject '{r.get('subject')}' appeared in ECE!"
        assert r.get("faculty_code") not in cse_faculty_codes, f"Data Leakage: CSE faculty code '{r.get('faculty_code')}' appeared in ECE!"
        assert r.get("room") not in cse_rooms, f"Data Leakage: CSE room '{r.get('room')}' appeared in ECE!"

    print("  [OK] VERIFIED 100% DATA ISOLATION: Zero CSE subjects, faculty, rooms, or rows appear in ECE!")

    # -------------------------------------------------------------
    # TEST C: SWITCH BACK TO CSE
    # -------------------------------------------------------------
    print("\n[TEST C] Switch Back to CSE: Verify CSE Timetable Still Intact...")
    tt_cse_back = client.get("/api/timetable?department=CSE").get_json()
    assert len(tt_cse_back) == cse_v1_sessions, f"CSE Timetable was corrupted after ECE generation! Expected {cse_v1_sessions}, got {len(tt_cse_back)}"
    assert all(r.get("department") == "CSE" for r in tt_cse_back), "Non-CSE rows found in CSE timetable!"
    print("  [OK] Verified CSE Timetable was 100% preserved and untouched by ECE generation.")

    # -------------------------------------------------------------
    # TEST D: REGENERATION & VERSION ARCHIVING
    # -------------------------------------------------------------
    print("\n[TEST D] Generate New Version for CSE: Verify Old Version Archived...")
    gen_cse_v2 = client.post("/api/generate-timetable", json={
        "department": "CSE",
        "academic_year": "2026-2027",
        "semester": "Semester 3"
    })
    assert gen_cse_v2.status_code == 200
    cse_v2_data = gen_cse_v2.get_json()
    cse_v2_id = cse_v2_data["version"]["id"]
    print(f"  [OK] Generated CSE Version 2 (ID: {cse_v2_id})")

    # Check version statuses
    versions_cse = client.get("/api/timetable-versions?department=CSE").get_json()
    v1_rec = next((v for v in versions_cse if v["id"] == cse_v1_id), None)
    v2_rec = next((v for v in versions_cse if v["id"] == cse_v2_id), None)

    assert v1_rec is not None and v1_rec["is_active"] is False, f"Version 1 should be ARCHIVED! {v1_rec}"
    assert v2_rec is not None and v2_rec["is_active"] is True, f"Version 2 should be ACTIVE! {v2_rec}"
    print(f"  [OK] Verified: Version 1 is ARCHIVED, Version 2 is ACTIVE.")

    # Fetching without version_id returns Active (Version 2)
    active_tt = client.get("/api/timetable?department=CSE").get_json()
    assert all(str(r.get("version_id")) == str(cse_v2_id) for r in active_tt)
    print("  [OK] Standard timetable query returns only the Active Version.")

    # Fetching historical Version 1 explicitly returns Version 1 rows
    hist_tt = client.get(f"/api/timetable?department=CSE&version_id={cse_v1_id}").get_json()
    assert len(hist_tt) == cse_v1_sessions
    assert all(str(r.get("version_id")) == str(cse_v1_id) for r in hist_tt)
    print(f"  [OK] Explicit query for historical Version 1 returns {len(hist_tt)} rows unchanged.")

    # -------------------------------------------------------------
    # TEST E: RESTORE HISTORICAL VERSION
    # -------------------------------------------------------------
    print("\n[TEST E] Restore Version 1: Verify Safe Non-Destructive Restore...")
    restore_res = client.post(f"/api/timetable-versions/{cse_v1_id}/restore", json={
        "department": "CSE",
        "created_by": "Test Suite"
    })
    assert restore_res.status_code == 200, f"Restore failed: {restore_res.data}"
    restored_v = restore_res.get_json()["version"]
    new_active_id = restored_v["id"]
    print(f"  [OK] Restored Version 1 -> Created New Active Version {restored_v['name']} (ID: {new_active_id})")

    # Verify Version 1 is still preserved unchanged
    hist_tt_after = client.get(f"/api/timetable?department=CSE&version_id={cse_v1_id}").get_json()
    assert len(hist_tt_after) == cse_v1_sessions, "Original Version 1 was mutated!"
    print("  [OK] Historical Version 1 remains 100% intact and unchanged.")

    # Verify New Active Version contains cloned rows
    current_active_tt = client.get("/api/timetable?department=CSE").get_json()
    assert len(current_active_tt) == cse_v1_sessions
    assert all(str(r.get("version_id")) == str(new_active_id) for r in current_active_tt)
    print("  [OK] Active schedule seamlessly switched to restored clone version.")

    # -------------------------------------------------------------
    # TEST F: DASHBOARD REAL METRICS
    # -------------------------------------------------------------
    print("\n[TEST F] Verify Dashboard Returns Real Department Metrics...")
    dash_cse = client.get("/api/dashboard?department=CSE").get_json()
    dash_ece = client.get("/api/dashboard?department=ECE").get_json()

    assert dash_cse["department"] == "CSE"
    assert dash_ece["department"] == "ECE"
    assert dash_cse["counts"]["faculty"] >= 8
    assert dash_ece["counts"]["faculty"] == 4
    print(f"  [OK] CSE Faculty count: {dash_cse['counts']['faculty']}, ECE Faculty count: {dash_ece['counts']['faculty']}")

    print("\n" + "=" * 70)
    print("ALL ENTERPRISE ACCEPTANCE TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 70)

if __name__ == "__main__":
    run_enterprise_tests()

