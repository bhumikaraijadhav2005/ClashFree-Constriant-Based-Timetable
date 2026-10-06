# backend/db.py
# Handles data storage with graceful fallback:
# 1. Supabase PostgreSQL when SUPABASE_URL and SUPABASE_KEY are provided.
# 2. In-Memory store when Supabase credentials are not yet set up,
#    allowing immediate testing without breaking!

import os
from pathlib import Path
from dotenv import load_dotenv

root_dir = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=root_dir / ".env")
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

_client = None

# In-memory mock store for instant local testing
_memory_store = {
    "faculty": [],
    "rooms": [],
    "subjects": [],
    "sections": [],
    "timetable": []
}

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
        from supabase import create_client
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client

# ---------------------------------------------------------------------------
# Faculty
# ---------------------------------------------------------------------------
def get_all_faculty():
    client = get_client()
    if client:
        res = client.table("faculty").select("*").order("name").execute()
        return res.data or []
    return _memory_store["faculty"]

def insert_faculty(faculty_list: list):
    client = get_client()
    if client:
        client.table("faculty").delete().neq("id", 0).execute()
        if faculty_list:
            client.table("faculty").insert(faculty_list).execute()
    else:
        for idx, f in enumerate(faculty_list):
            f["id"] = idx + 1
        _memory_store["faculty"] = list(faculty_list)

def upsert_faculty(record: dict):
    client = get_client()
    if client:
        return client.table("faculty").upsert(record).execute()
    if "id" not in record or not record["id"]:
        record["id"] = len(_memory_store["faculty"]) + 1
        _memory_store["faculty"].append(record)
    else:
        for idx, f in enumerate(_memory_store["faculty"]):
            if f["id"] == record["id"]:
                _memory_store["faculty"][idx] = record
                break
    return type("Obj", (), {"data": [record]})()

def delete_faculty(faculty_id: int):
    client = get_client()
    if client:
        client.table("faculty").delete().eq("id", faculty_id).execute()
    else:
        _memory_store["faculty"] = [f for f in _memory_store["faculty"] if f.get("id") != faculty_id]

# ---------------------------------------------------------------------------
# Rooms
# ---------------------------------------------------------------------------
def get_all_rooms():
    client = get_client()
    if client:
        res = client.table("rooms").select("*").order("name").execute()
        return res.data or []
    return _memory_store["rooms"]

def insert_rooms(room_list: list):
    client = get_client()
    if client:
        client.table("rooms").delete().neq("id", 0).execute()
        if room_list:
            client.table("rooms").insert(room_list).execute()
    else:
        for idx, r in enumerate(room_list):
            r["id"] = idx + 1
        _memory_store["rooms"] = list(room_list)

def upsert_room(record: dict):
    client = get_client()
    if client:
        return client.table("rooms").upsert(record).execute()
    if "id" not in record or not record["id"]:
        record["id"] = len(_memory_store["rooms"]) + 1
        _memory_store["rooms"].append(record)
    else:
        for idx, r in enumerate(_memory_store["rooms"]):
            if r["id"] == record["id"]:
                _memory_store["rooms"][idx] = record
                break
    return type("Obj", (), {"data": [record]})()

def delete_room(room_id: int):
    client = get_client()
    if client:
        client.table("rooms").delete().eq("id", room_id).execute()
    else:
        _memory_store["rooms"] = [r for r in _memory_store["rooms"] if r.get("id") != room_id]

# ---------------------------------------------------------------------------
# Subjects
# ---------------------------------------------------------------------------
def get_all_subjects():
    client = get_client()
    if client:
        res = client.table("subjects").select("*").order("name").execute()
        return res.data or []
    return _memory_store["subjects"]

def insert_subjects(subject_list: list):
    client = get_client()
    if client:
        client.table("subjects").delete().neq("id", 0).execute()
        if subject_list:
            client.table("subjects").insert(subject_list).execute()
    else:
        for idx, s in enumerate(subject_list):
            s["id"] = idx + 1
        _memory_store["subjects"] = list(subject_list)

def upsert_subject(record: dict):
    client = get_client()
    if client:
        return client.table("subjects").upsert(record).execute()
    if "id" not in record or not record["id"]:
        record["id"] = len(_memory_store["subjects"]) + 1
        _memory_store["subjects"].append(record)
    else:
        for idx, s in enumerate(_memory_store["subjects"]):
            if s["id"] == record["id"]:
                _memory_store["subjects"][idx] = record
                break
    return type("Obj", (), {"data": [record]})()

def delete_subject(subject_id: int):
    client = get_client()
    if client:
        client.table("subjects").delete().eq("id", subject_id).execute()
    else:
        _memory_store["subjects"] = [s for s in _memory_store["subjects"] if s.get("id") != subject_id]

# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------
def get_all_sections():
    client = get_client()
    if client:
        res = client.table("sections").select("*").order("name").execute()
        return res.data or []
    return _memory_store["sections"]

def insert_sections(section_list: list):
    client = get_client()
    if client:
        client.table("sections").delete().neq("id", 0).execute()
        if section_list:
            client.table("sections").insert(section_list).execute()
    else:
        for idx, sec in enumerate(section_list):
            sec["id"] = idx + 1
        _memory_store["sections"] = list(section_list)

def upsert_section(record: dict):
    client = get_client()
    if client:
        return client.table("sections").upsert(record).execute()
    if "id" not in record or not record["id"]:
        record["id"] = len(_memory_store["sections"]) + 1
        _memory_store["sections"].append(record)
    else:
        for idx, sec in enumerate(_memory_store["sections"]):
            if sec["id"] == record["id"]:
                _memory_store["sections"][idx] = record
                break
    return type("Obj", (), {"data": [record]})()

def delete_section(section_id: int):
    client = get_client()
    if client:
        client.table("sections").delete().eq("id", section_id).execute()
    else:
        _memory_store["sections"] = [s for s in _memory_store["sections"] if s.get("id") != section_id]

# ---------------------------------------------------------------------------
# Timetable
# ---------------------------------------------------------------------------
def get_timetable():
    client = get_client()
    if client:
        res = client.table("timetable").select("*").order("day_order").order("period").execute()
        return res.data or []
    return _memory_store["timetable"]

def save_timetable(rows: list):
    client = get_client()
    if client:
        client.table("timetable").delete().neq("id", 0).execute()
        if rows:
            client.table("timetable").insert(rows).execute()
    else:
        _memory_store["timetable"] = list(rows)

def clear_timetable():
    client = get_client()
    if client:
        client.table("timetable").delete().neq("id", 0).execute()
    else:
        _memory_store["timetable"] = []
