import json
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
store_path = project_root / "backend" / "data_store.json"
with store_path.open("r", encoding="utf-8") as f:
    store = json.load(f)

# Ensure departments exist
existing_depts = {d.get("code"): d for d in store.get("departments", [])}
depts_to_add = [
    {"id": 1, "code": "CSE", "name": "Computer Science & Engineering"},
    {"id": 2, "code": "ECE", "name": "Electronics & Telecommunication Engineering"},
    {"id": 3, "code": "MECH", "name": "Mechanical Engineering"},
    {"id": 4, "code": "CIVIL", "name": "Civil Engineering"}
]
for d in depts_to_add:
    existing_depts[d["code"]] = d
store["departments"] = list(existing_depts.values())

# Shared College Resources
shared_rooms = [
    {"id": 101, "name": "AUDITORIUM", "type": "Classroom", "capacity": 300, "department": "COLLEGE", "is_shared": True, "is_active": True, "equipment": "Projector, Audio, Stage"},
    {"id": 102, "name": "CENTRAL-LAB", "type": "Lab", "capacity": 80, "department": "COLLEGE", "is_shared": True, "is_active": True, "num_pcs": 80, "equipment": "High-End Workstations"}
]
rooms = store.setdefault("rooms", [])
for sr in shared_rooms:
    if not any(r.get("name") == sr["name"] for r in rooms):
        rooms.append(sr)

# ECE Resources
ece_rooms = [
    {"id": 201, "name": "CR-E1", "type": "Classroom", "capacity": 65, "department": "ECE", "is_shared": False, "is_active": True, "equipment": "Projector"},
    {"id": 202, "name": "CR-E2", "type": "Classroom", "capacity": 65, "department": "ECE", "is_shared": False, "is_active": True, "equipment": "-"},
    {"id": 203, "name": "CR-E3", "type": "Classroom", "capacity": 65, "department": "ECE", "is_shared": False, "is_active": True, "equipment": "-"},
    {"id": 204, "name": "LAB-E1", "type": "Lab", "capacity": 35, "department": "ECE", "is_shared": False, "is_active": True, "num_pcs": 35, "equipment": "Computer"},
    {"id": 205, "name": "LAB-E2", "type": "Lab", "capacity": 35, "department": "ECE", "is_shared": False, "is_active": True, "num_pcs": 35, "equipment": "Computer"}
]
for r in ece_rooms:
    if not any(x.get("name") == r["name"] for x in rooms):
        rooms.append(r)

# MECH Resources
mech_rooms = [
    {"id": 301, "name": "CR-M1", "type": "Classroom", "capacity": 65, "department": "MECH", "is_shared": False, "is_active": True, "equipment": "Projector"},
    {"id": 302, "name": "CR-M2", "type": "Classroom", "capacity": 65, "department": "MECH", "is_shared": False, "is_active": True, "equipment": "-"},
    {"id": 303, "name": "LAB-M1", "type": "Lab", "capacity": 35, "department": "MECH", "is_shared": False, "is_active": True, "num_pcs": 35, "equipment": "Computer"},
    {"id": 304, "name": "LAB-M2", "type": "Lab", "capacity": 35, "department": "MECH", "is_shared": False, "is_active": True, "num_pcs": 35, "equipment": "Computer"}
]
for r in mech_rooms:
    if not any(x.get("name") == r["name"] for x in rooms):
        rooms.append(r)

# ECE Faculty
ece_faculty = [
    {"id": 201, "name": "Dr. R. S. Deshmukh", "code": "RSD", "department": "ECE", "designation": "Professor & Head", "max_load": 16, "preference": "Morning", "availability": "Mon-Fri 9:00 AM-4:00 PM", "subjects": ["Digital Communication"]},
    {"id": 202, "name": "Prof. A. P. Joshi", "code": "APJ", "department": "ECE", "designation": "Assistant Professor", "max_load": 18, "preference": "Morning", "availability": "Mon-Fri 9:00 AM-1:00 PM", "subjects": ["Digital Communication Lab", "Signals & Systems"]},
    {"id": 203, "name": "Prof. S. M. Kulkarni", "code": "SMK", "department": "ECE", "designation": "Assistant Professor", "max_load": 18, "preference": "Afternoon", "availability": "Mon-Fri 10:00 AM-4:00 PM", "subjects": ["Electronic Devices", "Electronic Devices Lab"]},
    {"id": 204, "name": "Prof. N. V. Patil", "code": "NVP", "department": "ECE", "designation": "Assistant Professor", "max_load": 16, "preference": "Morning", "availability": "Mon-Fri 9:00 AM-2:00 PM", "subjects": ["Control Systems", "VLSI Design"]}
]
faculty = store.setdefault("faculty", [])
for ef in ece_faculty:
    if not any(x.get("code") == ef["code"] for x in faculty):
        faculty.append(ef)

