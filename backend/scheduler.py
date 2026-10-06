# backend/scheduler.py
# Core scheduling engine — CSP + MRV + Backtracking.
# This file is PRESERVED from the original and adapted to work with
# data passed in as dicts (from Supabase) instead of the old data.py module.

# ---------------------------------------------------------------------------
# TEACHING PERIODS — only these are used. Breaks/lunch are excluded so
# the scheduler structurally cannot assign a class during them.
# ---------------------------------------------------------------------------
TEACHING_PERIODS = [
    ("09:00-10:00",  True),   # Morning
    ("10:00-11:00",  True),   # Morning
    ("11:15-12:15",  True),   # Morning (after 11:00-11:15 short break)
    ("13:00-14:00",  False),  # Afternoon (after 12:15-13:00 lunch)
    ("14:00-15:00",  False),  # Afternoon
    ("15:15-16:15",  False),  # Afternoon (after 15:00-15:15 short break)
]

# Full schedule with break/lunch labels — used for display on the timetable
FULL_SCHEDULE = [
    {"period": "09:00-10:00",  "type": "TEACHING"},
    {"period": "10:00-11:00",  "type": "TEACHING"},
    {"period": "11:00-11:15",  "type": "SHORT_BREAK"},
    {"period": "11:15-12:15",  "type": "TEACHING"},
    {"period": "12:15-13:00",  "type": "LUNCH"},
    {"period": "13:00-14:00",  "type": "TEACHING"},
    {"period": "14:00-15:00",  "type": "TEACHING"},
    {"period": "15:00-15:15",  "type": "SHORT_BREAK"},
    {"period": "15:15-16:15",  "type": "TEACHING"},
]

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
DAY_ORDER = {d: i for i, d in enumerate(DAYS)}

# All schedulable (day, period) combinations
ALL_SLOTS = [(day, period) for day in DAYS for (period, _) in TEACHING_PERIODS]

# Quick lookup: period → is_morning
PERIOD_IS_MORNING = {p: m for (p, m) in TEACHING_PERIODS}

# Global session lookup (filled during generate)
_session_lookup = {}


def _time_to_minutes(time_str: str) -> int:
    """'09:00' → 540"""
    try:
        h, m = time_str.strip().split(":")
        return int(h) * 60 + int(m)
    except Exception:
        return 0


def _faculty_is_available(faculty: dict, period_label: str) -> bool:
    """
    Hard availability: Return True only if the faculty can teach in this period.
    Checks available_from / available_to fields.
    """
    avail_from = _time_to_minutes(faculty.get("available_from") or "09:00")
    avail_to   = _time_to_minutes(faculty.get("available_to")   or "17:00")
    period_start = _time_to_minutes(period_label.split("-")[0])
    return avail_from <= period_start < avail_to


def _find_faculty_for_subject(subject_name: str, faculty_list: list) -> list:
    """Return all faculty who can teach this subject."""
    result = []
    for f in faculty_list:
        # subjects field is a list like ["DSA", "OS"]
        subjects = f.get("subjects") or []
        if isinstance(subjects, str):
            subjects = [s.strip() for s in subjects.split(",")]
        if subject_name in subjects:
            result.append(f)
    return result


def _find_rooms_for_session(is_lab: bool, section_strength: int, room_list: list) -> list:
    """Return rooms of the right type with enough capacity."""
    needed_type = "Lab" if is_lab else "Classroom"
    return [
        r for r in room_list
        if r.get("type") == needed_type and (r.get("capacity") or 0) >= section_strength
    ]


# ---------------------------------------------------------------------------
# BUILD SESSIONS  (CSP Variables)
# ---------------------------------------------------------------------------
def _build_sessions(faculty_list, room_list, subject_list, section_list):
    """
    Each session = one class/lab slot that must be placed in the timetable.
    Returns list of session dicts.
    """
    sessions = []
    sid = 0
    for section in section_list:
        for subject in subject_list:
            # Lecture sessions
            for i in range(subject.get("lectures_per_week") or 0):
                sessions.append({
                    "id":      f"s{sid}",
                    "section": section["name"],
                    "subject": subject["name"],
                    "is_lab":  False,
                    "index":   i,
                })
                sid += 1
            # Lab sessions
            for i in range(subject.get("labs_per_week") or 0):
                sessions.append({
                    "id":      f"s{sid}",
                    "section": section["name"],
                    "subject": subject["name"],
                    "is_lab":  True,
                    "index":   i,
                })
                sid += 1
    return sessions


# ---------------------------------------------------------------------------
# BUILD DOMAIN  (CSP Domains)
# ---------------------------------------------------------------------------
def _build_domain(session, faculty_list, room_list, section_list):
    """
    Return all valid (slot, room, faculty) options for a session.
    Applies hard availability and sorts by soft preference.
    """
    sec = next((s for s in section_list if s["name"] == session["section"]), None)
    strength = (sec.get("strength") or 0) if sec else 0

    possible_faculty = _find_faculty_for_subject(session["subject"], faculty_list)
    possible_rooms   = _find_rooms_for_session(session["is_lab"], strength, room_list)

    domain = []
    for (day, period) in ALL_SLOTS:
        for room in possible_rooms:
            for faculty in possible_faculty:
                if _faculty_is_available(faculty, period):
                    domain.append(((day, period), room, faculty))

    # Soft preference: morning-preferring faculty → sort morning slots first
    def sort_key(entry):
        (day, period), room, faculty = entry
        is_morning    = PERIOD_IS_MORNING.get(period, False)
        pref          = (faculty.get("preferred_time") or "Any")
        if pref == "Morning" and is_morning:
            return 0
        if pref == "Morning" and not is_morning:
            return 1
        if pref == "Afternoon" and not is_morning:
            return 0
        if pref == "Afternoon" and is_morning:
            return 1
        return 0

    domain.sort(key=sort_key)
    return domain


