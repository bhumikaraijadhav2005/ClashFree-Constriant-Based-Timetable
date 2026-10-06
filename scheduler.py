# scheduler.py
# This file contains the core scheduling logic.
#
# Concepts used:
#   CSP        — Constraint Satisfaction Problem: we model each class/lab
#                session as a variable that needs a value (day + period + room + faculty).
#   MRV        — Minimum Remaining Values: always schedule the session that
#                has the FEWEST valid options first (hardest to place = first).
#   Backtracking — If we get stuck, undo the last assignment and try another option.

import data as db

# ---------------------------------------------------------------------------
# TEACHING PERIODS
# Only these periods are used by the scheduler.
# Breaks and lunch are NOT in this list — so the scheduler cannot place a class there.
# ---------------------------------------------------------------------------
TEACHING_PERIODS = [
    ("09:00-10:00",  True),   # Morning slot
    ("10:00-11:00",  True),   # Morning slot
    ("11:15-12:15",  True),   # Morning slot (after 11:00-11:15 short break)
    ("13:00-14:00",  False),  # Afternoon slot (after 12:15-13:00 lunch)
    ("14:00-15:00",  False),  # Afternoon slot
    ("15:15-16:15",  False),  # Afternoon slot (after 15:00-15:15 short break)
]

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

# All possible (day, period) combinations = 5 days × 6 periods = 30 slots
ALL_SLOTS = [(day, period) for day in DAYS for (period, _) in TEACHING_PERIODS]

# Map period label → is_morning flag for quick lookup
PERIOD_IS_MORNING = {period: is_morning for (period, is_morning) in TEACHING_PERIODS}


# ---------------------------------------------------------------------------
# HELPER: convert "HH:MM" string → integer minutes since midnight
# ---------------------------------------------------------------------------
def time_to_minutes(time_str):
    """Convert '09:00' → 540 (minutes since midnight)."""
    try:
        h, m = time_str.strip().split(":")
        return int(h) * 60 + int(m)
    except Exception:
        return 0


# ---------------------------------------------------------------------------
# HELPER: check whether a given period falls within a faculty's available hours
# Hard availability — faculty CANNOT teach outside their available hours.
# ---------------------------------------------------------------------------
def faculty_is_available(faculty, period_label):
    """Returns True only if the faculty's working hours cover this period."""
    avail_from = time_to_minutes(faculty.get("available_from", "09:00"))
    avail_to   = time_to_minutes(faculty.get("available_to",   "17:00"))

    # Extract the start time from "HH:MM-HH:MM"
    start_str    = period_label.split("-")[0]
    period_start = time_to_minutes(start_str)

    return avail_from <= period_start < avail_to


# ---------------------------------------------------------------------------
# HELPER: look up which faculty can teach a given subject
# ---------------------------------------------------------------------------
def find_faculty_for_subject(subject_name):
    """Return a list of faculty dicts who teach this subject."""
    return [f for f in db.faculty_list if subject_name in f["subjects"]]


# ---------------------------------------------------------------------------
# HELPER: find suitable rooms for a session
# ---------------------------------------------------------------------------
def find_rooms_for_session(is_lab, section_strength):
    """
    Return rooms that:
      - Are the right type (Lab for lab sessions, Classroom for lectures)
      - Have enough capacity for the section
    """
    needed_type = "Lab" if is_lab else "Classroom"
    return [r for r in db.room_list
            if r["type"] == needed_type and r["capacity"] >= section_strength]


# ---------------------------------------------------------------------------
# BUILD SESSIONS
# A "session" is one individual class or lab slot to be placed in the timetable.
# This is the CSP "variables" step — each session is a variable.
# ---------------------------------------------------------------------------
def build_sessions():
    """
    Create the list of all sessions that need to be scheduled.

    For each section × subject, create:
      - N lecture session objects  (N = lectures_per_week)
      - M lab session objects      (M = labs_per_week)
    """
    sessions = []
    session_id = 0

    for section in db.section_list:
        for subject in db.subject_list:

            # Create one session object per lecture needed per week
            for i in range(subject["lectures_per_week"]):
                sessions.append({
                    "id":      "s" + str(session_id),
                    "section": section["name"],
                    "subject": subject["name"],
                    "is_lab":  False,
                    "index":   i  # which lecture of the week this is
                })
                session_id += 1

            # Create one session object per lab session needed per week
            for i in range(subject["labs_per_week"]):
                sessions.append({
                    "id":      "s" + str(session_id),
                    "section": section["name"],
                    "subject": subject["name"],
                    "is_lab":  True,
                    "index":   i
                })
                session_id += 1

    return sessions


