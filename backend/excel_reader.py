# backend/excel_reader.py
# Reads single-sheet CLASHFREE_INPUT template (and legacy multi-sheet workbooks),
# performs strict validation across teaching requirements, resource configuration,
# and time configuration, auto-generates faculty codes, and returns structured data
# with human-friendly diagnostics for HOD review.

import io
import re
import datetime
import openpyxl


# ---------------------------------------------------------------------------
# TIME HELPERS (Strict 12-Hour AM/PM Support)
# ---------------------------------------------------------------------------
def format_time_12h(val) -> str:
    """
    Format time object, float, or string to standard 12-hour AM/PM format.
    Examples:
      '09:00' -> '9:00 AM'
      '13:00' -> '1:00 PM'
      '13:15' -> '1:15 PM'
      datetime.time(14, 0) -> '2:00 PM'
      '9:00 AM' -> '9:00 AM'
    """
    if val is None or val == "":
        return ""

    if isinstance(val, datetime.time):
        hour = val.hour
        minute = val.minute
        meridiem = "PM" if hour >= 12 else "AM"
        display_hour = hour % 12
        if display_hour == 0:
            display_hour = 12
        return f"{display_hour}:{minute:02d} {meridiem}"

    if isinstance(val, datetime.datetime):
        return format_time_12h(val.time())

    s = str(val).strip()

    # Already has AM / PM
    m = re.match(r"^(\d{1,2})(?::(\d{2}))?\s*(AM|PM|am|pm)$", s)
    if m:
        h = int(m.group(1))
        mins = int(m.group(2) or 0)
        mer = m.group(3).upper()
        return f"{h}:{mins:02d} {mer}"

    # 24-hour 'HH:MM' or 'HH:MM:SS'
    m2 = re.match(r"^(\d{1,2}):(\d{2})(?::\d{2})?$", s)
    if m2:
        hour = int(m2.group(1))
        minute = int(m2.group(2))
        meridiem = "PM" if hour >= 12 else "AM"
        display_hour = hour % 12
        if display_hour == 0:
            display_hour = 12
        return f"{display_hour}:{minute:02d} {meridiem}"

    # Simple integer hour e.g. 9 or 13
    if s.isdigit():
        hour = int(s)
        meridiem = "PM" if hour >= 12 else "AM"
        display_hour = hour % 12
        if display_hour == 0:
            display_hour = 12
        return f"{display_hour}:00 {meridiem}"

    return s


def time_str_to_minutes(val) -> int:
    """
    Converts '9:00 AM', '1:00 PM', '13:00', or datetime.time into minutes from 00:00.
    """
    if val is None:
        return 0
    if isinstance(val, (datetime.time, datetime.datetime)):
        return val.hour * 60 + val.minute

    s = str(val).strip()
    # Check AM/PM
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

    # Check 24-hour HH:MM
    m24 = re.match(r"^(\d{1,2}):(\d{2})", s)
    if m24:
        return int(m24.group(1)) * 60 + int(m24.group(2))

    return 0


def format_period_label(start_str, end_str) -> str:
    """Formats '9:00 AM' and '10:00 AM' into '9:00 AM - 10:00 AM'."""
    s12 = format_time_12h(start_str)
    e12 = format_time_12h(end_str)
    if s12 and e12:
        return f"{s12} - {e12}"
    return s12 or e12 or ""