# ---------------------------------------------------------------------------
# HARD CONSTRAINT CHECKER
# ---------------------------------------------------------------------------
def _is_valid(session, slot, room, faculty, assignment):
    """
    Returns True if (slot, room, faculty) does not clash with existing assignments.

    Checks:
      1. Same section → no two classes at same time
      2. Same room    → not double-booked
      3. Same faculty → not double-booked
    """
    day, period = slot
    for assigned_id, (a_slot, a_room, a_faculty) in assignment.items():
        a_day, a_period = a_slot
        if a_day == day and a_period == period:
            a_session = _session_lookup.get(assigned_id)
            if not a_session:
                continue
            if a_session["section"] == session["section"]:
                return False
            if a_room["name"] == room["name"]:
                return False
            if a_faculty.get("code") == faculty.get("code"):
                return False
    return True


# ---------------------------------------------------------------------------
# MRV — pick the session with the fewest remaining valid options
# ---------------------------------------------------------------------------
def _pick_next_session(unscheduled, assignment, domains):
    """
    MRV (Minimum Remaining Values):
    Count valid options for each unscheduled session.
    Pick the one with the FEWEST options.
    Schedule it first — hardest to place → most likely to cause failure if left later.
    """
    best_session = None
    best_count   = float("inf")

    for session in unscheduled:
        count = sum(
            1 for (slot, room, faculty) in domains[session["id"]]
            if _is_valid(session, slot, room, faculty, assignment)
        )
        if count < best_count:
            best_count   = count
            best_session = session
        if best_count == 0:
            break

    return best_session, best_count


# ---------------------------------------------------------------------------
# BACKTRACKING SEARCH
# ---------------------------------------------------------------------------
def _backtrack(unscheduled, assignment, domains):
    """
    Recursive backtracking search.
    Step 1: If nothing left → success.
    Step 2: MRV picks the next session to schedule.
    Step 3: Try each (slot, room, faculty) in the domain.
    Step 4: Check constraints. If valid, assign.
    Step 5: Recurse. If later failure, undo (backtrack) and try next.
    """
    if not unscheduled:
        return assignment  # All sessions scheduled!

    session, count = _pick_next_session(unscheduled, assignment, domains)

    if session is None or count == 0:
        return None  # Dead-end

    for (slot, room, faculty) in domains[session["id"]]:
        if _is_valid(session, slot, room, faculty, assignment):
            assignment[session["id"]] = (slot, room, faculty)
            remaining = [s for s in unscheduled if s["id"] != session["id"]]
            result = _backtrack(remaining, assignment, domains)
            if result is not None:
                return result
            del assignment[session["id"]]  # Backtrack

    return None  # No option worked → signal failure


# ---------------------------------------------------------------------------
# PUBLIC ENTRY POINT
# ---------------------------------------------------------------------------
def generate_timetable(faculty_list, room_list, subject_list, section_list):
    """
    Main scheduling function.
    Accepts data directly (from Supabase) instead of the old global data.py.
    Returns: (success: bool, message: str, timetable_rows: list, conflicts: list)
    """
    global _session_lookup

    conflicts = []

    if not faculty_list:
        return False, "No faculty data found.", [], ["No faculty loaded."]
    if not room_list:
        return False, "No rooms found.", [], ["No rooms loaded."]
    if not subject_list:
        return False, "No subjects found.", [], ["No subjects loaded."]
    if not section_list:
        return False, "No sections found.", [], ["No sections loaded."]

    # Step A: Build all sessions (CSP Variables)
    sessions = _build_sessions(faculty_list, room_list, subject_list, section_list)
    _session_lookup = {s["id"]: s for s in sessions}

    if not sessions:
        return False, "No sessions to schedule.", [], ["All subjects have 0 lectures and 0 labs per week."]

    # Step B: Build domains for each session (CSP Domains)
    domains = {}
    for session in sessions:
        d = _build_domain(session, faculty_list, room_list, section_list)
        domains[session["id"]] = d
        if not d:
            label = "Lab" if session["is_lab"] else "Lecture"
            msg = (
                f"No valid slot for {session['section']} / {session['subject']} ({label}). "
                f"Check faculty assignment, room availability, and capacity."
            )
            conflicts.append(msg)

    if conflicts:
        return False, "Cannot generate timetable due to conflicts.", [], conflicts

    # Step C: Run backtracking search
    result = _backtrack(list(sessions), {}, domains)

    if result is None:
        return False, (
            "Unable to generate a complete timetable. "
            "Constraints may be too tight. Try adding more rooms or adjusting availability."
        ), [], ["Backtracking exhausted all possibilities. Constraints too tight."]

    # Step D: Convert assignments to timetable rows
    DAYS_ORDER = {d: i for i, d in enumerate(DAYS)}
    timetable_rows = []
    for session in sessions:
        if session["id"] in result:
            (day, period), room, faculty = result[session["id"]]
            timetable_rows.append({
                "day":          day,
                "day_order":    DAYS_ORDER.get(day, 99),
                "period":       period,
                "is_morning":   PERIOD_IS_MORNING.get(period, False),
                "section":      session["section"],
                "subject":      session["subject"],
                "faculty_code": faculty.get("code", ""),
                "faculty_name": faculty.get("name", ""),
                "room":         room.get("name", ""),
                "is_lab":       session["is_lab"],
            })

    timetable_rows.sort(key=lambda r: (r["day_order"], r["period"], r["section"]))

    return (
        True,
        f"Timetable generated successfully! {len(timetable_rows)} sessions scheduled.",
        timetable_rows,
        []
    )

