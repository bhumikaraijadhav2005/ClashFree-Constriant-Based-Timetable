"""Historical source patch utility retained for reference; do not run it."""

import re
from pathlib import Path

db_file = Path(__file__).resolve().parents[2] / "backend" / "db.py"
with db_file.open("r", encoding="utf-8") as f:
    text = f.read()

# 1. Replace insert_divisions
old_ins_div = """def insert_divisions(division_list: list):
    client = get_client()
    if client:
        try:
            client.table("divisions").delete().neq("id", 0).execute()
            if division_list:
                client.table("divisions").insert(division_list).execute()
        except Exception:
            pass
    for idx, d in enumerate(division_list):
        if "id" not in d or not d["id"]:
            d["id"] = idx + 1
    _memory_store["divisions"] = list(division_list)
    _save_local_store(_memory_store)"""

new_ins_div = """def insert_divisions(division_list: list, dept_code: str = None):
    client = get_client()
    if client:
        try:
            if dept_code:
                client.table("divisions").delete().eq("department_code", dept_code).execute()
            else:
                client.table("divisions").delete().neq("id", 0).execute()
            if division_list:
                client.table("divisions").insert(division_list).execute()
        except Exception:
            pass

    existing = _memory_store.get("divisions", [])
    if dept_code:
        # Retain divisions of other departments
        retained = [d for d in existing if d.get("department_code") != dept_code and d.get("department") != dept_code]
    else:
        retained = []

    max_id = max([d.get("id", 0) for d in retained] or [0])
    for idx, d in enumerate(division_list):
        if dept_code and not d.get("department_code"):
            d["department_code"] = dept_code
        if "id" not in d or not d["id"]:
            max_id += 1
            d["id"] = max_id
        retained.append(d)

    _memory_store["divisions"] = retained
    _save_local_store(_memory_store)"""

assert old_ins_div in text, "Could not find insert_divisions in db.py"
text = text.replace(old_ins_div, new_ins_div, 1)

# 2. Replace insert_batches
old_ins_bat = """def insert_batches(batch_list: list):
    client = get_client()
    if client:
        try:
            client.table("batches").delete().neq("id", 0).execute()
            if batch_list:
                client.table("batches").insert(batch_list).execute()
        except Exception:
            pass
    for idx, b in enumerate(batch_list):
        if "id" not in b or not b["id"]:
            b["id"] = idx + 1
    _memory_store["batches"] = list(batch_list)
    _save_local_store(_memory_store)"""

new_ins_bat = """def insert_batches(batch_list: list, dept_code: str = None):
    client = get_client()
    if client:
        try:
            if dept_code:
                client.table("batches").delete().eq("department_code", dept_code).execute()
            else:
                client.table("batches").delete().neq("id", 0).execute()
            if batch_list:
                client.table("batches").insert(batch_list).execute()
        except Exception:
            pass

    existing = _memory_store.get("batches", [])
    if dept_code:
        retained = [b for b in existing if b.get("department_code") != dept_code]
    else:
        retained = []

    max_id = max([b.get("id", 0) for b in retained] or [0])
    for idx, b in enumerate(batch_list):
        if dept_code and not b.get("department_code"):
            b["department_code"] = dept_code
        if "id" not in b or not b["id"]:
            max_id += 1
            b["id"] = max_id
        retained.append(b)

    _memory_store["batches"] = retained
    _save_local_store(_memory_store)"""

assert old_ins_bat in text, "Could not find insert_batches in db.py"
text = text.replace(old_ins_bat, new_ins_bat, 1)

# 3. Replace insert_rooms
old_ins_room = """def insert_rooms(room_list: list):
    client = get_client()
    if client:
        try:
            client.table("rooms").delete().neq("id", 0).execute()
            cleaned = []
            for r in room_list:
                cleaned.append({
                    "name": r.get("name"),
                    "type": r.get("type", "Classroom"),
                    "capacity": r.get("capacity", 60)
                })
            client.table("rooms").insert(cleaned).execute()
        except Exception as e:
            print(f"Supabase insert rooms error: {e}")
    _memory_store["rooms"] = list(room_list)
    _save_local_store(_memory_store)"""