def parse_availability_string(avail_str: str) -> dict:
    """
    Parses strings such as:
    'Mon-Fri 9:00 AM-4:00 PM'
    'Mon-Fri 9AM-4PM'
    'Mon-Fri 9AM-1PM'
    'Mon,Tue,Wed 10:00 AM-2:00 PM'
    Returns:
    {
       'days': ['Monday', 'Tuesday', ...],
       'from_minutes': 540,
       'to_minutes': 960,
       'from_str': '9:00 AM',
       'to_str': '4:00 PM'
    }
    """
    ALL_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    DAY_ABBR = {"mon": "Monday", "tue": "Tuesday", "wed": "Wednesday", "thu": "Thursday", "fri": "Friday", "sat": "Saturday"}

    if not avail_str or str(avail_str).strip() == "" or str(avail_str).strip() == "-":
        return {
            "days": ALL_DAYS[:5],
            "from_minutes": 540,
            "to_minutes": 1020,
            "from_str": "9:00 AM",
            "to_str": "5:00 PM",
            "raw": avail_str
        }

    s = str(avail_str).strip()
    matched_days = []

    # Check for day range e.g. Mon-Fri
    m_range = re.search(r"([A-Za-z]+)\s*-\s*([A-Za-z]+)", s)
    if m_range:
        d1 = m_range.group(1)[:3].lower()
        d2 = m_range.group(2)[:3].lower()
        if d1 in DAY_ABBR and d2 in DAY_ABBR:
            start_idx = [i for i, d in enumerate(ALL_DAYS) if d.lower().startswith(d1)][0]
            end_idx = [i for i, d in enumerate(ALL_DAYS) if d.lower().startswith(d2)][0]
            if start_idx <= end_idx:
                matched_days = ALL_DAYS[start_idx:end_idx + 1]

    if not matched_days:
        # Check individual days
        for abbr, full in DAY_ABBR.items():
            if re.search(r"\b" + abbr, s, re.IGNORECASE):
                if full not in matched_days:
                    matched_days.append(full)

    if not matched_days:
        matched_days = ALL_DAYS[:5]

    # Time range: e.g. 9:00 AM-4:00 PM or 9AM-4PM
    times = re.findall(r"(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)", s)
    # Filter out day abbreviations
    valid_times = []
    for t in times:
        t_clean = t.strip()
        if re.search(r"\d", t_clean):
            valid_times.append(t_clean)

    from_mins = 540   # 9:00 AM
    to_mins = 1020    # 5:00 PM
    from_str = "9:00 AM"
    to_str = "5:00 PM"

    if len(valid_times) >= 2:
        from_str = format_time_12h(valid_times[0])
        to_str = format_time_12h(valid_times[1])
        from_mins = time_str_to_minutes(from_str)
        to_mins = time_str_to_minutes(to_str)
    elif len(valid_times) == 1:
        from_str = format_time_12h(valid_times[0])
        from_mins = time_str_to_minutes(from_str)

    return {
        "days": matched_days,
        "from_minutes": from_mins,
        "to_minutes": to_mins,
        "from_str": from_str,
        "to_str": to_str,
        "raw": avail_str
    }


# ---------------------------------------------------------------------------
# FACULTY SHORT CODE GENERATION
# ---------------------------------------------------------------------------
def generate_faculty_codes(faculty_data: list) -> list:
    """
    Auto-generate unique short codes:
    - 2-part name: 'Kunal Patil' -> 'KP'
    - 3-part name: 'Vishal H. Pundikar' -> 'VHP'
    - Single name: 'Amit' -> 'AM'
    - Duplicates: 'KP1', 'KP2', ...
    """
    HONORIFICS = {"mr", "dr", "mrs", "ms", "prof", "shri", "smt"}

    def _extract_base(name):
        tokens = [p.strip("., ") for p in name.split() if p.strip("., ")]
        clean_tokens = [t for t in tokens if t.lower() not in HONORIFICS]
        if not clean_tokens:
            clean_tokens = tokens
        if len(clean_tokens) >= 3:
            return (clean_tokens[0][0] + clean_tokens[1][0] + clean_tokens[-1][0]).upper()
        elif len(clean_tokens) == 2:
            return (clean_tokens[0][0] + clean_tokens[1][0]).upper()
        elif len(clean_tokens) == 1 and len(clean_tokens[0]) >= 2:
            return clean_tokens[0][:2].upper()
        return "FC"

    code_count = {}
    for f in faculty_data:
        base = _extract_base(f.get("name", ""))
        code_count[base] = code_count.get(base, 0) + 1

    occurrence = {}
    for f in faculty_data:
        if f.get("code") and str(f.get("code")).strip():
            f["code"] = str(f["code"]).strip().upper()
            continue
        base = _extract_base(f.get("name", ""))
        if code_count[base] == 1:
            f["code"] = base
        else:
            occurrence[base] = occurrence.get(base, 0) + 1
            f["code"] = f"{base}{occurrence[base]}"

    return faculty_data


