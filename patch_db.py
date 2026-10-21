# patch_db.py
import json

# 1. Update data_store.json to exactly 10 slots
dyp_slots = [
    {"period": "09:00-10:00", "type": "TEACHING",   "is_morning": True,  "start_time": "09:00", "end_time": "10:00", "order_index": 1},
    {"period": "10:00-11:00", "type": "TEACHING",   "is_morning": True,  "start_time": "10:00", "end_time": "11:00", "order_index": 2},
    {"period": "11:00-11:10", "type": "SHORT_BREAK", "is_morning": True,  "start_time": "11:00", "end_time": "11:10", "order_index": 3},
    {"period": "11:10-12:10", "type": "TEACHING",   "is_morning": True,  "start_time": "11:10", "end_time": "12:10", "order_index": 4},
    {"period": "12:10-01:10", "type": "TEACHING",   "is_morning": True,  "start_time": "12:10", "end_time": "13:10", "order_index": 5},
    {"period": "01:10-01:50", "type": "LUNCH",      "is_morning": False, "start_time": "13:10", "end_time": "13:50", "order_index": 6},
    {"period": "01:50-02:50", "type": "TEACHING",   "is_morning": False, "start_time": "13:50", "end_time": "14:50", "order_index": 7},
    {"period": "02:50-03:50", "type": "TEACHING",   "is_morning": False, "start_time": "14:50", "end_time": "15:50", "order_index": 8},
    {"period": "03:50-04:00", "type": "SHORT_BREAK", "is_morning": False, "start_time": "15:50", "end_time": "16:00", "order_index": 9},
    {"period": "04:00-05:00", "type": "TEACHING",   "is_morning": False, "start_time": "16:00", "end_time": "17:00", "order_index": 10},
]

with open("backend/data_store.json", "r", encoding="utf-8") as f:
    ds = json.load(f)

ds["time_slots"] = dyp_slots

with open("backend/data_store.json", "w", encoding="utf-8") as f:
    json.dump(ds, f, indent=4)

print("[OK] data_store.json set to 10 unique slots!")

# 2. Update backend/db.py
with open("backend/db.py", "r", encoding="utf-8") as f:
    code = f.read()

# Replace time_slots in DEFAULT_STORE
old_default_slots = '''    "time_slots": [
        {"period": "09:00-10:00", "type": "TEACHING", "is_morning": True, "start_time": "09:00", "end_time": "10:00", "order_index": 1},
        {"period": "10:00-11:00", "type": "TEACHING", "is_morning": True, "start_time": "10:00", "end_time": "11:00", "order_index": 2},
        {"period": "11:00-11:15", "type": "SHORT_BREAK", "is_morning": True, "start_time": "11:00", "end_time": "11:15", "order_index": 3},
        {"period": "11:15-12:15", "type": "TEACHING", "is_morning": True, "start_time": "11:15", "end_time": "12:15", "order_index": 4},
        {"period": "12:15-13:00", "type": "LUNCH", "is_morning": False, "start_time": "12:15", "end_time": "13:00", "order_index": 5},
        {"period": "13:00-14:00", "type": "TEACHING", "is_morning": False, "start_time": "13:00", "end_time": "14:00", "order_index": 6},
        {"period": "14:00-15:00", "type": "TEACHING", "is_morning": False, "start_time": "14:00", "end_time": "15:00", "order_index": 7},
        {"period": "15:00-15:15", "type": "SHORT_BREAK", "is_morning": False, "start_time": "15:00", "end_time": "15:15", "order_index": 8},
        {"period": "15:15-16:15", "type": "TEACHING", "is_morning": False, "start_time": "15:15", "end_time": "16:15", "order_index": 9}
    ],'''

