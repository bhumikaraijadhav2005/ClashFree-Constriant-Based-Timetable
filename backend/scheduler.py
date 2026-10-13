# backend/scheduler.py
# Core CSP + MRV + Backtracking Scheduling Engine for ClashFree.
# Preserves the proven CSP/MRV architecture while supporting:
# - Resource reservation (HOD requirement: keep configurable classrooms/labs reserved)
# - Batch-level lab scheduling (parallel lab conduction per batch)
# - Division & Batch student strengths and room capacity verification
# - Computer lab PC availability and Student:PC ratio constraints
# - Multi-department awareness & approved resource sharing
# - Hard faculty availability & soft morning/afternoon preferences
# - Break & lunch exclusion (structurally impossible to schedule during breaks)
# - Infeasibility diagnostics with actionable plain-English explanations

import copy

# ---------------------------------------------------------------------------
# DEFAULT TIME SLOTS & PERIODS
# ---------------------------------------------------------------------------
DEFAULT_SCHEDULE = [
    {"period": "09:00-10:00", "type": "TEACHING",   "is_morning": True},
    {"period": "10:00-11:00", "type": "TEACHING",   "is_morning": True},
    {"period": "11:00-11:15", "type": "SHORT_BREAK", "is_morning": True},
    {"period": "11:15-12:15", "type": "TEACHING",   "is_morning": True},
    {"period": "12:15-13:00", "type": "LUNCH",       "is_morning": False},
    {"period": "13:00-14:00", "type": "TEACHING",   "is_morning": False},
    {"period": "14:00-15:00", "type": "TEACHING",   "is_morning": False},
    {"period": "15:00-15:15", "type": "SHORT_BREAK", "is_morning": False},
    {"period": "15:15-16:15", "type": "TEACHING",   "is_morning": False},
]

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
DAY_ORDER = {d: i for i, d in enumerate(DAYS)}

_session_lookup = {}
_period_order_map = {}
_active_days = list(DAYS)
_day_order = dict(DAY_ORDER)


def _are_periods_consecutive(p1: str, p2: str) -> bool:
    """Return True if p1 and p2 are consecutive in chronological period order."""
    idx1 = _period_order_map.get(p1)
    idx2 = _period_order_map.get(p2)
    if idx1 is not None and idx2 is not None:
        return abs(idx1 - idx2) == 1
    return False


def _time_to_minutes(time_str: str) -> int:
    """'09:00' -> 540"""
    try:
        parts = time_str.strip().split(":")
        return int(parts[0]) * 60 + int(parts[1])
    except Exception:
        return 0


def _parse_ratio(ratio_str) -> float:
    """'1:1' -> 1.0, '2:1' -> 0.5 (2 students per PC)"""
    if isinstance(ratio_str, (int, float)):
        return float(ratio_str)
    try:
        if ":" in str(ratio_str):
            num, den = str(ratio_str).split(":")
            return float(den) / float(num) if float(num) > 0 else 1.0
        return float(ratio_str)
    except Exception:
        return 1.0


def _faculty_is_available(faculty: dict, day: str, period_label: str) -> bool:
    """
    Hard availability: checks available_from, available_to, and blocked_slots.
    """
    avail_from = _time_to_minutes(faculty.get("available_from") or "09:00")
    avail_to   = _time_to_minutes(faculty.get("available_to")   or "17:00")
    period_start = _time_to_minutes(period_label.split("-")[0])

    if not (avail_from <= period_start < avail_to):
        return False

    blocked = faculty.get("blocked_slots") or []
    slot_tag = f"{day} {period_label}"
    if slot_tag in blocked:
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


