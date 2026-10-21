# backend/scheduler.py
# Core CSP + MRV + Backtracking Scheduling Engine for ClashFree:
# Constraint-Based Timetable & Academic Resource Management System.
#
# CSP Formulation:
# - Variables: Each required teaching session (Lectures & Labs).
# - Domain: Combinations of (Time Slot, Resource, Faculty).
# - Heuristic: MRV (Minimum Remaining Values) variable ordering.
# - Search: Recursive Backtracking with state restoration and clash resolution tracking.
#
# Features:
# - Strict 12-hour AM/PM time representation throughout (NEVER 24-hour time).
# - Dynamic resource matching based on Resource Type, Capacity Required, and Equipment.
# - Exclusion of all old "Reserved Classroom" logic (all active resources are dynamically allocable).
# - Hard faculty availability parsing (e.g. 'Mon-Fri 9:00 AM-4:00 PM') & soft preferences (Morning/Afternoon/Any).
# - Structural exclusion of non-teaching slots (Break and Lunch).
# - Multi-division and batch-level lab scheduling with parallel conduction support.
# - Spread constraints: no back-to-back duplicate same classes; even day distribution.
# - Detailed human-readable infeasibility diagnostics.
# - Clash Detection & Clash Resolution History log (#101, #102, ...).

import copy
import re
import datetime

# ---------------------------------------------------------------------------
# TIME HELPERS (Strict 12-Hour AM/PM Support)
# ---------------------------------------------------------------------------
def format_time_12h(val) -> str:
    """
    Standardize any time representation into 12-hour AM/PM string.
    Examples:
      '09:00' -> '9:00 AM'
      '13:00' -> '1:00 PM'
      '09:00-10:00' -> '9:00 AM - 10:00 AM'
      '13:00-14:00' -> '1:00 PM - 2:00 PM'
    """
    if val is None or val == "":
        return ""

    s = str(val).strip()

    # If it's a range like '09:00-10:00' or '13:00 - 14:00'
    if "-" in s and not ("AM" in s and "PM" in s and len(s.split("-")) == 1):
        parts = s.split("-")
        if len(parts) == 2:
            return f"{format_time_12h(parts[0])} - {format_time_12h(parts[1])}"

    # Already has AM/PM
    m_ampm = re.match(r"^(\d{1,2})(?::(\d{2}))?\s*(AM|PM|am|pm)$", s)
    if m_ampm:
        h = int(m_ampm.group(1))
        mins = int(m_ampm.group(2) or 0)
        mer = m_ampm.group(3).upper()
        return f"{h}:{mins:02d} {mer}"

    # 24-hour 'HH:MM'
    m24 = re.match(r"^(\d{1,2}):(\d{2})", s)
    if m24:
        hour = int(m24.group(1))
        minute = int(m24.group(2))
        meridiem = "PM" if (hour >= 12 or (1 <= hour <= 7)) else "AM"
        display_hour = hour % 12
        if display_hour == 0:
            display_hour = 12
        return f"{display_hour}:{minute:02d} {meridiem}"

    if s.isdigit():
        hour = int(s)
        meridiem = "PM" if (hour >= 12 or (1 <= hour <= 7)) else "AM"
        display_hour = hour % 12
        if display_hour == 0:
            display_hour = 12
        return f"{display_hour}:00 {meridiem}"

    return s


def time_to_minutes(val) -> int:
    """Converts 12h or 24h string to minutes from midnight (e.g. '9:00 AM' -> 540)."""
    if val is None or val == "":
        return 0
    s = str(val).strip()
    m_ampm = re.match(r"^(\d{1,2})(?::(\d{2}))?\s*(AM|PM|am|pm)$", s)
    if m_ampm:
        h = int(m_ampm.group(1))
        mins = int(m_ampm.group(2) or 0)
        mer = m_ampm.group(3).upper()
        if mer == "PM" and h < 12:
            h += 12
        elif mer == "AM" and h == 12:
            h = 0
        return h * 60 + mins

    m24 = re.match(r"^(\d{1,2}):(\d{2})", s)
    if m24:
        h = int(m24.group(1))
        m = int(m24.group(2))
        if 1 <= h <= 7:
            h += 12
        return h * 60 + m
    return 0