# MECH Faculty
mech_faculty = [
    {"id": 301, "name": "Dr. P. B. Mane", "code": "PBM", "department": "MECH", "designation": "Professor & Head", "max_load": 16, "preference": "Morning", "availability": "Mon-Fri 9:00 AM-4:00 PM", "subjects": ["Thermodynamics"]},
    {"id": 302, "name": "Prof. K. T. Shinde", "code": "KTS", "department": "MECH", "designation": "Assistant Professor", "max_load": 18, "preference": "Morning", "availability": "Mon-Fri 9:00 AM-1:00 PM", "subjects": ["Thermodynamics Lab", "Fluid Mechanics"]},
    {"id": 303, "name": "Prof. M. R. Gaikwad", "code": "MRG", "department": "MECH", "designation": "Assistant Professor", "max_load": 18, "preference": "Afternoon", "availability": "Mon-Fri 10:00 AM-4:00 PM", "subjects": ["Theory of Machines", "Fluid Mechanics Lab"]},
    {"id": 304, "name": "Prof. S. D. Jadhav", "code": "SDJ", "department": "MECH", "designation": "Assistant Professor", "max_load": 16, "preference": "Morning", "availability": "Mon-Fri 9:00 AM-2:00 PM", "subjects": ["Manufacturing Processes"]}
]
for mf in mech_faculty:
    if not any(x.get("code") == mf["code"] for x in faculty):
        faculty.append(mf)

# ECE Divisions
divisions = store.setdefault("divisions", [])
ece_divs = [
    {"id": 201, "name": "A", "division": "A", "department_code": "ECE", "department": "ECE", "year": "Year 2", "semester": "Semester 3", "strength": 60, "academic_year": "2026-2027", "display_name": "Year 2 Div A"},
    {"id": 202, "name": "B", "division": "B", "department_code": "ECE", "department": "ECE", "year": "Year 2", "semester": "Semester 3", "strength": 60, "academic_year": "2026-2027", "display_name": "Year 2 Div B"}
]
for ed in ece_divs:
    if not any(x.get("department_code") == "ECE" and x.get("name") == ed["name"] for x in divisions):
        divisions.append(ed)

# MECH Divisions
mech_divs = [
    {"id": 301, "name": "A", "division": "A", "department_code": "MECH", "department": "MECH", "year": "Year 2", "semester": "Semester 3", "strength": 60, "academic_year": "2026-2027", "display_name": "Year 2 Div A"}
]
for md in mech_divs:
    if not any(x.get("department_code") == "MECH" and x.get("name") == md["name"] for x in divisions):
        divisions.append(md)

# ECE Batches
batches = store.setdefault("batches", [])
ece_batches = [
    {"id": 201, "name": "A1", "division_name": "A", "department_code": "ECE", "strength": 30},
    {"id": 202, "name": "A2", "division_name": "A", "department_code": "ECE", "strength": 30},
    {"id": 203, "name": "B1", "division_name": "B", "department_code": "ECE", "strength": 30},
    {"id": 204, "name": "B2", "division_name": "B", "department_code": "ECE", "strength": 30}
]
for eb in ece_batches:
    if not any(x.get("department_code") == "ECE" and x.get("name") == eb["name"] and x.get("division_name") == eb["division_name"] for x in batches):
        batches.append(eb)

# ECE Subjects
subjects = store.setdefault("subjects", [])
ece_subs = [
    {"id": 201, "code": "DCL", "name": "Digital Communication", "department": "ECE", "year": "Year 2", "semester": "Semester 3", "type": "Lecture", "lectures_per_week": 4, "labs_per_week": 0, "requires_lab": False},
    {"id": 202, "code": "SS", "name": "Signals & Systems", "department": "ECE", "year": "Year 2", "semester": "Semester 3", "type": "Lecture", "lectures_per_week": 3, "labs_per_week": 0, "requires_lab": False},
    {"id": 203, "code": "EDC", "name": "Electronic Devices", "department": "ECE", "year": "Year 2", "semester": "Semester 3", "type": "Lecture", "lectures_per_week": 3, "labs_per_week": 0, "requires_lab": False},
    {"id": 204, "code": "DCL-LAB", "name": "Digital Communication Lab", "department": "ECE", "year": "Year 2", "semester": "Semester 3", "type": "Lab", "lectures_per_week": 0, "labs_per_week": 1, "requires_lab": True},
    {"id": 205, "code": "EDC-LAB", "name": "Electronic Devices Lab", "department": "ECE", "year": "Year 2", "semester": "Semester 3", "type": "Lab", "lectures_per_week": 0, "labs_per_week": 1, "requires_lab": True}
]
for es in ece_subs:
    if not any(x.get("department") == "ECE" and x.get("code") == es["code"] for x in subjects):
        subjects.append(es)