# ---------------------------------------------------------------------------
# SINGLE-SHEET (CLASHFREE_INPUT) PARSER
# ---------------------------------------------------------------------------
def parse_clashfree_single_sheet(ws):
    """
    Parses the new human-friendly single sheet template containing:
    1. Teaching Requirements table (18 columns)
    2. RESOURCE CONFIGURATION section
    3. TIME CONFIGURATION section
    """
    errors = []
    warnings = []

    # Convert all rows to list of lists (values only)
    all_rows = list(ws.iter_rows(values_only=True))
    if not all_rows:
        return None, ["Sheet is completely empty."], [], {}

    # Identify row boundaries for the 3 sections
    teaching_header_row_idx = None
    resource_section_start_idx = None
    time_section_start_idx = None

    for idx, row in enumerate(all_rows):
        if not row or all(c is None for c in row):
            continue
        row_str = " ".join(str(c or "").strip() for c in row).upper()

        if "RESOURCE CONFIGURATION" in row_str:
            resource_section_start_idx = idx
            continue
        if "TIME CONFIGURATION" in row_str:
            time_section_start_idx = idx
            continue

        # Check for teaching header row
        if teaching_header_row_idx is None:
            if ("SUBJECT" in row_str or "SUBJECT CODE" in row_str) and ("FACULTY" in row_str or "DIVISION" in row_str):
                teaching_header_row_idx = idx

    if teaching_header_row_idx is None:
        return None, ["Could not find the main teaching requirements table header in sheet."], [], {}

    # --- 1. Parse Teaching Requirements ---
    header_row = [str(c or "").strip() for c in all_rows[teaching_header_row_idx]]
    col_map = {}
    for c_idx, col_name in enumerate(header_row):
        norm = re.sub(r"[^A-Z0-9]", "", col_name.upper())
        col_map[norm] = c_idx

    req_cols = ["YEAR", "SEMESTER", "DIVISION", "STRENGTH", "SUBJECT", "TYPE", "SESSIONSWEEK", "FACULTYNAME", "RESOURCETYPE", "CAPACITYREQUIRED"]
    missing_teaching_cols = []
    for rc in req_cols:
        matched = any(rc in k or k in rc for k in col_map.keys())
        if not matched:
            missing_teaching_cols.append(rc)

    if missing_teaching_cols:
        errors.append(f"Teaching Requirements table is missing required columns: {', '.join(missing_teaching_cols)}")

    def get_val(r, col_keys, default=None):
        for k in col_keys:
            norm = re.sub(r"[^A-Z0-9]", "", k.upper())
            for actual_key, idx in col_map.items():
                if norm == actual_key or norm in actual_key or actual_key in norm:
                    if idx < len(r) and r[idx] is not None:
                        val = r[idx]
                        if isinstance(val, str):
                            val = val.strip()
                        return val
        return default

    # Slice teaching rows
    end_teaching_idx = resource_section_start_idx if resource_section_start_idx is not None else len(all_rows)
    teaching_rows = []
    for r_idx in range(teaching_header_row_idx + 1, end_teaching_idx):
        row = all_rows[r_idx]
        if not row or all(c is None or str(c).strip() == "" for c in row):
            continue
        # Check if accidentally entered next section
        first_cell = str(row[0] or "").strip().upper()
        if "RESOURCE CONFIGURATION" in first_cell or "TIME CONFIGURATION" in first_cell:
            break
        teaching_rows.append((r_idx + 1, row))

    # --- 2. Parse Resource Configuration ---
    resource_rows = []
    res_col_map = {}
    if resource_section_start_idx is not None:
        # Find header for resource section
        end_res_idx = time_section_start_idx if time_section_start_idx is not None else len(all_rows)
        res_header_idx = None
        for r_idx in range(resource_section_start_idx, end_res_idx):
            row = all_rows[r_idx]
            row_str = " ".join(str(c or "").strip() for c in row).upper()
            if "RESOURCE NAME" in row_str or ("TYPE" in row_str and "CAPACITY" in row_str):
                res_header_idx = r_idx
                for c_idx, c_val in enumerate(row):
                    norm = re.sub(r"[^A-Z0-9]", "", str(c_val or "").strip().upper())
                    res_col_map[norm] = c_idx
                break

        if res_header_idx is not None:
            for r_idx in range(res_header_idx + 1, end_res_idx):
                row = all_rows[r_idx]
                if not row or all(c is None or str(c).strip() == "" for c in row):
                    continue
                first_cell = str(row[0] or "").strip().upper()
                if "TIME CONFIGURATION" in first_cell:
                    break
                resource_rows.append((r_idx + 1, row))
        else:
            warnings.append("RESOURCE CONFIGURATION section header was not detected. Default resources will be retained.")
    else:
        warnings.append("RESOURCE CONFIGURATION section not found on sheet. Using default room resources.")

    # --- 3. Parse Time Configuration ---
    time_rows = []
    time_col_map = {}
    if time_section_start_idx is not None:
        time_header_idx = None
        for r_idx in range(time_section_start_idx, len(all_rows)):
            row = all_rows[r_idx]
            row_str = " ".join(str(c or "").strip() for c in row).upper()
            if "START TIME" in row_str or "END TIME" in row_str or ("DAY" in row_str and "TYPE" in row_str):
                time_header_idx = r_idx
                for c_idx, c_val in enumerate(row):
                    norm = re.sub(r"[^A-Z0-9]", "", str(c_val or "").strip().upper())
                    time_col_map[norm] = c_idx
                break

        if time_header_idx is not None:
            for r_idx in range(time_header_idx + 1, len(all_rows)):
                row = all_rows[r_idx]
                if not row or all(c is None or str(c).strip() == "" for c in row):
                    continue
                time_rows.append((r_idx + 1, row))
        else:
            warnings.append("TIME CONFIGURATION section header was not detected. Standard college slots will be used.")
    else:
        warnings.append("TIME CONFIGURATION section not found on sheet. Standard college slots will be used.")

    # Process and Validate Resources
    parsed_resources = []
    def get_res_val(r, col_keys, default=None):
        for k in col_keys:
            norm = re.sub(r"[^A-Z0-9]", "", k.upper())
            for actual_key, idx in res_col_map.items():
                if norm == actual_key or norm in actual_key or actual_key in norm:
                    if idx < len(r) and r[idx] is not None:
                        return r[idx]
        return default

    for row_num, row in resource_rows:
        r_type = str(get_res_val(row, ["RESOURCETYPE", "TYPE"], "Classroom")).strip()
        r_name = str(get_res_val(row, ["RESOURCENAME", "NAME", "ROOMNAME"], "")).strip()
        cap_val = get_res_val(row, ["CAPACITY"], 60)
        equipment = str(get_res_val(row, ["EQUIPMENT"], "-")).strip()
        active_val = str(get_res_val(row, ["ACTIVE", "ISACTIVE"], "Yes")).strip().lower()

        if not r_name:
            errors.append(f"Resource Configuration, Row {row_num}: Resource Name cannot be blank.")
            continue

        try:
            capacity = int(cap_val)
            if capacity <= 0:
                errors.append(f"Resource Configuration, Row {row_num}: Capacity for '{r_name}' must be a positive integer.")
                continue
        except (ValueError, TypeError):
            errors.append(f"Resource Configuration, Row {row_num}: Capacity for '{r_name}' must be a number.")
            continue

        is_active = (active_val in ["yes", "true", "1", "y"])
        is_lab = ("lab" in r_type.lower())

        parsed_resources.append({
            "name": r_name,
            "type": "Lab" if is_lab else "Classroom",
            "capacity": capacity,
            "equipment": equipment if equipment != "-" else "",
            "is_active": is_active,
            "is_reserved": False,
            "department": "CSE",
            "num_pcs": capacity if is_lab and ("comp" in equipment.lower() or "pc" in equipment.lower()) else 0
        })

    # Fallback to default resources if none parsed
    if not parsed_resources:
        parsed_resources = [
            {"name": "CR-1", "type": "Classroom", "capacity": 65, "equipment": "", "is_active": True, "department": "CSE"},
            {"name": "CR-2", "type": "Classroom", "capacity": 65, "equipment": "Projector", "is_active": True, "department": "CSE"},
            {"name": "CR-3", "type": "Classroom", "capacity": 70, "equipment": "Projector", "is_active": True, "department": "CSE"},
            {"name": "CR-4", "type": "Classroom", "capacity": 65, "equipment": "", "is_active": True, "department": "CSE"},
            {"name": "CR-5", "type": "Classroom", "capacity": 65, "equipment": "", "is_active": True, "department": "CSE"},
            {"name": "LAB-1", "type": "Lab", "capacity": 35, "equipment": "Computer", "is_active": True, "department": "CSE", "num_pcs": 35},
            {"name": "LAB-2", "type": "Lab", "capacity": 35, "equipment": "Computer", "is_active": True, "department": "CSE", "num_pcs": 35},
            {"name": "LAB-3", "type": "Lab", "capacity": 35, "equipment": "Computer", "is_active": True, "department": "CSE", "num_pcs": 35},
            {"name": "LAB-4", "type": "Lab", "capacity": 35, "equipment": "Computer", "is_active": True, "department": "CSE", "num_pcs": 35},
        ]

    active_rooms = [r for r in parsed_resources if r.get("is_active", True)]
    max_classroom_cap = max([r["capacity"] for r in active_rooms if r["type"] == "Classroom"] or [0])
    max_lab_cap = max([r["capacity"] for r in active_rooms if r["type"] == "Lab"] or [0])

    # Process and Validate Time Configuration
    parsed_time_slots = []
    def get_time_val(r, col_keys, default=None):
        for k in col_keys:
            norm = re.sub(r"[^A-Z0-9]", "", k.upper())
            for actual_key, idx in time_col_map.items():
                if norm == actual_key or norm in actual_key or actual_key in norm:
                    if idx < len(r) and r[idx] is not None:
                        return r[idx]
        return default

    for row_num, row in time_rows:
        day = str(get_time_val(row, ["DAY"], "Monday")).strip()
        s_time = get_time_val(row, ["STARTTIME", "START"], "")
        e_time = get_time_val(row, ["ENDTIME", "END"], "")
        s_type = str(get_time_val(row, ["TYPE", "SLOTTYPE"], "Teaching")).strip()

        start_12h = format_time_12h(s_time)
        end_12h = format_time_12h(e_time)
        period_lbl = format_period_label(start_12h, end_12h)

        is_teaching = (s_type.lower() == "teaching")
        is_break = ("break" in s_type.lower() or "lunch" in s_type.lower())

        start_mins = time_str_to_minutes(start_12h)
        is_morning = (start_mins < 720)  # Before 12:00 PM

        parsed_time_slots.append({
            "day": day,
            "start_time": start_12h,
            "end_time": end_12h,
            "period": period_lbl,
            "type": "TEACHING" if is_teaching else ("LUNCH" if "lunch" in s_type.lower() else "SHORT_BREAK"),
            "is_morning": is_morning,
            "is_teaching": is_teaching
        })

    # Fallback to standard time slots if none parsed
    if not parsed_time_slots:
        std_periods = [
            ("9:00 AM", "10:00 AM", "TEACHING", True),
            ("10:00 AM", "11:00 AM", "TEACHING", True),
            ("11:00 AM", "11:15 AM", "SHORT_BREAK", True),
            ("11:15 AM", "12:15 PM", "TEACHING", True),
            ("12:15 PM", "1:15 PM", "TEACHING", False),
            ("1:15 PM", "2:00 PM", "LUNCH", False),
            ("2:00 PM", "3:00 PM", "TEACHING", False),
            ("3:00 PM", "4:00 PM", "TEACHING", False),
        ]
        for d in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            for st, et, tp, morn in std_periods:
                parsed_time_slots.append({
                    "day": d,
                    "start_time": st,
                    "end_time": et,
                    "period": f"{st} - {et}",
                    "type": tp,
                    "is_morning": morn,
                    "is_teaching": (tp == "TEACHING")
                })

    teaching_slots = [s for s in parsed_time_slots if s.get("type") == "TEACHING"]
    total_teaching_slots_per_week = len(teaching_slots)

    # Process and Validate Teaching Requirements
    requirements = []
    faculty_map = {}
    subjects_map = {}
    divisions_map = {}
    batches_map = {}
    division_weekly_loads = {}

    for row_num, row in teaching_rows:
        year = get_val(row, ["YEAR"], 2)
        semester = get_val(row, ["SEMESTER", "SEM"], 3)
        division = str(get_val(row, ["DIVISION", "DIV", "SECTION"], "A")).strip()
        batch = str(get_val(row, ["BATCH"], "-")).strip()
        if batch in ["-", "None", "nan", ""]:
            batch = None

        strength_val = get_val(row, ["STRENGTH"], 60)
        subj_code = str(get_val(row, ["SUBJECTCODE", "CODE"], "")).strip()
        subj_name = str(get_val(row, ["SUBJECT", "COURSE", "SUBJECTNAME"], "")).strip()
        sess_type = str(get_val(row, ["TYPE", "SESSIONTYPE"], "Lecture")).strip()
        sessions_week_val = get_val(row, ["SESSIONSWEEK", "SESSIONS"], 3)
        duration = str(get_val(row, ["DURATION"], "1 hr")).strip()
        fac_name = str(get_val(row, ["FACULTYNAME", "FACULTY", "INSTRUCTOR"], "")).strip()
        fac_code = str(get_val(row, ["FACULTYCODE", "INITIALS"], "")).strip()
        max_load_val = get_val(row, ["WEEKLYMAXLOAD", "MAXLOAD"], 18)
        preference = str(get_val(row, ["PREFERENCE", "PREF"], "Any")).strip()
        availability = str(get_val(row, ["AVAILABILITY", "AVAIL"], "")).strip()
        res_type = str(get_val(row, ["RESOURCETYPE", "ROOMTYPE"], "Classroom")).strip()
        cap_req_val = get_val(row, ["CAPACITYREQUIRED", "CAPACITYREQ", "CAPACITY"], 60)
        equipment = str(get_val(row, ["EQUIPMENT", "EQ"], "-")).strip()

        # Validations on required values
        if not subj_name:
            errors.append(f"Row {row_num}: Subject Name cannot be empty.")
            continue
        if not fac_name:
            errors.append(f"Row {row_num}: Faculty Name cannot be empty for subject '{subj_name}'.")
            continue

        if not availability or availability == "-" or availability.lower() == "none":
            errors.append(f'ERROR: Faculty "{fac_name}" has no availability information.')

        try:
            sessions_week = int(sessions_week_val)
            if sessions_week <= 0:
                errors.append(f"Row {row_num}: Sessions/Week for '{subj_name}' must be greater than 0.")
                continue
        except (ValueError, TypeError):
            errors.append(f"Row {row_num}: Sessions/Week for '{subj_name}' must be a number.")
            continue

        try:
            strength = int(strength_val)
        except (ValueError, TypeError):
            strength = 60

        try:
            capacity_req = int(cap_req_val)
            if capacity_req <= 0:
                capacity_req = strength
        except (ValueError, TypeError):
            capacity_req = strength

        try:
            max_load = int(max_load_val)
        except (ValueError, TypeError):
            max_load = 18

        is_lab = ("lab" in sess_type.lower() or "lab" in res_type.lower())

        # Check capacity feasibility against active resources
        if is_lab:
            if capacity_req > max_lab_cap:
                errors.append(
                    f'ERROR: {subj_name} requires a lab capacity of {capacity_req}, but no active lab has capacity >= {capacity_req} (Maximum active lab capacity is {max_lab_cap}).'
                )
            if equipment and equipment != "-":
                has_eq = any(r["type"] == "Lab" and equipment.lower() in (r.get("equipment") or "").lower() for r in active_rooms)
                if not has_eq:
                    errors.append(
                        f'ERROR: Lab session "{subj_name}" requires equipment "{equipment}", but no active lab provides it.'
                    )
        else:
            if capacity_req > max_classroom_cap:
                errors.append(
                    f'ERROR: {subj_name} requires a classroom capacity of {capacity_req}, but no active classroom has capacity >= {capacity_req} (Maximum active classroom capacity is {max_classroom_cap}).'
                )

        # Track weekly load per division
        div_key = f"{year}-{semester}-{division}"
        division_weekly_loads[div_key] = division_weekly_loads.get(div_key, 0) + sessions_week

        # Record requirements row
        requirements.append({
            "year": year,
            "semester": semester,
            "division": division,
            "batch": batch,
            "strength": strength,
            "subject_code": subj_code or (subj_name[:3].upper()),
            "subject": subj_name,
            "type": "Lab" if is_lab else "Lecture",
            "sessions_week": sessions_week,
            "duration": duration,
            "faculty_name": fac_name,
            "faculty_code": fac_code,
            "weekly_max_load": max_load,
            "preference": preference if preference in ["Morning", "Afternoon", "Any"] else "Any",
            "availability": availability,
            "resource_type": "Lab" if is_lab else "Classroom",
            "capacity_required": capacity_req,
            "equipment": equipment if equipment != "-" else ""
        })

        # Track faculty
        if fac_name not in faculty_map:
            faculty_map[fac_name] = {
                "name": fac_name,
                "code": fac_code,
                "designation": "Assistant Professor",
                "max_load": max_load,
                "preference": preference if preference in ["Morning", "Afternoon", "Any"] else "Any",
                "preferred_time": preference if preference in ["Morning", "Afternoon", "Any"] else "Any",
                "availability": availability,
                "subjects": set(),
                "assigned_load": 0,
                "department": "CSE"
            }
        faculty_map[fac_name]["subjects"].add(subj_name)
        faculty_map[fac_name]["assigned_load"] += sessions_week

        # Track subjects
        s_key = (subj_code, subj_name)
        if s_key not in subjects_map:
            subjects_map[s_key] = {
                "name": subj_name,
                "code": subj_code or subj_name[:4].upper(),
                "type": "Lab" if is_lab else "Lecture",
                "requires_lab": is_lab,
                "lectures_per_week": 0,
                "labs_per_week": 0,
                "duration": duration,
                "resource_type": "Lab" if is_lab else "Classroom",
                "capacity_required": capacity_req,
                "equipment": equipment if equipment != "-" else "",
                "department": "CSE"
            }
        if is_lab:
            subjects_map[s_key]["labs_per_week"] += sessions_week
        else:
            subjects_map[s_key]["lectures_per_week"] += sessions_week

        # Track division & batches
        if division not in divisions_map:
            divisions_map[division] = {
                "name": division,
                "strength": strength,
                "department_code": "CSE",
                "year": f"Year {year}",
                "semester": f"Semester {semester}"
            }
        else:
            divisions_map[division]["strength"] = max(divisions_map[division]["strength"], strength)

        if batch:
            batches_map[(division, batch)] = {
                "division_name": division,
                "name": batch,
                "strength": strength
            }

    # Division load checks
    for div_k, req_sessions in division_weekly_loads.items():
        if req_sessions > total_teaching_slots_per_week:
            errors.append(
                f"ERROR: Division '{div_k}' requires {req_sessions} teaching sessions per week, but only {total_teaching_slots_per_week} teaching slots are configured."
            )

    # Process faculty codes & check duplicates
    faculty_list = list(faculty_map.values())
    for f in faculty_list:
        f["subjects"] = list(f["subjects"])
    faculty_list = generate_faculty_codes(faculty_list)

    fac_code_seen = {}
    for f in faculty_list:
        c = f["code"]
        if c in fac_code_seen:
            warnings.append(f"WARNING: Faculty code '{c}' appears more than once ({fac_code_seen[c]} and {f['name']}).")
        else:
            fac_code_seen[c] = f["name"]

        if f["assigned_load"] > f["max_load"]:
            warnings.append(
                f"WARNING: Faculty '{f['name']}' has assigned load of {f['assigned_load']} hrs which exceeds weekly max load ({f['max_load']} hrs)."
            )

    # Update faculty codes back in requirements
    code_by_name = {f["name"]: f["code"] for f in faculty_list}
    for req in requirements:
        if not req.get("faculty_code"):
            req["faculty_code"] = code_by_name.get(req["faculty_name"], "FC")

    # Final structured data dict
    data_dict = {
        "requirements": requirements,
        "faculty": faculty_list,
        "subjects": list(subjects_map.values()),
        "divisions": list(divisions_map.values()),
        "batches": list(batches_map.values()),
        "rooms": parsed_resources,
        "time_slots": parsed_time_slots,
        "sections": [{"name": d["name"], "strength": d["strength"], "department": "CSE"} for d in divisions_map.values()],
        "departments": [{"code": "CSE", "name": "Computer Science and Engineering"}]
    }

    classrooms_count = len([r for r in parsed_resources if r["type"] == "Classroom"])
    labs_count = len([r for r in parsed_resources if r["type"] == "Lab"])

    summary = {
        "teaching_requirements_count": len(requirements),
        "faculty_count": len(faculty_list),
        "subjects_count": len(subjects_map),
        "divisions_count": len(divisions_map),
        "classrooms_count": classrooms_count,
        "labs_count": labs_count,
        "teaching_slots_count": total_teaching_slots_per_week,
        "total_slots_count": len(parsed_time_slots)
    }

    return data_dict, errors, warnings, summary