# ---------------------------------------------------------------------------
# DEFAULT TIME SLOTS (12-Hour AM/PM Standard)
# ---------------------------------------------------------------------------
DEFAULT_SCHEDULE = [
    {"period": "09:00-10:00", "type": "TEACHING",   "is_morning": True},
    {"period": "10:00-11:00", "type": "TEACHING",   "is_morning": True},
    {"period": "11:00-11:10", "type": "SHORT_BREAK", "is_morning": True},
    {"period": "11:10-12:10", "type": "TEACHING",   "is_morning": True},
    {"period": "12:10-01:10", "type": "TEACHING",   "is_morning": True},
    {"period": "01:10-01:50", "type": "LUNCH",      "is_morning": False},
    {"period": "01:50-02:50", "type": "TEACHING",   "is_morning": False},
    {"period": "02:50-03:50", "type": "TEACHING",   "is_morning": False},
    {"period": "03:50-04:00", "type": "SHORT_BREAK", "is_morning": False},
    {"period": "04:00-05:00", "type": "TEACHING",   "is_morning": False},
]

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
DAY_ORDER = {d: i for i, d in enumerate(DAYS)}

_session_lookup = {}
_period_order_map = {}
_active_days = list(DAYS)
_day_order = dict(DAY_ORDER)


def _are_periods_consecutive(p1: str, p2: str) -> bool:
    """Return True if p1 and p2 are strictly consecutive teaching periods."""
    idx1 = _period_order_map.get(p1)
    idx2 = _period_order_map.get(p2)
    if idx1 is not None and idx2 is not None:
        return abs(idx1 - idx2) == 1
    return False


def _faculty_is_available(faculty: dict, day: str, period_label: str) -> bool:
    """
    Hard availability constraint checker:
    1. Check availability string (e.g. 'Mon-Fri 9:00 AM-4:00 PM')
    2. Check available_from and available_to
    3. Check blocked_slots list
    """
    avail_str = faculty.get("availability")
    if avail_str and str(avail_str).strip() not in ["", "-", "None"]:
        from backend.excel_reader import parse_availability_string
        parsed = parse_availability_string(avail_str)
        if day not in parsed.get("days", []):
            return False

        # Extract period start minutes
        parts = period_label.split("-")
        period_start = time_to_minutes(parts[0])
        period_end = time_to_minutes(parts[1]) if len(parts) > 1 else period_start + 60

        if period_start < parsed.get("from_minutes", 0) or period_end > (parsed.get("to_minutes", 1440) + 5):
            return False

    # Check available_from / available_to legacy fields
    if faculty.get("available_from") and faculty.get("available_to"):
        avail_from = time_to_minutes(faculty.get("available_from"))
        avail_to = time_to_minutes(faculty.get("available_to"))
        parts = period_label.split("-")
        period_start = time_to_minutes(parts[0])
        if not (avail_from <= period_start < avail_to):
            return False

    # Blocked slots
    blocked = faculty.get("blocked_slots") or []
    for b in blocked:
        if day in b and (period_label in b or format_time_12h(period_label) in b):
            return False

    return True


def _find_faculty_for_subject(subject_name: str, faculty_list: list) -> list:
    """Return faculty members qualified to teach this subject."""
    result = []
    for f in faculty_list:
        subjects = f.get("subjects") or []
        if isinstance(subjects, str):
            subjects = [s.strip() for s in subjects.split(",")]
        if subject_name in subjects:
            result.append(f)
    return result