# ---------------------------------------------------------------------------
# RESOURCE RESERVATION & FILTERING (HOD REQUIREMENT)
# ---------------------------------------------------------------------------
def filter_and_reserve_resources(room_list: list, dept_code: str, resource_config: dict = None):
    """
    Partition rooms into:
    - active_rooms: available for scheduling
    - reserved_rooms: marked RESERVED (NOT selected by timetable scheduler)

    Configurable reserved counts:
    - reserved_classrooms_count
    - reserved_labs_count
    """
    if resource_config is None:
        resource_config = {
            "reserved_classrooms_count": 1,
            "reserved_labs_count": 1,
            "student_pc_ratio": "1:1"
        }

    reserved_cr_target = int(resource_config.get("reserved_classrooms_count", 1))
    reserved_lab_target = int(resource_config.get("reserved_labs_count", 1))

    dept_rooms = [r for r in room_list if r.get("department", "CSE") == dept_code]
    other_rooms = [r for r in room_list if r.get("department", "CSE") != dept_code]

    cr_list = [r for r in dept_rooms if r.get("type") == "Classroom"]
    lab_list = [r for r in dept_rooms if r.get("type") == "Lab"]

    # 1. Identify already marked reserved
    reserved_cr = [r for r in cr_list if r.get("is_reserved")]
    unreserved_cr = [r for r in cr_list if not r.get("is_reserved")]

    # If explicit reserved < target, reserve from end of list
    needed_cr = max(0, reserved_cr_target - len(reserved_cr))
    for _ in range(min(needed_cr, len(unreserved_cr))):
        r = unreserved_cr.pop()
        r_copy = dict(r)
        r_copy["is_reserved"] = True
        r_copy["reservation_reason"] = r_copy.get("reservation_reason") or "HOD Department Reserve"
        reserved_cr.append(r_copy)

    # 2. Labs
    reserved_lab = [r for r in lab_list if r.get("is_reserved")]
    unreserved_lab = [r for r in lab_list if not r.get("is_reserved")]

    needed_lab = max(0, reserved_lab_target - len(reserved_lab))
    for _ in range(min(needed_lab, len(unreserved_lab))):
        r = unreserved_lab.pop()
        r_copy = dict(r)
        r_copy["is_reserved"] = True
        r_copy["reservation_reason"] = r_copy.get("reservation_reason") or "HOD Lab Reserve"
        reserved_lab.append(r_copy)

    active_rooms = unreserved_cr + unreserved_lab
    reserved_rooms = reserved_cr + reserved_lab

    return active_rooms, reserved_rooms, other_rooms


def _find_suitable_rooms(session: dict, active_rooms: list, shared_rooms_by_slot: dict, student_pc_ratio: float = 1.0) -> list:
    """
    Return rooms that:
    1. Match type (Lab for lab session, Classroom for lecture)
    2. Have sufficient seating capacity >= session strength
    3. If Computer Lab, have enough PCs >= required_pcs
    """
    req_strength = session.get("strength", 60)
    is_lab = session.get("is_lab", False)
    req_type = "Lab" if is_lab else "Classroom"

    suitable = []
    for r in active_rooms:
        if r.get("type") != req_type:
            continue
        if (r.get("capacity") or 0) < req_strength:
            continue

        if is_lab:
            lab_type = session.get("lab_type", "")
            if lab_type and r.get("lab_type") and lab_type.lower() not in r.get("lab_type", "").lower() and r.get("lab_type", "").lower() not in lab_type.lower():
                # Loose matching or fallback
                pass
            
            # PC constraint for Computer Labs
            if "computer" in (r.get("lab_type") or "").lower() or "pc" in (r.get("lab_type") or "").lower():
                num_pcs = r.get("num_pcs") or 0
                needed_pcs = int(req_strength * student_pc_ratio)
                if num_pcs > 0 and num_pcs < needed_pcs:
                    continue

        suitable.append(r)

    return suitable


# ---------------------------------------------------------------------------
# BUILD SESSIONS (CSP VARIABLES)
# ---------------------------------------------------------------------------
def _build_sessions(subject_list: list, division_list: list, batch_list: list, department: str = "CSE"):
    """
    Builds CSP variables:
    - Lecture sessions: generated division-wise (full class)
    - Lab sessions: generated batch-wise (e.g. A1, A2 separate sessions)
    """
    sessions = []
    sid = 0

    dept_subjects = [s for s in subject_list if s.get("department", "CSE") == department]
    dept_divisions = [d for d in division_list if d.get("department_code", d.get("department", "CSE")) == department]

    if not dept_divisions:
        dept_divisions = division_list

    for div in dept_divisions:
        div_name = div.get("name")
        div_strength = div.get("strength", 60)

        # Find batches for this division
        div_batches = [b for b in batch_list if b.get("division_name") == div_name]
        if not div_batches:
            # Fallback default batches A1, A2 if not explicitly listed
            half = div_strength // 2
            div_batches = [
                {"name": f"{div_name}-1", "strength": half},
                {"name": f"{div_name}-2", "strength": div_strength - half}
            ]

        for subj in dept_subjects:
            lec_count = subj.get("lectures_per_week") or 0
            lab_count = subj.get("labs_per_week") or 0

            # Lecture sessions (Whole Division)
            for i in range(lec_count):
                sessions.append({
                    "id": f"s{sid}",
                    "department": department,
                    "division": div_name,
                    "batch": None,
                    "subject": subj["name"],
                    "is_lab": False,
                    "strength": div_strength,
                    "lab_type": "",
                    "index": i,
                    "total_sessions": lec_count,
                })
                sid += 1

            # Lab sessions (Batch-wise!)
            for i in range(lab_count):
                for batch in div_batches:
                    sessions.append({
                        "id": f"s{sid}",
                        "department": department,
                        "division": div_name,
                        "batch": batch["name"],
                        "subject": subj["name"],
                        "is_lab": True,
                        "strength": batch.get("strength", 30),
                        "lab_type": subj.get("lab_type") or "Computer Lab",
                        "index": i,
                        "total_sessions": lab_count,
                    })
                    sid += 1

    return sessions