new_default_slots = '''    "time_slots": [
        {"period": "09:00-10:00", "type": "TEACHING",   "is_morning": True,  "start_time": "09:00", "end_time": "10:00", "order_index": 1},
        {"period": "10:00-11:00", "type": "TEACHING",   "is_morning": True,  "start_time": "10:00", "end_time": "11:00", "order_index": 2},
        {"period": "11:00-11:10", "type": "SHORT_BREAK", "is_morning": True,  "start_time": "11:00", "end_time": "11:10", "order_index": 3},
        {"period": "11:10-12:10", "type": "TEACHING",   "is_morning": True,  "start_time": "11:10", "end_time": "12:10", "order_index": 4},
        {"period": "12:10-01:10", "type": "TEACHING",   "is_morning": True,  "start_time": "12:10", "end_time": "13:10", "order_index": 5},
        {"period": "01:10-01:50", "type": "LUNCH",      "is_morning": False, "start_time": "13:10", "end_time": "13:50", "order_index": 6},
        {"period": "01:50-02:50", "type": "TEACHING",   "is_morning": False, "start_time": "13:50", "end_time": "14:50", "order_index": 7},
        {"period": "02:50-03:50", "type": "TEACHING",   "is_morning": False, "start_time": "14:50", "end_time": "15:50", "order_index": 8},
        {"period": "03:50-04:00", "type": "SHORT_BREAK", "is_morning": False, "start_time": "15:50", "end_time": "16:00", "order_index": 9},
        {"period": "04:00-05:00", "type": "TEACHING",   "is_morning": False, "start_time": "16:00", "end_time": "17:00", "order_index": 10},
    ],'''

if old_default_slots in code:
    code = code.replace(old_default_slots, new_default_slots)

# Add _deduplicate_slots and update get_time_slots and save_time_slots
old_time_funcs = '''def get_time_slots():
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
    _save_local_store(_memory_store)'''

new_time_funcs = '''OFFICIAL_DYPATIL_SLOTS = [
    {"period": "09:00-10:00", "type": "TEACHING",   "is_morning": True,  "start_time": "09:00", "end_time": "10:00", "order_index": 1},
    {"period": "10:00-11:00", "type": "TEACHING",   "is_morning": True,  "start_time": "10:00", "end_time": "11:00", "order_index": 2},
    {"period": "11:00-11:10", "type": "SHORT_BREAK", "is_morning": True,  "start_time": "11:00", "end_time": "11:10", "order_index": 3},
    {"period": "11:10-12:10", "type": "TEACHING",   "is_morning": True,  "start_time": "11:10", "end_time": "12:10", "order_index": 4},
    {"period": "12:10-01:10", "type": "TEACHING",   "is_morning": True,  "start_time": "12:10", "end_time": "13:10", "order_index": 5},
    {"period": "01:10-01:50", "type": "LUNCH",      "is_morning": False, "start_time": "13:10", "end_time": "13:50", "order_index": 6},
    {"period": "01:50-02:50", "type": "TEACHING",   "is_morning": False, "start_time": "13:50", "end_time": "14:50", "order_index": 7},
    {"period": "02:50-03:50", "type": "TEACHING",   "is_morning": False, "start_time": "14:50", "end_time": "15:50", "order_index": 8},
    {"period": "03:50-04:00", "type": "SHORT_BREAK", "is_morning": False, "start_time": "15:50", "end_time": "16:00", "order_index": 9},
    {"period": "04:00-05:00", "type": "TEACHING",   "is_morning": False, "start_time": "16:00", "end_time": "17:00", "order_index": 10},
]

def _deduplicate_slots(slots_list):
    if not slots_list:
        return list(OFFICIAL_DYPATIL_SLOTS)
    seen = set()
    unique = []
    for s in slots_list:
        p = s.get("period") or f"{s.get('start_time')}-{s.get('end_time')}"
        if not p or p in seen:
            continue
        seen.add(p)
        unique.append(dict(s))
    if len(unique) <= 2:
        return list(OFFICIAL_DYPATIL_SLOTS)
    for idx, s in enumerate(unique, start=1):
        s["order_index"] = idx
    return unique

def get_time_slots():
    client = get_client()
    if client:
        try:
            res = client.table("time_slots").select("*").order("order_index").execute()
            if res.data:
                return _deduplicate_slots(res.data)
        except Exception:
            pass
    raw = _memory_store.get("time_slots", DEFAULT_STORE.get("time_slots", OFFICIAL_DYPATIL_SLOTS))
    return _deduplicate_slots(raw)

def save_time_slots(slots_list: list):
    cleaned = _deduplicate_slots(slots_list)
    client = get_client()
    if client:
        try:
            client.table("time_slots").delete().neq("id", 0).execute()
            client.table("time_slots").insert(cleaned).execute()
        except Exception:
            pass
    _memory_store["time_slots"] = list(cleaned)
    _save_local_store(_memory_store)'''

assert old_time_funcs in code, "old_time_funcs not found"
code = code.replace(old_time_funcs, new_time_funcs)

with open("backend/db.py", "w", encoding="utf-8") as f:
    f.write(code)

print("[OK] backend/db.py updated with slot deduplication!")

