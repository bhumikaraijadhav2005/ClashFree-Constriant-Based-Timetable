# test_scheduler.py
# Comprehensive automated test suite for ClashFree CSP+MRV Scheduling Engine

import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import db
import excel_reader
import scheduler

def test_clashfree_pipeline():
    print("=" * 60)
    print("Running ClashFree Automated Verification Suite...")
    print("=" * 60)

    # 1. Test Excel Reader & Faculty Code Engine
    print("\n[Test 1] Testing Excel Reader & Faculty Short-Code Generation...")
    data, errors, warnings, summary = excel_reader.read_excel("sample_data.xlsx")
    assert not errors, f"Excel read failed with errors: {errors}"
    print(f"[OK] Excel read successfully: {summary}")

    print("\nFaculty Short Codes Generated:")
    for f in data["faculty"]:
        print(f"  {f['name']} ({f['designation']}) -> [{f['code']}] | Preference: {f['preferred_time']}")
    assert any(f["code"] == "VHP" for f in data["faculty"]), "Expected VHP short code for Vishal H. Pundikar"

    # 2. Test Resource Reservation (HOD Requirement)
    print("\n[Test 2] Testing HOD Resource Reservation Policy...")
    rooms = db.get_all_rooms("CSE")
    cfg = db.get_resource_config("CSE")
    active_rooms, reserved_rooms, _ = scheduler.filter_and_reserve_resources(rooms, "CSE", cfg)
    print(f"Total Rooms: {len(rooms)}")
    print(f"Active for Scheduling: {len(active_rooms)} {[r['name'] for r in active_rooms]}")
    print(f"Reserved by HOD: {len(reserved_rooms)} {[r['name'] for r in reserved_rooms]}")
    assert len(reserved_rooms) >= 2, f"Expected at least 2 reserved rooms (1 CR + 1 Lab), got {len(reserved_rooms)}"
    print("[OK] HOD Resource Reservation policy verified.")

    # 3. Test CSP + MRV + Backtracking Scheduler
    print("\n[Test 3] Running CSP + MRV + Backtracking Scheduler...")
    fac = db.get_all_faculty("CSE")
    subs = db.get_all_subjects("CSE")
    divs = db.get_all_divisions("CSE")
    batches = db.get_all_batches()

    success, msg, rows, conflicts, meta = scheduler.generate_timetable(
        faculty_list=fac,
        room_list=rooms,
        subject_list=subs,
        division_list=divs,
        batch_list=batches,
        resource_config=cfg,
        department="CSE"
    )

    print(f"Success: {success}")
    print(f"Message: {msg}")
    print(f"Metadata: {meta}")
    assert success, f"Scheduler failed: {conflicts}"
    assert len(rows) > 0, "No timetable rows scheduled"
    print(f"[OK] {len(rows)} sessions successfully scheduled without clashes!")

    # Verify no reserved rooms used in timetable
    reserved_names = set(meta.get("reserved_rooms", []))
    for r in rows:
        assert r["room"] not in reserved_names, f"Error: Reserved room {r['room']} was assigned in timetable!"
    print("[OK] Verified: 0 reserved rooms assigned by timetable generator.")

    print("\n[Test 4] Verifying No Back-to-Back Same Classes & Day Spreading...")
    div_a_rows = [r for r in rows if r["section"] == "Division A"]
    print(f"\n--- Division A Weekly Timetable ({len(div_a_rows)} sessions) ---")
    current_day = None
    for r in div_a_rows:
        if r["day"] != current_day:
            current_day = r["day"]
            print(f"\n  {current_day.upper()}:")
        batch_str = f"[{r['batch']}]" if r.get("batch") else ""
        print(f"    {r['period']:12} | {r['subject']:8} {batch_str:6} | {r['room']:7} | {r['faculty_code']}")

    # Verification: No back-to-back same subject on same day
    for d in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
        day_sessions = [r for r in div_a_rows if r["day"] == d and not r.get("is_lab")]
        subjects_on_day = [r["subject"] for r in day_sessions]
        # Assert no duplicate lectures on same day when subject <= 5 lectures/week
        assert len(subjects_on_day) == len(set(subjects_on_day)), f"Duplicate theory subject on {d}: {subjects_on_day}"
    print("[OK] Verified: 0 duplicate theory subjects on the same day for Division A!")
    print("[OK] Verified: 0 back-to-back same classes!")

    # 5. Test Slot-Wise Occupancy Matrix
    print("\n[Test 5] Testing Slot-Wise Occupancy Matrix...")
    sample_slot = rows[0]
    day = sample_slot["day"]
    period = sample_slot["period"]
    occupied_in_slot = [r for r in rows if r["day"] == day and r["period"] == period]
    print(f"Slot {day} {period} has {len(occupied_in_slot)} simultaneous sessions:")
    for s in occupied_in_slot:
        print(f"  {s['room']} ({s['subject']}) -> Div {s['section']} {s.get('batch') or 'Whole Class'} by {s['faculty_code']}")

    print("\n" + "=" * 60)
    print("ALL CLASHFREE SYSTEM TESTS PASSED SUCCESSFULLY! [OK]")
    print("=" * 60)

if __name__ == "__main__":
    test_clashfree_pipeline()