new_ins_room = """def insert_rooms(room_list: list, dept_code: str = None):
    client = get_client()
    if client:
        try:
            if dept_code:
                client.table("rooms").delete().eq("department", dept_code).execute()
            else:
                client.table("rooms").delete().neq("id", 0).execute()
            cleaned = []
            for r in room_list:
                cleaned.append({
                    "name": r.get("name"),
                    "type": r.get("type", "Classroom"),
                    "capacity": r.get("capacity", 60),
                    "department": r.get("department") or dept_code or "CSE"
                })
            client.table("rooms").insert(cleaned).execute()
        except Exception as e:
            print(f"Supabase insert rooms error: {e}")

    existing = _memory_store.get("rooms", [])
    if dept_code:
        # Retain other department rooms and shared college resources
        retained = [r for r in existing if r.get("department") != dept_code and not r.get("is_shared")]
    else:
        retained = []

    max_id = max([r.get("id", 0) for r in retained] or [0])
    for idx, r in enumerate(room_list):
        if dept_code and not r.get("department"):
            r["department"] = dept_code
        if "id" not in r or not r["id"]:
            max_id += 1
            r["id"] = max_id
        retained.append(r)

    _memory_store["rooms"] = retained
    _save_local_store(_memory_store)"""

assert old_ins_room in text, "Could not find insert_rooms in db.py"
text = text.replace(old_ins_room, new_ins_room, 1)

# 4. Replace insert_faculty
old_ins_fac = """def insert_faculty(faculty_list: list):
    client = get_client()
    if client:
        try:
            client.table("faculty").delete().neq("id", 0).execute()
            cleaned = []
            for f in faculty_list:
                cleaned.append({
                    "name": f.get("name"),
                    "code": f.get("code"),
                    "subjects": f.get("subjects", []),
                    "available_from": f.get("available_from", "09:00"),
                    "available_to": f.get("available_to", "17:00"),
                    "preferred_time": f.get("preferred_time", "Any"),
                    "max_load": f.get("max_load", 20)
                })
            client.table("faculty").insert(cleaned).execute()
        except Exception as e:
            print(f"Supabase insert faculty error: {e}")
    _memory_store["faculty"] = list(faculty_list)
    _save_local_store(_memory_store)"""

new_ins_fac = """def insert_faculty(faculty_list: list, dept_code: str = None):
    client = get_client()
    if client:
        try:
            if dept_code:
                client.table("faculty").delete().eq("department", dept_code).execute()
            else:
                client.table("faculty").delete().neq("id", 0).execute()
            cleaned = []
            for f in faculty_list:
                cleaned.append({
                    "name": f.get("name"),
                    "code": f.get("code"),
                    "department": f.get("department") or dept_code or "CSE",
                    "subjects": f.get("subjects", []),
                    "available_from": f.get("available_from", "09:00"),
                    "available_to": f.get("available_to", "17:00"),
                    "preferred_time": f.get("preferred_time", "Any"),
                    "max_load": f.get("max_load", 20)
                })
            client.table("faculty").insert(cleaned).execute()
        except Exception as e:
            print(f"Supabase insert faculty error: {e}")

    existing = _memory_store.get("faculty", [])
    if dept_code:
        retained = [f for f in existing if f.get("department") != dept_code]
    else:
        retained = []

    max_id = max([f.get("id", 0) for f in retained] or [0])
    for idx, f in enumerate(faculty_list):
        if dept_code and not f.get("department"):
            f["department"] = dept_code
        if "id" not in f or not f["id"]:
            max_id += 1
            f["id"] = max_id
        retained.append(f)

    _memory_store["faculty"] = retained
    _save_local_store(_memory_store)"""

assert old_ins_fac in text, "Could not find insert_faculty in db.py"
text = text.replace(old_ins_fac, new_ins_fac, 1)

# 5. Replace insert_subjects
old_ins_sub = """def insert_subjects(subject_list: list):
    client = get_client()
    if client:
        try:
            client.table("subjects").delete().neq("id", 0).execute()
            cleaned = []
            for s in subject_list:
                cleaned.append({
                    "name": s.get("name"),
                    "code": s.get("code"),
                    "lectures_per_week": s.get("lectures_per_week", 3),
                    "labs_per_week": s.get("labs_per_week", 0),
                    "requires_lab": s.get("requires_lab", False)
                })
            client.table("subjects").insert(cleaned).execute()
        except Exception as e:
            print(f"Supabase insert subjects error: {e}")
    _memory_store["subjects"] = list(subject_list)
    _save_local_store(_memory_store)"""

