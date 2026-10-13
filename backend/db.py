# backend/db.py
# Handles database storage for ClashFree:
# 1. Supabase PostgreSQL when SUPABASE_URL and SUPABASE_KEY are provided.
# 2. Resilient local fallback store (data_store.json) for extended schema
#    attributes or if tables haven't been run in Supabase SQL editor yet.

import os
import json
from pathlib import Path
from dotenv import load_dotenv

root_dir = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=root_dir / ".env")
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

_client = None

STORE_FILE = Path(__file__).resolve().parent / "data_store.json"

DEFAULT_STORE = {
    "departments": [
        {"id": 1, "code": "CSE", "name": "Computer Science and Engineering"},
        {"id": 2, "code": "E&TC", "name": "Electronics & Telecommunication Engineering"},
        {"id": 3, "code": "MECH", "name": "Mechanical Engineering"}
    ],
    "academic_structure": [
        {"id": 1, "department_code": "CSE", "degree": "B.Tech", "year": "Second Year", "semester": "Semester III", "academic_year": "2026-2027"},
        {"id": 2, "department_code": "E&TC", "degree": "B.Tech", "year": "Second Year", "semester": "Semester III", "academic_year": "2026-2027"}
    ],
    "divisions": [
        {"id": 1, "department_code": "CSE", "degree": "B.Tech", "year": "Second Year", "semester": "Semester III", "name": "Division A", "code": "CSE-A", "strength": 75},
        {"id": 2, "department_code": "CSE", "degree": "B.Tech", "year": "Second Year", "semester": "Semester III", "name": "Division B", "code": "CSE-B", "strength": 72}
    ],
    "batches": [
        {"id": 1, "division_name": "Division A", "name": "A1", "strength": 38},
        {"id": 2, "division_name": "Division A", "name": "A2", "strength": 37},
        {"id": 3, "division_name": "Division B", "name": "B1", "strength": 36},
        {"id": 4, "division_name": "Division B", "name": "B2", "strength": 36}
    ],
    "sections": [
        {"id": 1, "name": "CSE-A", "strength": 75, "department": "CSE"},
        {"id": 2, "name": "CSE-B", "strength": 72, "department": "CSE"}
    ],
    "rooms": [
        {"id": 1, "name": "CR-01", "type": "Classroom", "capacity": 80, "department": "CSE", "lab_type": "", "num_pcs": 0, "equipment": "Projector, Audio", "is_reserved": False, "reservation_reason": ""},
        {"id": 2, "name": "CR-02", "type": "Classroom", "capacity": 80, "department": "CSE", "lab_type": "", "num_pcs": 0, "equipment": "Projector, Smartboard", "is_reserved": False, "reservation_reason": ""},
        {"id": 3, "name": "CR-03", "type": "Classroom", "capacity": 75, "department": "CSE", "lab_type": "", "num_pcs": 0, "equipment": "Projector", "is_reserved": False, "reservation_reason": ""},
        {"id": 4, "name": "CR-04", "type": "Classroom", "capacity": 80, "department": "CSE", "lab_type": "", "num_pcs": 0, "equipment": "Projector", "is_reserved": False, "reservation_reason": ""},
        {"id": 5, "name": "CR-05", "type": "Classroom", "capacity": 80, "department": "CSE", "lab_type": "", "num_pcs": 0, "equipment": "Projector", "is_reserved": True, "reservation_reason": "Reserved for HOD Seminar / Electives"},
        {"id": 6, "name": "LAB-01", "type": "Lab", "capacity": 40, "department": "CSE", "lab_type": "Computer Lab", "num_pcs": 40, "equipment": "40 PCs, High-Speed LAN", "is_reserved": False, "reservation_reason": ""},
        {"id": 7, "name": "LAB-02", "type": "Lab", "capacity": 40, "department": "CSE", "lab_type": "Computer Lab", "num_pcs": 40, "equipment": "40 PCs, Linux OS", "is_reserved": False, "reservation_reason": ""},
        {"id": 8, "name": "LAB-03", "type": "Lab", "capacity": 40, "department": "CSE", "lab_type": "Computer Lab", "num_pcs": 40, "equipment": "40 PCs, Database Server", "is_reserved": False, "reservation_reason": ""},
        {"id": 9, "name": "LAB-04", "type": "Lab", "capacity": 40, "department": "CSE", "lab_type": "Computer Lab", "num_pcs": 40, "equipment": "40 PCs, AI Workstations", "is_reserved": True, "reservation_reason": "Reserved for Research / Project Work"},
        {"id": 10, "name": "CR-11", "type": "Classroom", "capacity": 70, "department": "E&TC", "lab_type": "", "num_pcs": 0, "equipment": "Projector", "is_reserved": False, "reservation_reason": ""},
        {"id": 11, "name": "LAB-05", "type": "Lab", "capacity": 40, "department": "E&TC", "lab_type": "Electronics Lab", "num_pcs": 20, "equipment": "DSO, Function Generators", "is_reserved": False, "reservation_reason": ""}
    ],
    "resource_config": [
        {"id": 1, "department": "CSE", "reserved_classrooms_count": 1, "reserved_labs_count": 1, "student_pc_ratio": "1:1"},
        {"id": 2, "department": "E&TC", "reserved_classrooms_count": 1, "reserved_labs_count": 0, "student_pc_ratio": "1:1"}
    ],
    "faculty": [
        {"id": 1, "name": "Mr. Vishal H. Pundikar", "code": "VHP", "designation": "Assistant Professor", "department": "CSE", "subjects": ["DSA", "DS Lab"], "available_from": "09:00", "available_to": "17:00", "preferred_time": "Morning", "blocked_slots": [], "max_load": 18},
        {"id": 2, "name": "Dr. Vikas L. Bhise", "code": "VLB", "designation": "Associate Professor", "department": "CSE", "subjects": ["DS Lab", "DBMS"], "available_from": "09:00", "available_to": "17:00", "preferred_time": "Morning", "blocked_slots": [], "max_load": 18},
        {"id": 3, "name": "Dr. Amit R. Sharma", "code": "ARS", "designation": "Professor & HOD", "department": "CSE", "subjects": ["TOC", "Maths"], "available_from": "09:00", "available_to": "13:00", "preferred_time": "Morning", "blocked_slots": ["Friday 14:00-15:00"], "max_load": 12},
        {"id": 4, "name": "Mrs. Sneha P. Desai", "code": "SPD", "designation": "Assistant Professor", "department": "CSE", "subjects": ["OS", "CN"], "available_from": "11:00", "available_to": "17:00", "preferred_time": "Afternoon", "blocked_slots": [], "max_load": 18},
        {"id": 5, "name": "Mr. Rahul K. Mehta", "code": "RKM", "designation": "Assistant Professor", "department": "CSE", "subjects": ["OS", "TOC"], "available_from": "09:00", "available_to": "17:00", "preferred_time": "Any", "blocked_slots": [], "max_load": 18},
        {"id": 6, "name": "Ms. Priya S. Joshi", "code": "PSJ", "designation": "Assistant Professor", "department": "CSE", "subjects": ["DBMS", "CN"], "available_from": "09:00", "available_to": "15:00", "preferred_time": "Morning", "blocked_slots": [], "max_load": 16}
    ],
    "subjects": [
        {"id": 1, "name": "DSA", "code": "CS301", "department": "CSE", "year": "Second Year", "semester": "Semester III", "lectures_per_week": 4, "labs_per_week": 0, "requires_lab": False, "lab_type": "", "student_pc_ratio": 1.0},
        {"id": 2, "name": "DS Lab", "code": "CS302L", "department": "CSE", "year": "Second Year", "semester": "Semester III", "lectures_per_week": 0, "labs_per_week": 2, "requires_lab": True, "lab_type": "Computer Lab", "student_pc_ratio": 1.0},
        {"id": 3, "name": "DBMS", "code": "CS303", "department": "CSE", "year": "Second Year", "semester": "Semester III", "lectures_per_week": 3, "labs_per_week": 0, "requires_lab": False, "lab_type": "", "student_pc_ratio": 1.0},
        {"id": 4, "name": "OS", "code": "CS304", "department": "CSE", "year": "Second Year", "semester": "Semester III", "lectures_per_week": 3, "labs_per_week": 0, "requires_lab": False, "lab_type": "", "student_pc_ratio": 1.0},
        {"id": 5, "name": "CN", "code": "CS305", "department": "CSE", "year": "Second Year", "semester": "Semester III", "lectures_per_week": 3, "labs_per_week": 0, "requires_lab": False, "lab_type": "", "student_pc_ratio": 1.0},
        {"id": 6, "name": "Maths", "code": "CS306", "department": "CSE", "year": "Second Year", "semester": "Semester III", "lectures_per_week": 3, "labs_per_week": 0, "requires_lab": False, "lab_type": "", "student_pc_ratio": 1.0},
        {"id": 7, "name": "TOC", "code": "CS307", "department": "CSE", "year": "Second Year", "semester": "Semester III", "lectures_per_week": 3, "labs_per_week": 0, "requires_lab": False, "lab_type": "", "student_pc_ratio": 1.0}
    ],
    "time_slots": [
        {"period": "09:00-10:00", "type": "TEACHING", "is_morning": True, "start_time": "09:00", "end_time": "10:00", "order_index": 1},
        {"period": "10:00-11:00", "type": "TEACHING", "is_morning": True, "start_time": "10:00", "end_time": "11:00", "order_index": 2},
        {"period": "11:00-11:15", "type": "SHORT_BREAK", "is_morning": True, "start_time": "11:00", "end_time": "11:15", "order_index": 3},
        {"period": "11:15-12:15", "type": "TEACHING", "is_morning": True, "start_time": "11:15", "end_time": "12:15", "order_index": 4},
        {"period": "12:15-13:00", "type": "LUNCH", "is_morning": False, "start_time": "12:15", "end_time": "13:00", "order_index": 5},
        {"period": "13:00-14:00", "type": "TEACHING", "is_morning": False, "start_time": "13:00", "end_time": "14:00", "order_index": 6},
        {"period": "14:00-15:00", "type": "TEACHING", "is_morning": False, "start_time": "14:00", "end_time": "15:00", "order_index": 7},
        {"period": "15:00-15:15", "type": "SHORT_BREAK", "is_morning": False, "start_time": "15:00", "end_time": "15:15", "order_index": 8},
        {"period": "15:15-16:15", "type": "TEACHING", "is_morning": False, "start_time": "15:15", "end_time": "16:15", "order_index": 9}
    ],
    "timetable_versions": [
        {"id": 1, "version_number": 1, "name": "Version 1 (Initial)", "academic_year": "2026-2027", "semester": "Semester III", "department": "CSE", "description": "Baseline generated schedule", "is_active": True, "created_by": "HOD CSE"}
    ],
    "timetable": [],
    "resource_sharing_requests": [
        {
            "id": 1,
            "resource_name": "CR-03",
            "day": "Monday",
            "period": "14:00-15:00",
            "owner_department": "CSE",
            "requesting_department": "E&TC",
            "reason": "Guest lecture on Embedded Systems",
            "status": "APPROVED",
            "requested_by": "E&TC Coordinator",
            "reviewed_by": "HOD CSE"
        }
    ]
}