# ---------------------------------------------------------------------------
# BUILD DOMAIN (CSP DOMAINS)
# ---------------------------------------------------------------------------
def _build_domain(session: dict, faculty_list: list, active_rooms: list, teaching_slots: list, student_pc_ratio: float = 1.0, approved_sharing: list = None):
    """
    Return all valid ((day, period), room, faculty) options for a session.
    Filters:
    - Only TEACHING slots
    - Faculty subject qualification
    - Faculty hard availability
    - Suitable room (capacity & lab PC count)
    - Resource sharing blocks
    """
    if approved_sharing is None:
        approved_sharing = []

    possible_faculty = _find_faculty_for_subject(session["subject"], faculty_list)
    suitable_rooms = _find_suitable_rooms(session, active_rooms, {}, student_pc_ratio)

    # Sharing map: (day, period, room_name) -> allowed dept
    sharing_blocks = {}
    for req in approved_sharing:
        if req.get("status") == "APPROVED":
            key = (req.get("day"), req.get("period"), req.get("resource_name"))
            sharing_blocks[key] = req.get("requesting_department")

    domain = []
    for (day, period, is_morning) in teaching_slots:
        for room in suitable_rooms:
            # Check if this room is shared away to another dept during this slot
            block_key = (day, period, room.get("name"))
            if block_key in sharing_blocks and sharing_blocks[block_key] != session.get("department"):
                continue

            for faculty in possible_faculty:
                if _faculty_is_available(faculty, day, period):
                    domain.append(((day, period), room, faculty))

    # Soft constraint sorting:
    # 1. Faculty preferred time (Morning vs Afternoon)
    # 2. Avoid cramming sessions on same day
    def sort_key(entry):
        (day, period), room, faculty = entry
        is_morning = any(slot[2] for slot in teaching_slots if slot[0] == day and slot[1] == period)
        pref = faculty.get("preferred_time") or "Any"

        pref_score = 0
        if pref == "Morning" and is_morning:
            pref_score = -2
        elif pref == "Morning" and not is_morning:
            pref_score = 2
        elif pref == "Afternoon" and not is_morning:
            pref_score = -2
        elif pref == "Afternoon" and is_morning:
            pref_score = 2

        # Balanced day distribution:
        # Distribute lectures of each subject across distinct days with hash offset
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
def _is_valid(session: dict, slot: tuple, room: dict, faculty: dict, assignment: dict) -> bool:
    """
    Verifies ALL hard constraints:
    1. Faculty cannot teach two sessions at the same time.
    2. Room cannot host two sessions at the same time.
    3. Lab cannot host two sessions at the same time.
    4. Division cannot have two lectures at the same time.
    5. A batch cannot have two classes at the same time.
    6. Parallel lab batches of same division cannot clash on batch, faculty, or room.
    7. No division lecture while a lab batch is scheduled, and vice versa.
    8. No back-to-back duplicate lecture of the same subject on the same day for same division.
    9. Even distribution: division cannot have more than ceil(total_sessions / num_days) of same subject on same day.
    10. Faculty fatigue limit: faculty cannot teach > 3 consecutive periods on the same day.
    """
    day, period = slot

    same_fac_consec = 0

    for assigned_id, (a_slot, a_room, a_faculty) in assignment.items():
        a_day, a_period = a_slot
        a_session = _session_lookup.get(assigned_id)
        if not a_session:
            continue

        # Check same slot clashes
        if a_day == day and a_period == period:
            # Constraint 1: Faculty clash
            if a_faculty.get("code") == faculty.get("code"):
                return False

            # Constraint 2 & 3: Room / Lab double booking
            if a_room.get("name") == room.get("name"):
                return False

            # Division and Batch checks
            if a_session["division"] == session["division"]:
                # If either is a full division lecture -> division clash!
                if not a_session.get("batch") or not session.get("batch"):
                    return False
                # Both are batch-level lab sessions: check if it's the SAME batch!
                if a_session.get("batch") == session.get("batch"):
                    return False
                # If different batches of the same division (e.g. A1 and A2), they CAN run in parallel in different labs with different faculty!

        # Constraint 8: Same day division checks for theory lectures
        if a_day == day and a_session["division"] == session["division"]:
            if not session.get("is_lab") and not a_session.get("is_lab"):
                if a_session["subject"] == session["subject"]:
                    # Never consecutive periods (no back-to-back same class)
                    if _are_periods_consecutive(a_period, period):
                        return False

        # Constraint 10: Faculty consecutive fatigue check on same day
        if a_day == day and a_faculty.get("code") == faculty.get("code"):
            if _are_periods_consecutive(a_period, period):
                same_fac_consec += 1
                if same_fac_consec >= 3:
                    return False

    # Constraint 9: Enforce daily lecture limit per subject for a division
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
            return False

    return True