new_ins_sub = """def insert_subjects(subject_list: list, dept_code: str = None):
    client = get_client()
    if client:
        try:
            if dept_code:
                client.table("subjects").delete().eq("department", dept_code).execute()
            else:
                client.table("subjects").delete().neq("id", 0).execute()
            cleaned = []
            for s in subject_list:
                cleaned.append({
                    "name": s.get("name"),
                    "code": s.get("code"),
                    "department": s.get("department") or dept_code or "CSE",
                    "lectures_per_week": s.get("lectures_per_week", 3),
                    "labs_per_week": s.get("labs_per_week", 0),
                    "requires_lab": s.get("requires_lab", False)
                })
            client.table("subjects").insert(cleaned).execute()
        except Exception as e:
            print(f"Supabase insert subjects error: {e}")

    existing = _memory_store.get("subjects", [])
    if dept_code:
        retained = [s for s in existing if s.get("department") != dept_code]
    else:
        retained = []

    max_id = max([s.get("id", 0) for s in retained] or [0])
    for idx, s in enumerate(subject_list):
        if dept_code and not s.get("department"):
            s["department"] = dept_code
        if "id" not in s or not s["id"]:
            max_id += 1
            s["id"] = max_id
        retained.append(s)

    _memory_store["subjects"] = retained
    _save_local_store(_memory_store)"""

assert old_ins_sub in text, "Could not find insert_subjects in db.py"
text = text.replace(old_ins_sub, new_ins_sub, 1)

# 6. Replace save_requirements and get_requirements
old_req_block = """def get_requirements(department: str = "CSE"):
    reqs = _memory_store.get("requirements", [])
    if department:
        return [r for r in reqs if r.get("department", "CSE") == department]
    return reqs

def save_requirements(req_list: list):
    _memory_store["requirements"] = list(req_list)
    _save_local_store(_memory_store)"""

new_req_block = """def get_requirements(department: str = None):
    reqs = _memory_store.get("requirements", [])
    if department:
        return [r for r in reqs if r.get("department") == department]
    return reqs

def save_requirements(req_list: list, department: str = "CSE"):
    existing = _memory_store.get("requirements", [])
    retained = [r for r in existing if r.get("department") != department]
    for r in req_list:
        if not r.get("department"):
            r["department"] = department
        retained.append(r)
    _memory_store["requirements"] = retained
    _save_local_store(_memory_store)"""

assert old_req_block in text, "Could not find old_req_block in db.py"
text = text.replace(old_req_block, new_req_block, 1)

# 7. Replace timetable & versioning handling
old_tt_block = """def get_timetable(version_id=None, department=None):
    client = get_client()
    tt = []
    if client:
        try:
            q = client.table("timetable").select("*").order("day_order").order("period")
            if department:
                q = q.eq("department", department)
            res = q.execute()
            if res.data:
                tt = res.data
        except Exception:
            pass
    if not tt:
        tt = list(_memory_store.get("timetable", []))

    if department:
        tt = [r for r in tt if r.get("department", "CSE") == department]
    if version_id:
        tt = [r for r in tt if str(r.get("version_id", 1)) == str(version_id)]
    return tt

def save_timetable(rows: list, version_id=1, department="CSE"):
    client = get_client()
    for r in rows:
        r["version_id"] = version_id
        if "department" not in r or not r["department"]:
            r["department"] = department

    if client:
        try:
            # First try with all columns
            client.table("timetable").delete().neq("id", 0).execute()
            if rows:
                client.table("timetable").insert(rows).execute()
        except Exception:
            try:
                # Core columns fallback
                client.table("timetable").delete().neq("id", 0).execute()
                cleaned = []
                for r in rows:
                    cleaned.append({
                        "day": r.get("day"),
                        "day_order": r.get("day_order", 0),
                        "period": r.get("period"),
                        "is_morning": r.get("is_morning", False),
                        "section": r.get("section"),
                        "subject": r.get("subject"),
                        "faculty_code": r.get("faculty_code"),
                        "faculty_name": r.get("faculty_name"),
                        "room": r.get("room"),
                        "is_lab": r.get("is_lab", False)
                    })
                client.table("timetable").insert(cleaned).execute()
            except Exception as e:
                print(f"Supabase save timetable error: {e}")

    _memory_store["timetable"] = list(rows)
    _save_local_store(_memory_store)

def clear_timetable():
    client = get_client()
    if client:
        try:
            client.table("timetable").delete().neq("id", 0).execute()
        except Exception:
            pass
    _memory_store["timetable"] = []
    _save_local_store(_memory_store)

def get_timetable_versions():
    client = get_client()
    if client:
        try:
            res = client.table("timetable_versions").select("*").order("version_number").execute()
            if res.data:
                return res.data
        except Exception:
            pass
    return _memory_store.get("timetable_versions", DEFAULT_STORE["timetable_versions"])

def create_timetable_version(version_dict: dict):
    client = get_client()
    if client:
        try:
            client.table("timetable_versions").insert(version_dict).execute()
        except Exception:
            pass
    versions = _memory_store.setdefault("timetable_versions", [])
    if "id" not in version_dict:
        version_dict["id"] = max([v.get("id", 0) for v in versions] or [0]) + 1
    versions.append(version_dict)
    _save_local_store(_memory_store)
    return version_dict

def set_active_version(version_id: int):
    client = get_client()
    if client:
        try:
            client.table("timetable_versions").update({"is_active": False}).neq("id", 0).execute()
            client.table("timetable_versions").update({"is_active": True}).eq("id", version_id).execute()
        except Exception:
            pass
    for v in _memory_store.get("timetable_versions", []):
        v["is_active"] = (v.get("id") == version_id or v.get("version_number") == version_id)
    _save_local_store(_memory_store)"""