# ---------------------------------------------------------------------------
# BUILD DOMAIN FOR ONE SESSION
# The "domain" = all possible (slot, room, faculty) tuples for this session.
# This is the CSP "domains" step.
# ---------------------------------------------------------------------------
def build_domain(session):
    """
    For a given session, return all possible assignments:
        [ (slot, room, faculty), ... ]
    where slot = ("Monday", "09:00-10:00")

    Also applies the soft constraint: morning-preferring faculty see
    morning slots sorted first, so the scheduler tries those first.
    """
    section_obj = next(
        (s for s in db.section_list if s["name"] == session["section"]), None
    )
    section_strength = section_obj["strength"] if section_obj else 0

    possible_faculty = find_faculty_for_subject(session["subject"])
    possible_rooms   = find_rooms_for_session(session["is_lab"], section_strength)

    domain = []

    for (day, period) in ALL_SLOTS:
        for room in possible_rooms:
            for faculty in possible_faculty:

                # HARD constraint: faculty must be available in this period
                if not faculty_is_available(faculty, period):
                    continue

                domain.append(((day, period), room, faculty))

    # --- SOFT CONSTRAINT: prefer morning for "Morning" faculty ---
    # Sort the domain so that morning slots come first for morning-preferring faculty.
    # This doesn't guarantee morning — it just makes the scheduler try them first.
    # If morning slots are all taken, it will fall back to afternoon slots.
    def preference_key(entry):
        slot, room, faculty = entry
        day, period = slot
        is_morning    = PERIOD_IS_MORNING.get(period, False)
        wants_morning = faculty.get("preferred_time") == "Morning"

        # Priority 0 = try first, Priority 1 = try later
        if wants_morning and is_morning:
            return 0   # faculty wants morning AND this IS morning → try first
        elif wants_morning and not is_morning:
            return 1   # faculty wants morning but this is afternoon → try later
        return 0       # no preference → no sorting penalty

    domain.sort(key=preference_key)
    return domain


# ---------------------------------------------------------------------------
# HARD CONSTRAINT CHECKER
# ---------------------------------------------------------------------------
def is_valid(session, slot, room, faculty, assignment):
    """
    Check whether assigning (slot, room, faculty) to this session is valid
    given what has already been assigned.

    Hard constraints checked:
      1. Same section cannot have two classes at the same time slot.
      2. Same room cannot be used by two sessions at the same time slot.
      3. Same faculty cannot teach two sessions at the same time slot.

    Returns True if no constraint is violated.
    """
    day, period = slot

    for assigned_id, (a_slot, a_room, a_faculty) in assignment.items():
        a_day, a_period = a_slot

        # Only matters if they are in the SAME time slot
        if a_day == day and a_period == period:

            # Find the session that owns this assignment
            a_session = _session_lookup.get(assigned_id)
            if a_session is None:
                continue

            # Constraint 1: Same section → clash
            if a_session["section"] == session["section"]:
                return False

            # Constraint 2: Same room → clash
            if a_room["name"] == room["name"]:
                return False

            # Constraint 3: Same faculty → clash
            if a_faculty["code"] == faculty["code"]:
                return False

    return True  # All constraints satisfied


# We store sessions in a dict for O(1) lookup during constraint checking
_session_lookup = {}


# ---------------------------------------------------------------------------
# MRV — Minimum Remaining Values
# Select the HARDEST unscheduled session first (fewest valid options).
# ---------------------------------------------------------------------------
def pick_next_session(unscheduled, assignment, domains):
    """
    MRV heuristic:

    For each unscheduled session, count how many valid domain values remain
    given the current (partial) assignment.

    Pick the session with the FEWEST remaining valid options.

    Why? Sessions with fewer choices are at risk of becoming impossible.
    Scheduling them first lets us discover dead-ends early, saving time.

    Example:
        DSA Lecture  → 18 remaining options
        DBMS Lab     →  4 remaining options   ← MRV picks this one
        OS Lecture   → 12 remaining options
    """
    best_session = None
    best_count   = float("inf")  # start with "infinity"

    for session in unscheduled:
        # Count how many domain values are still valid for this session
        valid_count = 0
        for (slot, room, faculty) in domains[session["id"]]:
            if is_valid(session, slot, room, faculty, assignment):
                valid_count += 1

        # Keep track of the session with the smallest count
        if valid_count < best_count:
            best_count   = valid_count
            best_session = session

        # Optimization: if count is 0, we've already failed — stop early
        if best_count == 0:
            break

    return best_session, best_count