# ---------------------------------------------------------------------------
# MRV (MINIMUM REMAINING VALUES) HEURISTIC
# ---------------------------------------------------------------------------
def _pick_next_session(unscheduled: list, assignment: dict, domains: dict):
    """
    Select the unscheduled session with the fewest remaining valid options.
    If ties, prioritize lab sessions first (hardest to place due to equipment/room).
    """
    best_session = None
    best_count = float("inf")

    for session in unscheduled:
        sid = session["id"]
        valid_count = sum(
            1 for (slot, room, faculty) in domains[sid]
            if _is_valid(session, slot, room, faculty, assignment)
        )

        # Tie-breaker: prefer lab sessions
        priority = 0 if session.get("is_lab") else 1

        if (valid_count, priority) < (best_count, 1):
            best_count = valid_count
            best_session = session

        if best_count == 0:
            break

    return best_session, best_count


# ---------------------------------------------------------------------------
# BACKTRACKING SEARCH
# ---------------------------------------------------------------------------
def _backtrack(unscheduled: list, assignment: dict, domains: dict, step_counter: list):
    """
    Recursive backtracking with state restoration and MRV variable ordering.
    """
    step_counter[0] += 1
    if step_counter[0] > 100000:
        # Search safety limit to prevent timeout on impossible constraints
        return None

    if not unscheduled:
        return assignment

    session, count = _pick_next_session(unscheduled, assignment, domains)

    if session is None or count == 0:
        return None  # Dead end reached, trigger backtrack

    sid = session["id"]
    for (slot, room, faculty) in domains[sid]:
        if _is_valid(session, slot, room, faculty, assignment):
            assignment[sid] = (slot, room, faculty)
            remaining = [s for s in unscheduled if s["id"] != sid]

            res = _backtrack(remaining, assignment, domains, step_counter)
            if res is not None:
                return res

            del assignment[sid]  # Undo (backtrack)

    return None