new_tt_block = """def get_timetable_versions(department=None):
    client = get_client()
    if client:
        try:
            q = client.table("timetable_versions").select("*").order("version_number")
            if department:
                q = q.eq("department", department)
            res = q.execute()
            if res.data:
                return res.data
        except Exception:
            pass
    versions = _memory_store.get("timetable_versions", DEFAULT_STORE.get("timetable_versions", []))
    if department:
        return [v for v in versions if v.get("department") == department]
    return versions

def get_active_timetable_version(department="CSE", academic_year=None, semester=None):
    versions = get_timetable_versions(department)
    for v in versions:
        if v.get("is_active"):
            if academic_year and v.get("academic_year") and v.get("academic_year") != academic_year:
                continue
            if semester and v.get("semester") and v.get("semester") != semester:
                continue
            return v
    # Fallback to the latest version for that department if no explicit active flag
    if versions:
        return versions[-1]
    return None

def get_timetable(version_id=None, department=None, academic_year=None, semester=None):
    all_tt = _memory_store.get("timetable", [])

    if version_id:
        target_rows = [r for r in all_tt if str(r.get("version_id")) == str(version_id)]
    else:
        active_ver = get_active_timetable_version(department=department or "CSE", academic_year=academic_year, semester=semester)
        if active_ver:
            target_rows = [r for r in all_tt if str(r.get("version_id")) == str(active_ver.get("id"))]
        else:
            target_rows = []

    if department:
        target_rows = [r for r in target_rows if r.get("department") == department]

    return target_rows

def save_timetable(rows: list, version_id=1, department="CSE", academic_year=None, semester=None):
    for r in rows:
        r["version_id"] = version_id
        r["department"] = department
        if academic_year and not r.get("academic_year"):
            r["academic_year"] = academic_year
        if semester and not r.get("semester"):
            r["semester"] = semester

    client = get_client()
    if client:
        try:
            # Delete only existing rows with this exact version_id and department
            client.table("timetable").delete().eq("version_id", version_id).eq("department", department).execute()
            if rows:
                client.table("timetable").insert(rows).execute()
        except Exception as e:
            print(f"Supabase save timetable error: {e}")

    # Retain all historical versions and other departments in local persistent store
    current_store = _memory_store.get("timetable", [])
    retained = [r for r in current_store if not (str(r.get("version_id")) == str(version_id) and r.get("department") == department)]
    retained.extend(rows)
    _memory_store["timetable"] = retained
    _save_local_store(_memory_store)

def clear_timetable(department=None):
    client = get_client()
    if client:
        try:
            if department:
                client.table("timetable").delete().eq("department", department).execute()
            else:
                client.table("timetable").delete().neq("id", 0).execute()
        except Exception:
            pass
    if department:
        _memory_store["timetable"] = [r for r in _memory_store.get("timetable", []) if r.get("department") != department]
    else:
        _memory_store["timetable"] = []
    _save_local_store(_memory_store)

def create_timetable_version(version_dict: dict):
    dept = version_dict.get("department", "CSE")
    versions = _memory_store.setdefault("timetable_versions", [])

    # If new version is marked active, archive previous active versions in the same department
    if version_dict.get("is_active"):
        for v in versions:
            if v.get("department") == dept:
                v["is_active"] = False
                v["status"] = "ARCHIVED"

    if "id" not in version_dict:
        version_dict["id"] = max([v.get("id", 0) for v in versions] or [0]) + 1

    client = get_client()
    if client:
        try:
            if version_dict.get("is_active"):
                client.table("timetable_versions").update({"is_active": False, "status": "ARCHIVED"}).eq("department", dept).execute()
            client.table("timetable_versions").insert(version_dict).execute()
        except Exception:
            pass

    versions.append(version_dict)
    _save_local_store(_memory_store)
    return version_dict

def set_active_version(version_id: int, department: str = None):
    versions = _memory_store.get("timetable_versions", [])
    target = None
    for v in versions:
        if str(v.get("id")) == str(version_id) or str(v.get("version_number")) == str(version_id):
            target = v
            break

    if not target:
        return False

    dept = target.get("department") or department

    client = get_client()
    if client:
        try:
            if dept:
                client.table("timetable_versions").update({"is_active": False, "status": "ARCHIVED"}).eq("department", dept).execute()
            else:
                client.table("timetable_versions").update({"is_active": False, "status": "ARCHIVED"}).neq("id", 0).execute()
            client.table("timetable_versions").update({"is_active": True, "status": "ACTIVE"}).eq("id", target.get("id")).execute()
        except Exception:
            pass

    for v in versions:
        if not dept or v.get("department") == dept:
            if str(v.get("id")) == str(target.get("id")):
                v["is_active"] = True
                v["status"] = "ACTIVE"
            else:
                v["is_active"] = False
                v["status"] = "ARCHIVED"

    _save_local_store(_memory_store)
    return True

def restore_timetable_version(version_id: int, department: str = None, restored_by: str = "Admin"):
    \"\"\"
    Clones a historical timetable version into a brand-new ACTIVE version,
    preserving complete historical integrity without destroying old versions.
    \"\"\"
    from datetime import datetime
    versions = _memory_store.get("timetable_versions", [])
    target = None
    for v in versions:
        if str(v.get("id")) == str(version_id) or str(v.get("version_number")) == str(version_id):
            target = v
            break

    if not target:
        return None

    dept = target.get("department") or department or "CSE"
    dept_versions = [v for v in versions if v.get("department") == dept]
    next_num = max([v.get("version_number", 0) for v in dept_versions] or [0]) + 1

    # Fetch rows from the target historical version
    historical_rows = [r for r in _memory_store.get("timetable", []) if str(r.get("version_id")) == str(target.get("id"))]

    # Create new active version
    new_version_id = max([v.get("id", 0) for v in versions] or [0]) + 1
    new_version = {
        "id": new_version_id,
        "version_number": next_num,
        "name": f"Version {next_num} (Restored from Version {target.get('version_number', target.get('id'))})",
        "department": dept,
        "academic_year": target.get("academic_year", "2026-2027"),
        "semester": target.get("semester", "Semester III"),
        "scope": target.get("scope", f"{dept} Timetable"),
        "status": "ACTIVE",
        "is_active": True,
        "created_at": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "created_by": f"Restored by {restored_by}",
        "sessions_count": len(historical_rows),
        "conflicts_count": 0
    }

    # Archive previous active versions in this department
    for v in versions:
        if v.get("department") == dept:
            v["is_active"] = False
            v["status"] = "ARCHIVED"

    versions.append(new_version)

    # Clone historical rows with new version_id
    cloned_rows = []
    for r in historical_rows:
        rc = dict(r)
        rc["version_id"] = new_version_id
        rc["department"] = dept
        cloned_rows.append(rc)

    # Save cloned rows
    current_tt = _memory_store.get("timetable", [])
    current_tt.extend(cloned_rows)
    _memory_store["timetable"] = current_tt

    _save_local_store(_memory_store)
    return new_version"""

assert old_tt_block in text, "Could not find old_tt_block in db.py"
text = text.replace(old_tt_block, new_tt_block, 1)

with db_file.open("w", encoding="utf-8", newline="\r\n") as f:
    f.write(text)

print("SUCCESS: backend/db.py patched with non-destructive multi-department & versioning logic!")