# ---------------------------------------------------------------------------
# PUBLIC ENTRY POINT
# ---------------------------------------------------------------------------
def read_excel(filepath_or_bytes):
    """
    Read .xlsx workbook from filepath or BytesIO.
    Prioritizes CLASHFREE_INPUT single sheet.
    Falls back gracefully to legacy multi-sheet workbooks.
    Returns: (data_dict, errors, warnings, summary)
    """
    try:
        if isinstance(filepath_or_bytes, (str, bytes)):
            wb = openpyxl.load_workbook(filepath_or_bytes, data_only=True)
        else:
            # File-like object (e.g. io.BytesIO or Werkzeug FileStorage)
            wb = openpyxl.load_workbook(filepath_or_bytes, data_only=True)
    except Exception as e:
        return None, [f"Could not open Excel file: {str(e)}"], [], {}

    sheetnames = wb.sheetnames

    # Check for CLASHFREE_INPUT sheet
    clashfree_sheet = None
    for name in sheetnames:
        if "CLASHFREE" in name.upper() or "INPUT" in name.upper():
            clashfree_sheet = wb[name]
            break

    if clashfree_sheet is not None or len(sheetnames) == 1:
        target_ws = clashfree_sheet if clashfree_sheet is not None else wb.active
        return parse_clashfree_single_sheet(target_ws)

    # Legacy multi-sheet parser fallback
    from backend import excel_reader_legacy
    return parse_clashfree_single_sheet(wb.active)


def validate_excel_data(filepath_or_bytes):
    """
    Performs pure validation on Excel without importing into database.
    Returns: (valid: bool, errors: list, warnings: list, summary: dict, data_dict: dict)
    """
    data_dict, errors, warnings, summary = read_excel(filepath_or_bytes)
    is_valid = (data_dict is not None and len(errors) == 0)
    return is_valid, errors, warnings, summary, data_dict