# ECE Requirements
requirements = store.setdefault("requirements", [])
ece_reqs = [
    {"department": "ECE", "academic_year": "2026-2027", "year": 2, "semester": 3, "division": "A", "batch": None, "strength": 60, "subject_code": "DCL", "subject": "Digital Communication", "type": "Lecture", "sessions_week": 4, "duration": "1 hr", "faculty_name": "Dr. R. S. Deshmukh", "faculty_code": "RSD", "weekly_max_load": 16, "preference": "Morning", "availability": "Mon-Fri 9:00 AM-4:00 PM", "resource_type": "Classroom", "capacity_required": 60},
    {"department": "ECE", "academic_year": "2026-2027", "year": 2, "semester": 3, "division": "A", "batch": "A1", "strength": 30, "subject_code": "DCL-LAB", "subject": "Digital Communication Lab", "type": "Lab", "sessions_week": 1, "duration": "2 hr", "faculty_name": "Prof. A. P. Joshi", "faculty_code": "APJ", "weekly_max_load": 18, "preference": "Morning", "availability": "Mon-Fri 9:00 AM-1:00 PM", "resource_type": "Lab", "capacity_required": 30},
    {"department": "ECE", "academic_year": "2026-2027", "year": 2, "semester": 3, "division": "A", "batch": "A2", "strength": 30, "subject_code": "DCL-LAB", "subject": "Digital Communication Lab", "type": "Lab", "sessions_week": 1, "duration": "2 hr", "faculty_name": "Prof. A. P. Joshi", "faculty_code": "APJ", "weekly_max_load": 18, "preference": "Morning", "availability": "Mon-Fri 9:00 AM-1:00 PM", "resource_type": "Lab", "capacity_required": 30},
    {"department": "ECE", "academic_year": "2026-2027", "year": 2, "semester": 3, "division": "A", "batch": None, "strength": 60, "subject_code": "SS", "subject": "Signals & Systems", "type": "Lecture", "sessions_week": 3, "duration": "1 hr", "faculty_name": "Prof. A. P. Joshi", "faculty_code": "APJ", "weekly_max_load": 18, "preference": "Morning", "availability": "Mon-Fri 9:00 AM-1:00 PM", "resource_type": "Classroom", "capacity_required": 60},
    {"department": "ECE", "academic_year": "2026-2027", "year": 2, "semester": 3, "division": "A", "batch": None, "strength": 60, "subject_code": "EDC", "subject": "Electronic Devices", "type": "Lecture", "sessions_week": 3, "duration": "1 hr", "faculty_name": "Prof. S. M. Kulkarni", "faculty_code": "SMK", "weekly_max_load": 18, "preference": "Afternoon", "availability": "Mon-Fri 10:00 AM-4:00 PM", "resource_type": "Classroom", "capacity_required": 60},
    {"department": "ECE", "academic_year": "2026-2027", "year": 2, "semester": 3, "division": "A", "batch": "A1", "strength": 30, "subject_code": "EDC-LAB", "subject": "Electronic Devices Lab", "type": "Lab", "sessions_week": 1, "duration": "2 hr", "faculty_name": "Prof. S. M. Kulkarni", "faculty_code": "SMK", "weekly_max_load": 18, "preference": "Afternoon", "availability": "Mon-Fri 10:00 AM-4:00 PM", "resource_type": "Lab", "capacity_required": 30},
    {"department": "ECE", "academic_year": "2026-2027", "year": 2, "semester": 3, "division": "A", "batch": "A2", "strength": 30, "subject_code": "EDC-LAB", "subject": "Electronic Devices Lab", "type": "Lab", "sessions_week": 1, "duration": "2 hr", "faculty_name": "Prof. S. M. Kulkarni", "faculty_code": "SMK", "weekly_max_load": 18, "preference": "Afternoon", "availability": "Mon-Fri 10:00 AM-4:00 PM", "resource_type": "Lab", "capacity_required": 30}
]
for er in ece_reqs:
    if not any(x.get("department") == "ECE" and x.get("subject_code") == er["subject_code"] and x.get("batch") == er["batch"] for x in requirements):
        requirements.append(er)

with store_path.open("w", encoding="utf-8") as f:
    json.dump(store, f, indent=2)

print("SUCCESS: Multi-department baseline seeded into data_store.json!")