# ---------------------------------------------------------------------------
# BACKTRACKING SEARCH (recursive)
# ---------------------------------------------------------------------------
def backtrack(unscheduled, assignment, domains):
    """
    Recursive backtracking:

    Step 1: If nothing is left to schedule → SUCCESS! Return the assignment.
    Step 2: Use MRV to choose which session to schedule next.
    Step 3: If no valid options exist for that session → FAILURE (return None).
    Step 4: Try each (slot, room, faculty) option for the chosen session.
    Step 5: Check hard constraints. If valid, assign it.
    Step 6: Recurse to schedule the remaining sessions.
    Step 7: If recursion succeeds → bubble the success up.
    Step 8: If recursion fails → UNDO the assignment (backtrack) and try next option.
    Step 9: If all options tried and none worked → return None (failure).
    """

    # Step 1: Base case — all sessions are scheduled
    if not unscheduled:
        return assignment  # SUCCESS

    # Step 2: MRV — pick the session with the fewest remaining valid options
    session, remaining_count = pick_next_session(unscheduled, assignment, domains)

    # Step 3: If no valid option exists for this session → fail immediately
    if session is None or remaining_count == 0:
        return None  # Dead end — trigger backtracking in the caller

    # Step 4: Try each possible assignment for this session
    for (slot, room, faculty) in domains[session["id"]]:

        # Step 5: Check hard constraints against current assignments
        if is_valid(session, slot, room, faculty, assignment):

            # Assign this option (tentatively)
            assignment[session["id"]] = (slot, room, faculty)

            # Remove this session from the "still to schedule" list
            remaining = [s for s in unscheduled if s["id"] != session["id"]]

            # Step 6: Recurse — try to schedule all remaining sessions
            result = backtrack(remaining, assignment, domains)

            # Step 7: If recursion succeeded, bubble the result up
            if result is not None:
                return result

            # Step 8: Recursion failed — undo this assignment (BACKTRACK)
            del assignment[session["id"]]

    # Step 9: No valid assignment worked for this session — signal failure
    return None


# ---------------------------------------------------------------------------
# MAIN FUNCTION
# ---------------------------------------------------------------------------
def generate_timetable():
    """
    Main function called by app.py.
    Returns: (success: bool, message: str)
    """
    global _session_lookup

    # Basic checks
    if not db.data_loaded:
        return False, "No data loaded. Please upload an Excel file first."
    if not db.faculty_list:
        return False, "No faculty found."
    if not db.room_list:
        return False, "No rooms found."
    if not db.subject_list:
        return False, "No subjects found."
    if not db.section_list:
        return False, "No sections found."

    # Step A: Build all sessions to schedule (CSP Variables)
    sessions = build_sessions()
    _session_lookup = {s["id"]: s for s in sessions}

    if not sessions:
        return False, "No sessions to schedule. Check that subjects have at least 1 lecture per week."

    # Step B: Build domain for each session (CSP Domains)
    domains = {}
    for session in sessions:
        d = build_domain(session)
        domains[session["id"]] = d

        # If a session has zero options before we even start → tell user why
        if not d:
            label = "Lab" if session["is_lab"] else "Lecture"
            return False, (
                "Cannot find any valid slot for: "
                + session["section"] + " / " + session["subject"] + " (" + label + "). "
                + "Possible reasons: no faculty assigned to this subject, "
                + "no room of the right type with enough capacity, "
                + "or faculty availability is too restricted."
            )

    # Step C: Run the backtracking search
    assignment = {}
    result = backtrack(list(sessions), assignment, domains)

    if result is None:
        return False, (
            "Unable to generate a complete timetable. "
            "The constraints may be too tight. "
            "Try: adding more rooms, adjusting faculty availability, "
            "or reducing lectures per week."
        )

    # Step D: Convert raw assignment dict → readable timetable rows
    timetable_rows = []
    for session in sessions:
        if session["id"] in result:
            slot, room, faculty = result[session["id"]]
            day, period = slot
            timetable_rows.append({
                "day":          day,
                "period":       period,
                "section":      session["section"],
                "subject":      session["subject"],
                "faculty_code": faculty["code"],
                "room":         room["name"],
                "is_lab":       session["is_lab"]
            })

    # Sort for nice display: day order, then period, then section name
    day_order = {d: i for i, d in enumerate(DAYS)}
    timetable_rows.sort(
        key=lambda r: (day_order.get(r["day"], 99), r["period"], r["section"])
    )

    # Save to global store so the Flask app can show it
    db.timetable = timetable_rows

    return True, (
        "Timetable generated successfully! "
        + str(len(timetable_rows)) + " sessions scheduled."
    )