def _find_suitable_rooms(session: dict, active_rooms: list) -> list:
    """
    Dynamic Resource Allocation (Section 10 requirement):
    Matches resource purely on:
    1. Resource Type: Classroom for Lecture, Lab for Lab.
    2. Capacity: room.capacity >= Capacity Required.
    3. Equipment: checks equipment requirement (e.g. 'Computer', 'Projector').
    4. Active: only is_active == True resources.
    NO old reserved-room buffer or filtering!
    """
    req_type = "Lab" if session.get("is_lab") else "Classroom"
    req_cap = session.get("capacity_required", session.get("strength", 60))
    req_eq = (session.get("equipment") or "").strip().lower()

    suitable = []
    for r in active_rooms:
        if not r.get("is_active", True):
            continue
        if r.get("type") != req_type:
            continue
        if (r.get("capacity") or 0) < req_cap:
            continue

        if req_eq and req_eq != "-":
            r_eq = (r.get("equipment") or "").lower()
            if req_eq not in r_eq:
                if req_eq in ["computer", "pc"]:
                    if not (r.get("num_pcs", 0) >= req_cap or "computer" in (r.get("lab_type") or "").lower()):
                        continue
                else:
                    continue

        suitable.append(r)

    # Sort rooms by capacity ascending (Best Fit heuristic: smallest room that fits to save larger rooms)
    suitable.sort(key=lambda r: r.get("capacity", 0))
    return suitable


# ---------------------------------------------------------------------------
# BUILD SESSIONS (CSP VARIABLES)
# ---------------------------------------------------------------------------
def _build_sessions(subject_list: list, division_list: list, batch_list: list, department: str = "CSE", requirements: list = None):
    """
    Builds CSP variables:
    Each variable is one required teaching session.
    Prioritizes explicit single-sheet teaching requirements if provided.
    Falls back to generating sessions from subject/division lists.
    """
    sessions = []
    sid = 0

    if requirements:
        for req in requirements:
            sess_count = req.get("sessions_week", 1)
            is_lab = (req.get("type") == "Lab" or req.get("resource_type") == "Lab")
            for i in range(sess_count):
                sessions.append({
                    "id": f"s{sid}",
                    "department": department,
                    "division": req.get("division", "A"),
                    "batch": req.get("batch"),
                    "subject": req.get("subject"),
                    "subject_code": req.get("subject_code"),
                    "is_lab": is_lab,
                    "strength": req.get("strength", 60),
                    "capacity_required": req.get("capacity_required", 60),
                    "equipment": req.get("equipment", ""),
                    "faculty_name": req.get("faculty_name"),
                    "faculty_code": req.get("faculty_code"),
                    "preference": req.get("preference", "Any"),
                    "index": i,
                    "total_sessions": sess_count,
                })
                sid += 1
        return sessions

    # Fallback generation from subject_list and division_list
    dept_subjects = [s for s in subject_list if s.get("department", "CSE") == department]
    dept_divisions = [d for d in division_list if d.get("department_code", d.get("department", "CSE")) == department]
    if not dept_divisions:
        dept_divisions = division_list

    for div in dept_divisions:
        div_name = div.get("name")
        div_strength = div.get("strength", 60)
        div_batches = [b for b in batch_list if b.get("division_name") == div_name]
        if not div_batches:
            half = div_strength // 2
            div_batches = [
                {"name": f"{div_name}-1", "strength": half},
                {"name": f"{div_name}-2", "strength": div_strength - half}
            ]

        for subj in dept_subjects:
            lec_count = subj.get("lectures_per_week") or 0
            lab_count = subj.get("labs_per_week") or 0

            # Lecture sessions
            for i in range(lec_count):
                sessions.append({
                    "id": f"s{sid}",
                    "department": department,
                    "division": div_name,
                    "batch": None,
                    "subject": subj["name"],
                    "subject_code": subj.get("code", ""),
                    "is_lab": False,
                    "strength": div_strength,
                    "capacity_required": div_strength,
                    "equipment": subj.get("equipment", ""),
                    "index": i,
                    "total_sessions": lec_count,
                })
                sid += 1

            # Lab sessions
            for i in range(lab_count):
                for batch in div_batches:
                    sessions.append({
                        "id": f"s{sid}",
                        "department": department,
                        "division": div_name,
                        "batch": batch["name"],
                        "subject": subj["name"],
                        "subject_code": subj.get("code", ""),
                        "is_lab": True,
                        "strength": batch.get("strength", 30),
                        "capacity_required": batch.get("strength", 30),
                        "equipment": subj.get("equipment") or "Computer",
                        "index": i,
                        "total_sessions": lab_count,
                    })
                    sid += 1

    return sessions


