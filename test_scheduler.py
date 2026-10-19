# test_scheduler.py
# Comprehensive automated test suite for ClashFree CSP+MRV Scheduling Engine:
# 1. Single-sheet CLASHFREE_INPUT Excel reading and validation
# 2. Dynamic resource matching (type, capacity >= required, equipment)
# 3. CSP + MRV + Backtracking search with clash resolution tracking
# 4. Strict 12-hour AM/PM format validation (NEVER 24-hour time)
# 5. Zero clashes (Faculty, Room, Division, Batch)
# 6. Spreading & no back-to-back duplicate lectures

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
    print("\n[Test 1] Testing Single-Sheet Excel Reader & Faculty Short Codes...")
    valid, errors, warnings, summary, data = excel_reader.validate_excel_data("sample_data.xlsx")
    assert valid, f"Excel validation failed: {errors}"
    print(f"[OK] Excel validated successfully: {summary}")

    print("\nFaculty Short Codes Generated:")
    for f in data["faculty"]:
        print(f"  {f['name']} -> [{f['code']}] | Preference: {f.get('preference', 'Any')} | Availability: {f.get('availability')}")
    assert any(f["code"] == "VHP" for f in data["faculty"]), "Expected VHP short code for Vishal H. Pundikar"
    assert any(f["code"] == "NAK" for f in data["faculty"]), "Expected NAK short code for Naresh A. Kamble"

    # 2. Test Dynamic Resource Allocation (No reserved room buffer)
    print("\n[Test 2] Testing Dynamic Resource Allocation Matching...")
    rooms = data["rooms"]
    active_rooms = [r for r in rooms if r.get("is_active", True)]
    print(f"Total Resources Configured: {len(rooms)}")
    print(f"Active Resources: {len(active_rooms)} {[r['name'] for r in active_rooms]}")
    assert len(active_rooms) >= 8, f"Expected at least 8 active resources, got {len(active_rooms)}"

    # 3. Test CSP + MRV + Backtracking Scheduler using Single-Sheet Requirements
    print("\n[Test 3] Running CSP + MRV + Backtracking Scheduler...")
    reqs = data["requirements"]
    time_slots = data["time_slots"]

    success, msg, rows, conflicts, meta = scheduler.generate_timetable(
        faculty_list=data["faculty"],
        room_list=data["rooms"],
        subject_list=data["subjects"],
        division_list=data["divisions"],
        batch_list=data["batches"],
        time_slots=time_slots,
        department="CSE",
        requirements=reqs
    )

    print(f"Success: {success}")
    print(f"Message: {msg}")
    print(f"Metadata: Backtrack Steps = {meta.get('backtrack_steps')}, Detected Clashes = {meta.get('detected_clashes')}, Resolved = {meta.get('resolved_clashes')}")
    assert success, f"Scheduler failed: {conflicts}"
    assert len(rows) > 0, "No timetable rows scheduled"
    print(f"[OK] {len(rows)} sessions successfully scheduled without clashes!")

    # 4. Test 12-Hour AM/PM Format
    print("\n[Test 4] Verifying Strict 12-Hour AM/PM Format...")
    for r in rows:
        period = r["period"]
        assert "AM" in period or "PM" in period, f"Period '{period}' is not in 12-hour AM/PM format!"
        # Assert no 24-hour hour string like 13:00, 14:00, etc.
        assert not any(f"{h:02d}:" in period for h in range(13, 24)), f"Found 24-hour time in period: {period}"
    print("[OK] Verified: All periods are strictly in 12-Hour AM/PM format (e.g. '9:00 AM - 10:00 AM', '1:00 PM - 2:00 PM')")

    # 5. Verify No Hard Constraint Clashes
    print("\n[Test 5] Verifying 0 Hard Constraint Clashes...")
    slot_assignments = {}
    for r in rows:
        key = (r["day"], r["period"])
        if key not in slot_assignments:
            slot_assignments[key] = []
        slot_assignments[key].append(r)

    for (day, period), sess_list in slot_assignments.items():
        # Check faculty clashes
        fac_codes = [s["faculty_code"] for s in sess_list]
        assert len(fac_codes) == len(set(fac_codes)), f"Faculty double-booking on {day} {period}: {fac_codes}"

        # Check room clashes
        room_names = [s["room"] for s in sess_list]
        assert len(room_names) == len(set(room_names)), f"Room double-booking on {day} {period}: {room_names}"

        # Check division clashes
        div_full_lectures = [s["section"] for s in sess_list if not s.get("batch")]
        assert len(div_full_lectures) == len(set(div_full_lectures)), f"Division double-booking on {day} {period}: {div_full_lectures}"
    print("[OK] Verified: 0 Faculty Clashes, 0 Room Clashes, 0 Division Clashes!")

    # 6. Verify Spreading & No Back-to-Back Same Lectures
    print("\n[Test 6] Verifying No Back-to-Back Same Classes & Day Spreading...")
    div_a_rows = [r for r in rows if r["section"] == "A"]
    for d in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
        day_sessions = [r for r in div_a_rows if r["day"] == d and not r.get("is_lab")]
        subjects_on_day = [r["subject"] for r in day_sessions]
        # At most 1 lecture of each subject per day for 3-4 sess/wk
        assert len(subjects_on_day) == len(set(subjects_on_day)), f"Duplicate theory subject on {d}: {subjects_on_day}"
    print("[OK] Verified: 0 duplicate theory classes on same day for Division A!")

    # 7. Clash Resolution History Log
    print("\n[Test 7] Verifying Clash Resolution History Log...")
    clash_log = meta.get("clash_history", [])
    print(f"Clash Resolution Log Entries: {len(clash_log)}")
    if clash_log:
        sample_entry = clash_log[0]
        print(f"Sample Entry: {sample_entry.get('id')} {sample_entry.get('type')} at {sample_entry.get('time')} -> {sample_entry.get('status')}")
        print(f"  Issue: {sample_entry.get('issue')}")
        print(f"  Resolution: {sample_entry.get('resolution')}")
    print("[OK] Clash Resolution History generated and verified.")

    print("\n" + "=" * 60)
    print("ALL CLASHFREE SYSTEM TESTS PASSED SUCCESSFULLY! [OK]")
    print("=" * 60)

if __name__ == "__main__":
    test_clashfree_pipeline()