def _load_local_store():
    if not STORE_FILE.exists():
        _save_local_store(DEFAULT_STORE)
        return dict(DEFAULT_STORE)
    try:
        with open(STORE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure all keys exist
            for k, v in DEFAULT_STORE.items():
                if k not in data or (isinstance(data[k], list) and not data[k] and v):
                    data[k] = v
            return data
    except Exception:
        return dict(DEFAULT_STORE)

def _save_local_store(data):
    try:
        with open(STORE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving local store: {e}")

_memory_store = _load_local_store()

def is_configured() -> bool:
    """Check if valid Supabase credentials exist."""
    return bool(
        SUPABASE_URL 
        and SUPABASE_KEY 
        and not SUPABASE_URL.startswith("https://your-project")
        and not SUPABASE_KEY.startswith("your-")
    )

def get_client():
    global _client
    if not is_configured():
        return None
    if _client is None:
        try:
            from supabase import create_client
            _client = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception:
            _client = None
    return _client

# ---------------------------------------------------------------------------
# DEPARTMENTS
# ---------------------------------------------------------------------------
def get_all_departments():
    client = get_client()
    if client:
        try:
            res = client.table("departments").select("*").order("code").execute()
            if res.data:
                return res.data
        except Exception:
            pass
    return _memory_store.get("departments", [])

def upsert_department(record: dict):
    client = get_client()
    if client:
        try:
            res = client.table("departments").upsert(record).execute()
            if res.data:
                record = res.data[0]
        except Exception:
            pass
    depts = _memory_store.setdefault("departments", [])
    if "id" not in record or not record["id"]:
        record["id"] = max([d.get("id", 0) for d in depts] or [0]) + 1
        depts.append(record)
    else:
        for idx, d in enumerate(depts):
            if d.get("id") == record["id"] or d.get("code") == record.get("code"):
                depts[idx] = record
                break
        else:
            depts.append(record)
    _save_local_store(_memory_store)
    return record

def delete_department(dept_id: int):
    client = get_client()
    if client:
        try:
            client.table("departments").delete().eq("id", dept_id).execute()
        except Exception:
            pass
    _memory_store["departments"] = [d for d in _memory_store.get("departments", []) if d.get("id") != dept_id]
    _save_local_store(_memory_store)

# ---------------------------------------------------------------------------
# ACADEMIC STRUCTURE
# ---------------------------------------------------------------------------
def get_academic_structure(dept_code="CSE"):
    client = get_client()
    if client:
        try:
            q = client.table("academic_structure").select("*")
            if dept_code:
                q = q.eq("department_code", dept_code)
            res = q.execute()
            if res.data:
                return res.data
        except Exception:
            pass
    items = _memory_store.get("academic_structure", [])
    if dept_code:
        return [i for i in items if i.get("department_code") == dept_code]
    return items

def upsert_academic_structure(record: dict):
    client = get_client()
    if client:
        try:
            client.table("academic_structure").upsert(record).execute()
        except Exception:
            pass
    structs = _memory_store.setdefault("academic_structure", [])
    if "id" not in record or not record["id"]:
        record["id"] = max([s.get("id", 0) for s in structs] or [0]) + 1
        structs.append(record)
    else:
        for idx, s in enumerate(structs):
            if s.get("id") == record["id"]:
                structs[idx] = record
                break
        else:
            structs.append(record)
    _save_local_store(_memory_store)
    return record

# ---------------------------------------------------------------------------
# DIVISIONS & SECTIONS
# ---------------------------------------------------------------------------
def get_all_divisions(dept_code=None):
    client = get_client()
    if client:
        try:
            q = client.table("divisions").select("*").order("name")
            if dept_code:
                q = q.eq("department_code", dept_code)
            res = q.execute()
            if res.data:
                return res.data
        except Exception:
            pass
    divs = _memory_store.get("divisions", [])
    if dept_code:
        return [d for d in divs if d.get("department_code") == dept_code]
    return divs

def upsert_division(record: dict):
    client = get_client()
    if client:
        try:
            client.table("divisions").upsert(record).execute()
        except Exception:
            pass
    divs = _memory_store.setdefault("divisions", [])
    if "id" not in record or not record["id"]:
        record["id"] = max([d.get("id", 0) for d in divs] or [0]) + 1
        divs.append(record)
    else:
        for idx, d in enumerate(divs):
            if d.get("id") == record["id"]:
                divs[idx] = record
                break
        else:
            divs.append(record)
    
    # Also sync to sections table for backward compatibility
    upsert_section({"name": record.get("name"), "strength": record.get("strength", 60), "department": record.get("department_code", "CSE")})
    _save_local_store(_memory_store)
    return record

def insert_divisions(division_list: list):
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
    _save_local_store(_memory_store)

def delete_division(div_id: int):
    client = get_client()
    if client:
        try:
            client.table("divisions").delete().eq("id", div_id).execute()
        except Exception:
            pass
    _memory_store["divisions"] = [d for d in _memory_store.get("divisions", []) if d.get("id") != div_id]
    _save_local_store(_memory_store)

# ---------------------------------------------------------------------------
# BATCHES
# ---------------------------------------------------------------------------
def get_all_batches(division_name=None):
    client = get_client()
    if client:
        try:
            q = client.table("batches").select("*").order("name")
            if division_name:
                q = q.eq("division_name", division_name)
            res = q.execute()
            if res.data:
                return res.data
        except Exception:
            pass
    batches = _memory_store.get("batches", [])
    if division_name:
        return [b for b in batches if b.get("division_name") == division_name]
    return batches

def upsert_batch(record: dict):
    client = get_client()
    if client:
        try:
            client.table("batches").upsert(record).execute()
        except Exception:
            pass
    batches = _memory_store.setdefault("batches", [])
    if "id" not in record or not record["id"]:
        record["id"] = max([b.get("id", 0) for b in batches] or [0]) + 1
        batches.append(record)
    else:
        for idx, b in enumerate(batches):
            if b.get("id") == record["id"]:
                batches[idx] = record
                break
        else:
            batches.append(record)
    _save_local_store(_memory_store)
    return record

def insert_batches(batch_list: list):
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
    _save_local_store(_memory_store)

def delete_batch(batch_id: int):
    client = get_client()
    if client:
        try:
            client.table("batches").delete().eq("id", batch_id).execute()
        except Exception:
            pass
    _memory_store["batches"] = [b for b in _memory_store.get("batches", []) if b.get("id") != batch_id]
    _save_local_store(_memory_store)

# ---------------------------------------------------------------------------
# SECTIONS (BACKWARD COMPATIBILITY)
# ---------------------------------------------------------------------------
def get_all_sections():
    client = get_client()
    if client:
        try:
            res = client.table("sections").select("*").order("name").execute()
            if res.data:
                return res.data
        except Exception:
            pass
    return _memory_store.get("sections", [])

def insert_sections(section_list: list):
    client = get_client()
    if client:
        try:
            client.table("sections").delete().neq("id", 0).execute()
            if section_list:
                cleaned = [{"name": s.get("name"), "strength": s.get("strength", 60)} for s in section_list]
                client.table("sections").insert(cleaned).execute()
        except Exception:
            pass
    _memory_store["sections"] = list(section_list)
    _save_local_store(_memory_store)

def upsert_section(record: dict):
    client = get_client()
    if client:
        try:
            cleaned = {"name": record.get("name"), "strength": record.get("strength", 60)}
            if "id" in record and record["id"]:
                cleaned["id"] = record["id"]
            client.table("sections").upsert(cleaned).execute()
        except Exception:
            pass
    secs = _memory_store.setdefault("sections", [])
    for idx, s in enumerate(secs):
        if s.get("name") == record.get("name"):
            secs[idx] = record
            break
    else:
        if "id" not in record or not record["id"]:
            record["id"] = max([s.get("id", 0) for s in secs] or [0]) + 1
        secs.append(record)
    _save_local_store(_memory_store)

def delete_section(sec_id: int):
    client = get_client()
    if client:
        try:
            client.table("sections").delete().eq("id", sec_id).execute()
        except Exception:
            pass
    _memory_store["sections"] = [s for s in _memory_store.get("sections", []) if s.get("id") != sec_id]
    _save_local_store(_memory_store)

# ---------------------------------------------------------------------------
# ROOMS & RESOURCES
# ---------------------------------------------------------------------------
def get_all_rooms(dept_code=None):
    client = get_client()
    supa_rooms = []
    if client:
        try:
            res = client.table("rooms").select("*").order("name").execute()
            supa_rooms = res.data or []
        except Exception:
            pass

    # Merge Supabase rooms with local metadata store
    local_rooms = {r["name"]: r for r in _memory_store.get("rooms", [])}
    merged = []
    
    if supa_rooms:
        for sr in supa_rooms:
            name = sr.get("name")
            extra = local_rooms.get(name, {})
            item = {
                "id": sr.get("id"),
                "name": name,
                "type": sr.get("type", "Classroom"),
                "capacity": sr.get("capacity", 60),
                "department": sr.get("department") or extra.get("department", "CSE"),
                "lab_type": sr.get("lab_type") or extra.get("lab_type", "Computer Lab" if sr.get("type") == "Lab" else ""),
                "num_pcs": sr.get("num_pcs") if sr.get("num_pcs") is not None else extra.get("num_pcs", 35 if sr.get("type") == "Lab" else 0),
                "equipment": sr.get("equipment") or extra.get("equipment", "Projector, LAN"),
                "is_reserved": sr.get("is_reserved", extra.get("is_reserved", False)),
                "reservation_reason": sr.get("reservation_reason") or extra.get("reservation_reason", "")
            }
            merged.append(item)
    else:
        merged = list(_memory_store.get("rooms", []))

    if dept_code:
        return [r for r in merged if r.get("department") == dept_code]
    return merged

def upsert_room(record: dict):
    client = get_client()
    if client:
        try:
            # First try with all columns
            client.table("rooms").upsert(record).execute()
        except Exception:
            try:
                # Fallback to core columns if extra columns not in Supabase schema yet
                core_record = {
                    "name": record.get("name"),
                    "type": record.get("type"),
                    "capacity": record.get("capacity", 60)
                }
                if "id" in record and record["id"]:
                    core_record["id"] = record["id"]
                client.table("rooms").upsert(core_record).execute()
            except Exception as e:
                print(f"Supabase upsert room error: {e}")

    rooms = _memory_store.setdefault("rooms", [])
    if "id" not in record or not record["id"]:
        record["id"] = max([r.get("id", 0) for r in rooms] or [0]) + 1
        rooms.append(record)
    else:
        for idx, r in enumerate(rooms):
            if r.get("id") == record["id"] or r.get("name") == record.get("name"):
                rooms[idx] = record
                break
        else:
            rooms.append(record)
    _save_local_store(_memory_store)
    return record

def insert_rooms(room_list: list):
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
    _save_local_store(_memory_store)

def delete_room(room_id: int):
    client = get_client()
    if client:
        try:
            client.table("rooms").delete().eq("id", room_id).execute()
        except Exception:
            pass
    _memory_store["rooms"] = [r for r in _memory_store.get("rooms", []) if r.get("id") != room_id]
    _save_local_store(_memory_store)

# ---------------------------------------------------------------------------
# RESOURCE CONFIGURATION & RESERVATION (HOD REQUIREMENT)
# ---------------------------------------------------------------------------
def get_resource_config(dept_code="CSE"):
    client = get_client()
    if client:
        try:
            res = client.table("resource_config").select("*").eq("department", dept_code).execute()
            if res.data:
                return res.data[0]
        except Exception:
            pass
    configs = _memory_store.get("resource_config", [])
    for c in configs:
        if c.get("department") == dept_code:
            return c
    default_cfg = {
        "department": dept_code,
        "reserved_classrooms_count": 1,
        "reserved_labs_count": 1,
        "student_pc_ratio": "1:1"
    }
    configs.append(default_cfg)
    _save_local_store(_memory_store)
    return default_cfg

def upsert_resource_config(record: dict):
    client = get_client()
    if client:
        try:
            client.table("resource_config").upsert(record).execute()
        except Exception:
            pass
    configs = _memory_store.setdefault("resource_config", [])
    for idx, c in enumerate(configs):
        if c.get("department") == record.get("department"):
            configs[idx] = record
            break
    else:
        if "id" not in record:
            record["id"] = len(configs) + 1
        configs.append(record)
    _save_local_store(_memory_store)
    return record

# ---------------------------------------------------------------------------
# FACULTY
# ---------------------------------------------------------------------------
def get_all_faculty(dept_code=None):
    client = get_client()
    supa_fac = []
    if client:
        try:
            res = client.table("faculty").select("*").order("name").execute()
            supa_fac = res.data or []
        except Exception:
            pass

    local_fac = {f.get("code") or f.get("name"): f for f in _memory_store.get("faculty", [])}
    merged = []
    
    if supa_fac:
        for sf in supa_fac:
            code = sf.get("code")
            extra = local_fac.get(code, local_fac.get(sf.get("name"), {}))
            merged.append({
                "id": sf.get("id"),
                "name": sf.get("name"),
                "code": sf.get("code") or extra.get("code", "FAC"),
                "designation": sf.get("designation") or extra.get("designation", "Assistant Professor"),
                "department": sf.get("department") or extra.get("department", "CSE"),
                "subjects": sf.get("subjects") or extra.get("subjects", []),
                "available_from": sf.get("available_from") or "09:00",
                "available_to": sf.get("available_to") or "17:00",
                "preferred_time": sf.get("preferred_time") or "Any",
                "blocked_slots": sf.get("blocked_slots") or extra.get("blocked_slots", []),
                "max_load": sf.get("max_load") or 20
            })
    else:
        merged = list(_memory_store.get("faculty", []))

    if dept_code:
        return [f for f in merged if f.get("department") == dept_code]
    return merged

def upsert_faculty(record: dict):
    client = get_client()
    if client:
        try:
            client.table("faculty").upsert(record).execute()
        except Exception:
            try:
                # Core columns fallback
                core = {
                    "name": record.get("name"),
                    "code": record.get("code"),
                    "subjects": record.get("subjects", []),
                    "available_from": record.get("available_from", "09:00"),
                    "available_to": record.get("available_to", "17:00"),
                    "preferred_time": record.get("preferred_time", "Any"),
                    "max_load": record.get("max_load", 20)
                }
                if "id" in record and record["id"]:
                    core["id"] = record["id"]
                client.table("faculty").upsert(core).execute()
            except Exception as e:
                print(f"Supabase upsert faculty error: {e}")

    fac = _memory_store.setdefault("faculty", [])
    if "id" not in record or not record["id"]:
        record["id"] = max([f.get("id", 0) for f in fac] or [0]) + 1
        fac.append(record)
    else:
        for idx, f in enumerate(fac):
            if f.get("id") == record["id"] or f.get("code") == record.get("code"):
                fac[idx] = record
                break
        else:
            fac.append(record)
    _save_local_store(_memory_store)
    return record

def insert_faculty(faculty_list: list):
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
    _save_local_store(_memory_store)

def delete_faculty(faculty_id: int):
    client = get_client()
    if client:
        try:
            client.table("faculty").delete().eq("id", faculty_id).execute()
        except Exception:
            pass
    _memory_store["faculty"] = [f for f in _memory_store.get("faculty", []) if f.get("id") != faculty_id]
    _save_local_store(_memory_store)

# ---------------------------------------------------------------------------
# SUBJECTS
# ---------------------------------------------------------------------------
def get_all_subjects(dept_code=None):
    client = get_client()
    supa_sub = []
    if client:
        try:
            res = client.table("subjects").select("*").order("name").execute()
            supa_sub = res.data or []
        except Exception:
            pass

    local_sub = {s["name"]: s for s in _memory_store.get("subjects", [])}
    merged = []
    
    if supa_sub:
        for ss in supa_sub:
            name = ss.get("name")
            extra = local_sub.get(name, {})
            merged.append({
                "id": ss.get("id"),
                "name": name,
                "code": ss.get("code") or extra.get("code", ""),
                "department": ss.get("department") or extra.get("department", "CSE"),
                "year": ss.get("year") or extra.get("year", "Second Year"),
                "semester": ss.get("semester") or extra.get("semester", "Semester III"),
                "lectures_per_week": ss.get("lectures_per_week", 3),
                "labs_per_week": ss.get("labs_per_week", 0),
                "requires_lab": ss.get("requires_lab", False),
                "lab_type": ss.get("lab_type") or extra.get("lab_type", "Computer Lab" if ss.get("requires_lab") else ""),
                "student_pc_ratio": ss.get("student_pc_ratio", extra.get("student_pc_ratio", 1.0))
            })
    else:
        merged = list(_memory_store.get("subjects", []))

    if dept_code:
        return [s for s in merged if s.get("department") == dept_code]
    return merged

def upsert_subject(record: dict):
    client = get_client()
    if client:
        try:
            client.table("subjects").upsert(record).execute()
        except Exception:
            try:
                core = {
                    "name": record.get("name"),
                    "code": record.get("code"),
                    "lectures_per_week": record.get("lectures_per_week", 3),
                    "labs_per_week": record.get("labs_per_week", 0),
                    "requires_lab": record.get("requires_lab", False)
                }
                if "id" in record and record["id"]:
                    core["id"] = record["id"]
                client.table("subjects").upsert(core).execute()
            except Exception as e:
                print(f"Supabase upsert subject error: {e}")

    subs = _memory_store.setdefault("subjects", [])
    if "id" not in record or not record["id"]:
        record["id"] = max([s.get("id", 0) for s in subs] or [0]) + 1
        subs.append(record)
    else:
        for idx, s in enumerate(subs):
            if s.get("id") == record["id"] or s.get("name") == record.get("name"):
                subs[idx] = record
                break
        else:
            subs.append(record)
    _save_local_store(_memory_store)
    return record

def insert_subjects(subject_list: list):
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
    _save_local_store(_memory_store)

def delete_subject(subject_id: int):
    client = get_client()
    if client:
        try:
            client.table("subjects").delete().eq("id", subject_id).execute()
        except Exception:
            pass
    _memory_store["subjects"] = [s for s in _memory_store.get("subjects", []) if s.get("id") != subject_id]
    _save_local_store(_memory_store)

# ---------------------------------------------------------------------------
# TIME SLOTS
# ---------------------------------------------------------------------------
def get_time_slots():
    client = get_client()
    if client:
        try:
            res = client.table("time_slots").select("*").order("order_index").execute()
            if res.data:
                return res.data
        except Exception:
            pass
    return _memory_store.get("time_slots", DEFAULT_STORE["time_slots"])

def save_time_slots(slots_list: list):
    client = get_client()
    if client:
        try:
            client.table("time_slots").delete().neq("id", 0).execute()
            client.table("time_slots").insert(slots_list).execute()
        except Exception:
            pass
    _memory_store["time_slots"] = list(slots_list)
    _save_local_store(_memory_store)

DEFAULT_TIME_SETTINGS = {
    "start_time": "09:00",
    "period_duration": 60,
    "morning_periods": 2,
    "short_break_1_duration": 10,
    "pre_lunch_periods": 2,
    "lunch_duration": 40,
    "afternoon_periods": 2,
    "short_break_2_duration": 10,
    "final_periods": 1,
    "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
}

def get_time_settings():
    return _memory_store.get("time_settings", DEFAULT_TIME_SETTINGS)

def save_time_settings(settings: dict):
    _memory_store["time_settings"] = dict(settings)
    _save_local_store(_memory_store)
    return _memory_store["time_settings"]

# ---------------------------------------------------------------------------
# TIMETABLE & VERSIONS
# ---------------------------------------------------------------------------
def get_timetable(version_id=None, department=None):
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
    _save_local_store(_memory_store)

# ---------------------------------------------------------------------------
# RESOURCE SHARING REQUESTS (CROSS-DEPARTMENT WORKFLOW)
# ---------------------------------------------------------------------------
def get_resource_sharing_requests():
    client = get_client()
    if client:
        try:
            res = client.table("resource_sharing_requests").select("*").order("created_at").execute()
            if res.data:
                return res.data
        except Exception:
            pass
    return _memory_store.get("resource_sharing_requests", DEFAULT_STORE["resource_sharing_requests"])

def create_resource_sharing_request(record: dict):
    record["status"] = "PENDING"
    client = get_client()
    if client:
        try:
            res = client.table("resource_sharing_requests").insert(record).execute()
            if res.data:
                record = res.data[0]
        except Exception:
            pass
    reqs = _memory_store.setdefault("resource_sharing_requests", [])
    if "id" not in record:
        record["id"] = max([r.get("id", 0) for r in reqs] or [0]) + 1
    reqs.append(record)
    _save_local_store(_memory_store)
    return record

def update_resource_sharing_request(req_id: int, status: str, reviewed_by: str = "HOD"):
    client = get_client()
    if client:
        try:
            client.table("resource_sharing_requests").update({"status": status, "reviewed_by": reviewed_by}).eq("id", req_id).execute()
        except Exception:
            pass
    for r in _memory_store.get("resource_sharing_requests", []):
        if r.get("id") == req_id:
            r["status"] = status
            r["reviewed_by"] = reviewed_by
            break
    _save_local_store(_memory_store)