# ---------------------------------------------------------------------------
# BUILD DOMAIN (CSP DOMAINS)
# ---------------------------------------------------------------------------
def _build_domain(session: dict, faculty_list: list, active_rooms: list, teaching_slots: list, approved_sharing: list = None):
    """
    Return all valid ((day, period), room, faculty) options for a session.
    Enforces:
    - Only valid TEACHING slots (breaks & lunches are already excluded).
    - Faculty subject qualification.
    - Faculty hard availability.
    - Suitable active room matching type, capacity, and equipment.
    - Cross-department resource sharing reservations.
    """
    if approved_sharing is None:
        approved_sharing = []

    # If faculty is explicitly assigned to session (from single sheet row)
    req_fac_code = session.get("faculty_code")
    req_fac_name = session.get("faculty_name")

    if req_fac_code or req_fac_name:
        possible_faculty = [
            f for f in faculty_list
            if (req_fac_code and f.get("code") == req_fac_code) or
               (req_fac_name and f.get("name") == req_fac_name)
        ]
        if not possible_faculty:
            possible_faculty = _find_faculty_for_subject(session["subject"], faculty_list)
    else:
        possible_faculty = _find_faculty_for_subject(session["subject"], faculty_list)

    suitable_rooms = _find_suitable_rooms(session, active_rooms)

    sharing_blocks = {}
    for req in approved_sharing:
        if req.get("status") == "APPROVED":
            key = (req.get("day"), format_time_12h(req.get("period")), req.get("resource_name"))
            sharing_blocks[key] = req.get("requesting_department")

    domain = []
    for (day, period, is_morning) in teaching_slots:
        for room in suitable_rooms:
            block_key = (day, period, room.get("name"))
            if block_key in sharing_blocks and sharing_blocks[block_key] != session.get("department"):
                continue

            for faculty in possible_faculty:
                if _faculty_is_available(faculty, day, period):
                    domain.append(((day, period), room, faculty))

    # Soft constraint sorting (Section 16 requirement):
    # 1. Faculty preferred time (Morning vs Afternoon)
    # 2. Spread across distinct days to avoid clustering
    def sort_key(entry):
        (day, period), room, faculty = entry
        is_morning = any(slot[2] for slot in teaching_slots if slot[0] == day and slot[1] == period)
        pref = faculty.get("preferred_time") or session.get("preference") or "Any"

        pref_score = 0
        if pref == "Morning" and is_morning:
            pref_score = -2
        elif pref == "Morning" and not is_morning:
            pref_score = 2
        elif pref == "Afternoon" and not is_morning:
            pref_score = -2
        elif pref == "Afternoon" and is_morning:
            pref_score = 2

        num_days = max(1, len(_active_days))
        total_s = max(1, session.get("total_sessions", 3))
        subj_hash = sum(ord(c) for c in session["subject"])
        ideal_day_idx = (int(session.get("index", 0) * (num_days / total_s)) + subj_hash) % num_days
        curr_day_idx = _day_order.get(day, 0)
        day_dist = min(abs(curr_day_idx - ideal_day_idx), num_days - abs(curr_day_idx - ideal_day_idx))

        return pref_score + (day_dist * 2.5)

    domain.sort(key=sort_key)
    return domain