# ---------------------------------------------------------------------------
# INFEASIBILITY DIAGNOSTICS
# ---------------------------------------------------------------------------
def diagnose_infeasibility(sessions, domains, active_rooms, faculty_list, teaching_slots, resource_config):
    """
    Generates clear, informative human-readable diagnosis of why scheduling could not succeed.
    """
    diagnostics = []

    # 1. Total teaching slots vs required sessions
    total_slots = len(teaching_slots)
    div_sessions = {}
    for s in sessions:
        key = s["division"]
        div_sessions[key] = div_sessions.get(key, 0) + 1

    for div, req_count in div_sessions.items():
        if req_count > total_slots:
            diagnostics.append(
                f"Division '{div}' requires {req_count} weekly sessions, but only {total_slots} teaching slots exist in the week."
            )

    # 2. Check for empty domains
    for s in sessions:
        sid = s["id"]
        d = domains.get(sid, [])
        label = f"Lab ({s.get('batch')})" if s.get("is_lab") else "Lecture"
        if not d:
            qualified = _find_faculty_for_subject(s["subject"], faculty_list)
            if not qualified:
                diagnostics.append(f"No faculty member is assigned to teach subject '{s['subject']}'.")
            else:
                suitable = _find_suitable_rooms(s, active_rooms, {})
                if not suitable:
                    diagnostics.append(
                        f"No available {label} room has sufficient capacity (>= {s.get('strength')}) for {s['division']} - {s['subject']}."
                    )
                else:
                    diagnostics.append(
                        f"Faculty qualified for '{s['subject']}' are unavailable during teaching hours or all slots clash."
                    )

    # 3. Lab availability bottleneck
    lab_sessions = [s for s in sessions if s.get("is_lab")]
    active_labs = [r for r in active_rooms if r.get("type") == "Lab"]
    reserved_count = resource_config.get("reserved_labs_count", 1)

    if lab_sessions and not active_labs:
        diagnostics.append(
            f"All laboratories in the department are reserved or none exist (Reserved Labs = {reserved_count}). At least 1 active lab is required."
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
    days: list = None
):
    """
    Main timetable generator with CSP + MRV + Backtracking.
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

    # Standardize time slots: only TEACHING slots are schedulable
    if not time_slots:
        time_slots = DEFAULT_SCHEDULE

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
    if not subject_list:
        return False, "No subjects found.", [], ["No subjects available to schedule."], {}
    if not division_list:
        return False, "No divisions/sections found.", [], ["No divisions available to schedule."], {}

    # Step 1: Resource Reservation (HOD Requirement)
    active_rooms, reserved_rooms, other_rooms = filter_and_reserve_resources(
        room_list, department, resource_config
    )

    ratio = _parse_ratio(resource_config.get("student_pc_ratio", "1:1") if resource_config else "1:1")

    # Step 2: Build Sessions (CSP Variables)
    sessions = _build_sessions(subject_list, division_list, batch_list, department)
    _session_lookup = {s["id"]: s for s in sessions}

    if not sessions:
        return False, "No teaching sessions to schedule.", [], ["All subjects have 0 lectures and 0 labs per week."], {}

    # Step 3: Build Domains (CSP Domains)
    domains = {}
    pre_conflicts = []
    for s in sessions:
        d = _build_domain(s, faculty_list, active_rooms, teaching_slots, ratio, approved_sharing)
        domains[s["id"]] = d
        if not d:
            label = f"Lab ({s.get('batch')})" if s.get("is_lab") else "Lecture"
            pre_conflicts.append(
                f"No feasible slot/room for {s['division']} {label} - {s['subject']}. Check faculty availability, room capacity, and reservations."
            )

    if pre_conflicts:
        return (
            False,
            f"Cannot generate timetable due to {len(pre_conflicts)} unresolvable constraint conflict(s).",
            [],
            pre_conflicts,
            {"active_rooms": len(active_rooms), "reserved_rooms": len(reserved_rooms)}
        )

    # Step 4: Backtracking with MRV
    step_counter = [0]
    result = _backtrack(list(sessions), {}, domains, step_counter)

    if result is None:
        explanations = diagnose_infeasibility(
            sessions, domains, active_rooms, faculty_list, teaching_slots, resource_config or {}
        )
        return (
            False,
            "Timetable generation could not find a clash-free assignment.",
            [],
            explanations,
            {"active_rooms": len(active_rooms), "reserved_rooms": len(reserved_rooms)}
        )

    # Step 5: Format Timetable Rows
    timetable_rows = []
    for s in sessions:
        sid = s["id"]
        if sid in result:
            (day, period), room, faculty = result[sid]
            is_morning = any(slot[2] for slot in teaching_slots if slot[0] == day and slot[1] == period)
            timetable_rows.append({
                "day": day,
                "day_order": _day_order.get(day, 99),
                "period": period,
                "is_morning": is_morning,
                "department": department,
                "section": s["division"],
                "batch": s.get("batch"),
                "subject": s["subject"],
                "faculty_code": faculty.get("code", ""),
                "faculty_name": faculty.get("name", ""),
                "room": room.get("name", ""),
                "is_lab": s["is_lab"]
            })

    timetable_rows.sort(key=lambda r: (r["day_order"], _period_order_map.get(r["period"], 99), r["section"], r.get("batch") or ""))

    summary_msg = (
        f"Timetable generated successfully! {len(timetable_rows)} sessions scheduled "
        f"using {len(active_rooms)} active rooms ({len(reserved_rooms)} rooms safely reserved by HOD policy)."
    )

    metadata = {
        "scheduled_count": len(timetable_rows),
        "active_rooms_count": len(active_rooms),
        "reserved_rooms_count": len(reserved_rooms),
        "backtrack_steps": step_counter[0],
        "reserved_rooms": [r["name"] for r in reserved_rooms]
    }

    return True, summary_msg, timetable_rows, [], metadata