# ---------------------------------------------------------------------------
# HARD CONSTRAINT CHECKER
# ---------------------------------------------------------------------------
def _is_valid(session: dict, slot: tuple, room: dict, faculty: dict, assignment: dict) -> tuple:
    """
    Verifies ALL hard constraints (Section 15 requirement):
    1. Faculty cannot teach two sessions at the same time.
    2. Room cannot host two sessions at the same time.
    3. Lab cannot host two sessions at the same time.
    4. Division cannot have two lectures at the same time.
    5. A batch cannot have two classes at the same time.
    6. Parallel lab batches of same division cannot clash on batch, faculty, or room.
    7. No division lecture while a lab batch is scheduled, and vice versa.
    8. No back-to-back duplicate lecture of the same subject on the same day for same division.
    9. Even distribution: division cannot exceed daily lecture limit of same subject.
    10. Faculty fatigue limit: faculty cannot teach > 3 consecutive periods on the same day.

    Returns: (is_valid: bool, conflict_details: dict or None)
    """
    day, period = slot
    same_fac_consec = 0

    for assigned_id, (a_slot, a_room, a_faculty) in assignment.items():
        a_day, a_period = a_slot
        a_session = _session_lookup.get(assigned_id)
        if not a_session:
            continue

        # Same slot clashes
        if a_day == day and a_period == period:
            # Constraint 1: Faculty clash
            if a_faculty.get("code") == faculty.get("code"):
                return False, {
                    "type": "Faculty Clash",
                    "entity": faculty.get("code"),
                    "faculty_name": faculty.get("name"),
                    "division": session.get("division"),
                    "resource": room.get("name"),
                    "time": f"{day} {period}",
                    "issue": f"Faculty {faculty.get('code')} ({faculty.get('name')}) is already assigned to {a_session['division']} {a_session['subject']}.",
                    "resolution": f"Reassigned {session['division']} {session['subject']} to alternate slot"
                }

            # Constraint 2 & 3: Room double booking
            if a_room.get("name") == room.get("name"):
                return False, {
                    "type": "Room Clash",
                    "entity": room.get("name"),
                    "faculty_name": faculty.get("name"),
                    "division": session.get("division"),
                    "resource": room.get("name"),
                    "time": f"{day} {period}",
                    "issue": f"Resource {room.get('name')} is already occupied by {a_session['division']} {a_session['subject']}.",
                    "resolution": f"Assigned alternate room for {session['division']} {session['subject']}"
                }

            # Constraint 4, 5, 7: Division and Batch checks
            if a_session["division"] == session["division"]:
                if not a_session.get("batch") or not session.get("batch"):
                    return False, {
                        "type": "Division Clash",
                        "entity": session.get("division"),
                        "faculty_name": faculty.get("name"),
                        "division": session.get("division"),
                        "resource": room.get("name"),
                        "time": f"{day} {period}",
                        "issue": f"Division {session['division']} already has class {a_session['subject']} scheduled in this slot.",
                        "resolution": f"Reassigned {session['division']} {session['subject']} to alternate slot"
                    }
                if a_session.get("batch") == session.get("batch"):
                    return False, {
                        "type": "Batch Clash",
                        "entity": session.get("batch"),
                        "faculty_name": faculty.get("name"),
                        "division": session.get("division"),
                        "resource": room.get("name"),
                        "time": f"{day} {period}",
                        "issue": f"Batch {session.get('batch')} already has lab {a_session['subject']} in this slot.",
                        "resolution": f"Reassigned Batch {session.get('batch')} to alternate slot"
                    }

        # Constraint 8: No back-to-back duplicate lecture of the same subject
        if a_day == day and a_session["division"] == session["division"]:
            if not session.get("is_lab") and not a_session.get("is_lab"):
                if a_session["subject"] == session["subject"]:
                    if _are_periods_consecutive(a_period, period):
                        return False, None

        # Constraint 10: Faculty consecutive fatigue check on same day
        if a_day == day and a_faculty.get("code") == faculty.get("code"):
            if _are_periods_consecutive(a_period, period):
                same_fac_consec += 1
                if same_fac_consec >= 3:
                    return False, None

    # Constraint 9: Daily lecture limit per subject for a division
    if not session.get("is_lab"):
        total_s = session.get("total_sessions", 3)
        num_days = max(1, len(_active_days))
        max_daily = max(1, (total_s + num_days - 1) // num_days)
        same_day_count = sum(
            1 for aid, (aslot, _, _) in assignment.items()
            if aslot[0] == day and
               _session_lookup.get(aid) and
               _session_lookup[aid]["division"] == session["division"] and
               _session_lookup[aid]["subject"] == session["subject"] and
               not _session_lookup[aid].get("is_lab")
        )
        if same_day_count >= max_daily:
            return False, None

    return True, None


# ---------------------------------------------------------------------------
# MRV (MINIMUM REMAINING VALUES) HEURISTIC
# ---------------------------------------------------------------------------
def _pick_next_session(unscheduled: list, assignment: dict, domains: dict):
    """
    MRV Heuristic (Section 17 requirement):
    Choose the unscheduled variable with the fewest remaining valid options.
    Rationale:
    If a variable has very few choices left, it is most likely to cause a dead end
    later; addressing it first fails fast and prunes the search space drastically.
    Tie-breaker: Lab sessions first (due to specialized equipment and lab rooms).
    """
    best_session = None
    best_count = float("inf")

    for session in unscheduled:
        sid = session["id"]
        valid_count = sum(
            1 for (slot, room, faculty) in domains[sid]
            if _is_valid(session, slot, room, faculty, assignment)[0]
        )

        priority = 0 if session.get("is_lab") else 1

        if (valid_count, priority) < (best_count, 1):
            best_count = valid_count
            best_session = session

        if best_count == 0:
            break

    return best_session, best_count


# ---------------------------------------------------------------------------
# BACKTRACKING SEARCH WITH CLASH RESOLUTION TRACKING
# ---------------------------------------------------------------------------
def _backtrack(unscheduled: list, assignment: dict, domains: dict, step_counter: list, clash_tracker: dict):
    """
    Recursive backtracking with state restoration, MRV variable ordering,
    and automatic clash resolution logging (Section 18, 19, 20 requirement).
    """
    step_counter[0] += 1
    if step_counter[0] > 100000:
        return None

    if not unscheduled:
        return assignment

    session, count = _pick_next_session(unscheduled, assignment, domains)
    if session is None or count == 0:
        return None

    sid = session["id"]
    for (slot, room, faculty) in domains[sid]:
        is_ok, conflict_info = _is_valid(session, slot, room, faculty, assignment)

        if not is_ok:
            # Record detected clash for history log
            if conflict_info:
                cid = clash_tracker["counter"]
                clash_tracker["counter"] += 1
                conflict_entry = {
                    "id": f"#{cid}",
                    "type": conflict_info["type"],
                    "entity": conflict_info["entity"],
                    "faculty": conflict_info.get("faculty_name", ""),
                    "division": conflict_info.get("division", ""),
                    "resource": conflict_info.get("resource", ""),
                    "time": conflict_info["time"],
                    "status": "Detected",
                    "issue": conflict_info["issue"],
                    "resolution": "Pending alternate slot/resource evaluation"
                }
                clash_tracker["log"].append(conflict_entry)
            continue

        # Commit tentative assignment
        assignment[sid] = (slot, room, faculty)
        remaining = [s for s in unscheduled if s["id"] != sid]

        res = _backtrack(remaining, assignment, domains, step_counter, clash_tracker)
        if res is not None:
            # Mark clashes for this session as Resolved
            for c in clash_tracker["log"]:
                if c.get("division") == session.get("division") and c.get("status") == "Detected":
                    c["status"] = "Resolved"
                    c["resolution"] = f"Reassigned {session['division']} {session['subject']} to {slot[0]} {slot[1]} in {room['name']}"
            return res

        # Undo tentative assignment (Backtrack)
        del assignment[sid]

    return None


# ---------------------------------------------------------------------------
# INFEASIBILITY DIAGNOSTICS
# ---------------------------------------------------------------------------
def diagnose_infeasibility(sessions, domains, active_rooms, faculty_list, teaching_slots):
    """
    Plain-English human-readable diagnostic report explaining why
    scheduling could not succeed (Section 21 requirement).
    """
    diagnostics = []
    total_slots = len(teaching_slots)

    div_sessions = {}
    for s in sessions:
        div_sessions[s["division"]] = div_sessions.get(s["division"], 0) + 1

    for div, req_count in div_sessions.items():
        if req_count > total_slots:
            diagnostics.append(
                f"Division '{div}' requires {req_count} weekly sessions, but only {total_slots} teaching slots exist in the week."
            )

    for s in sessions:
        sid = s["id"]
        d = domains.get(sid, [])
        label = f"Lab ({s.get('batch')})" if s.get("is_lab") else "Lecture"
        if not d:
            qualified = _find_faculty_for_subject(s["subject"], faculty_list)
            if not qualified:
                diagnostics.append(f"No faculty member is assigned to teach subject '{s['subject']}'.")
            else:
                suitable = _find_suitable_rooms(s, active_rooms)
                if not suitable:
                    diagnostics.append(
                        f"No active {label} room has sufficient capacity (>= {s.get('strength')}) or equipment for {s['division']} - {s['subject']}."
                    )
                else:
                    diagnostics.append(
                        f"Faculty qualified for '{s['subject']}' have tight availability or all candidate slots conflict."
                    )

    if not diagnostics:
        diagnostics.append(
            "Backtracking exhausted all search branches. Constraints are overly tight (tight faculty availability, room capacity limits, or parallel batch collisions)."
        )

    return diagnostics


# ---------------------------------------------------------------------------
# PUBLIC ENTRY POINT
# ---------------------------------------------------------------------------
def generate_timetable(
    faculty_list: list,
    room_list: list,
    subject_list: list,
    division_list: list,
    batch_list: list = None,
    time_slots: list = None,
    resource_config: dict = None,
    department: str = "CSE",
    approved_sharing: list = None,
    days: list = None,
    requirements: list = None
):
    """
    Main timetable generator with CSP + MRV + Backtracking.
    Strictly standardizes on 12-Hour AM/PM format.
    Dynamically matches active resources without reserved buffers.
    Tracks detected and resolved clashes.
    Returns: (success: bool, message: str, timetable_rows: list, conflicts: list, metadata: dict)
    """
    global _session_lookup, _period_order_map, _active_days, _day_order

    if batch_list is None:
        batch_list = []
    if approved_sharing is None:
        approved_sharing = []

    if days:
        _active_days = list(days)
    else:
        _active_days = list(DAYS)
    _day_order = {d: i for i, d in enumerate(_active_days)}

    # Standardize time slots in 12-Hour AM/PM format
    if not time_slots:
        time_slots = DEFAULT_SCHEDULE
    else:
        # Standardize period labels in time slots
        formatted_slots = []
        for s in time_slots:
            s_copy = dict(s)
            s_copy["period"] = format_time_12h(s.get("period"))
            formatted_slots.append(s_copy)
        time_slots = formatted_slots

    _period_order_map = {slot["period"]: idx for idx, slot in enumerate(time_slots)}

    teaching_slots = []
    for d in _active_days:
        for slot in time_slots:
            if slot.get("type") == "TEACHING":
                teaching_slots.append((d, slot["period"], slot.get("is_morning", False)))

    if not faculty_list:
        return False, "No faculty records found.", [], ["No faculty available to schedule."], {}
    if not room_list:
        return False, "No rooms or labs found.", [], ["No rooms available to schedule."], {}
    if not subject_list and not requirements:
        return False, "No subjects or requirements found.", [], ["No subjects available to schedule."], {}
    if not division_list and not requirements:
        return False, "No divisions found.", [], ["No divisions available to schedule."], {}

    # All active rooms are available for scheduling (no reserved room concept!)
    active_rooms = [r for r in room_list if r.get("is_active", True) and r.get("department", department) == department]
    if not active_rooms:
        active_rooms = [r for r in room_list if r.get("is_active", True)]

    # Step 1: Build Sessions (CSP Variables)
    sessions = _build_sessions(subject_list, division_list, batch_list, department, requirements)
    _session_lookup = {s["id"]: s for s in sessions}

    if not sessions:
        return False, "No teaching sessions to schedule.", [], ["All subjects have 0 lectures and 0 labs per week."], {}

    # Step 2: Build Domains (CSP Domains)
    domains = {}
    pre_conflicts = []
    for s in sessions:
        d = _build_domain(s, faculty_list, active_rooms, teaching_slots, approved_sharing)
        domains[s["id"]] = d
        if not d:
            label = f"Lab ({s.get('batch')})" if s.get("is_lab") else "Lecture"
            pre_conflicts.append(
                f"No feasible slot/room for {s['division']} {label} - {s['subject']}. Check faculty availability, room capacity, and equipment."
            )

    if pre_conflicts:
        return (
            False,
            f"Cannot generate timetable due to {len(pre_conflicts)} unresolvable constraint conflict(s).",
            [],
            pre_conflicts,
            {"active_rooms": len(active_rooms), "total_sessions": len(sessions)}
        )

    # Step 3: Backtracking with MRV & Clash Tracking
    step_counter = [0]
    clash_tracker = {"counter": 101, "log": []}
    result = _backtrack(list(sessions), {}, domains, step_counter, clash_tracker)

    if result is None:
        explanations = diagnose_infeasibility(
            sessions, domains, active_rooms, faculty_list, teaching_slots
        )
        return (
            False,
            "Timetable generation could not find a clash-free assignment.",
            [],
            explanations,
            {"active_rooms": len(active_rooms), "backtrack_steps": step_counter[0]}
        )

    # Step 4: Format Timetable Rows (Strict 12-Hour AM/PM)
    timetable_rows = []
    for s in sessions:
        sid = s["id"]
        if sid in result:
            (day, period), room, faculty = result[sid]
            is_morning = any(slot[2] for slot in teaching_slots if slot[0] == day and slot[1] == period)
            timetable_rows.append({
                "day": day,
                "day_order": _day_order.get(day, 99),
                "period": format_time_12h(period),
                "is_morning": is_morning,
                "department": department,
                "section": s["division"],
                "batch": s.get("batch"),
                "subject": s["subject"],
                "subject_code": s.get("subject_code", ""),
                "faculty_code": faculty.get("code", ""),
                "faculty_name": faculty.get("name", ""),
                "room": room.get("name", ""),
                "room_type": room.get("type", "Classroom"),
                "is_lab": s["is_lab"]
            })

    timetable_rows.sort(key=lambda r: (r["day_order"], _period_order_map.get(r["period"], 99), r["section"], r.get("batch") or ""))

    # Clash Resolution Summary
    detected_clashes = len(clash_tracker["log"])
    resolved_clashes = len([c for c in clash_tracker["log"] if c["status"] == "Resolved"])
    unresolved_clashes = detected_clashes - resolved_clashes

    cr_count = len([r for r in active_rooms if r.get("type") == "Classroom"])
    lab_count = len([r for r in active_rooms if r.get("type") == "Lab"])

    summary_msg = (
        f"Timetable generated successfully! {len(timetable_rows)} sessions scheduled "
        f"across {len(active_rooms)} active resources ({cr_count} classrooms, {lab_count} labs). "
        f"{detected_clashes} clashes detected and {resolved_clashes} automatically resolved by CSP engine."
    )

    metadata = {
        "scheduled_count": len(timetable_rows),
        "active_rooms_count": len(active_rooms),
        "backtrack_steps": step_counter[0],
        "detected_clashes": detected_clashes,
        "resolved_clashes": resolved_clashes,
        "unresolved_clashes": unresolved_clashes,
        "clash_history": clash_tracker["log"][:50]  # First 50 resolution events
    }

    return True, summary_msg, timetable_rows, [], metadata


def filter_and_reserve_resources(room_list: list, dept_code: str = "CSE", resource_config: dict = None):
    """
    Maintained for API backward compatibility.
    No rooms are reserved; all active rooms are returned as active.
    """
    dept_rooms = [r for r in room_list if r.get("department", "CSE") == dept_code]
    if not dept_rooms:
        dept_rooms = room_list
    active_rooms = [r for r in dept_rooms if r.get("is_active", True)]
    reserved_rooms = []
    other_rooms = [r for r in room_list if r not in dept_rooms]
    return active_rooms, reserved_rooms, other_rooms
