# backend/excel_reader.py
# Reads uploaded Excel (.xlsx) file, validates schema and values,
# generates unique faculty codes, and returns structured data with validation diagnostics.

import openpyxl


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
        if f.get("code"):
            continue
        base = _extract_base(f.get("name", ""))
        if code_count[base] == 1:
            f["code"] = base
        else:
            occurrence[base] = occurrence.get(base, 0) + 1
            f["code"] = f"{base}{occurrence[base]}"

    return faculty_data


def read_excel(filepath: str):
    """
    Read .xlsx file with multi-sheet support and robust error checking.
    Supports:
    - New Sheets: Departments, Academic_Structure, Divisions, Batches, Faculty, Rooms, Labs, Subjects, Time_Slots, Resource_Config
    - Legacy Sheets: Faculty, Rooms, Subjects, Sections
    Returns: (data_dict, errors, warnings, summary)
    """
    errors = []
    warnings = []

    try:
        workbook = openpyxl.load_workbook(filepath, data_only=True)
    except Exception as e:
        return None, [f"Could not open Excel file: {str(e)}"], [], {}

    sheetnames = workbook.sheetnames

    departments_data = []
    academic_structure_data = []
    divisions_data = []
    batches_data = []
    sections_data = []
    rooms_data = []
    faculty_data = []
    subjects_data = []
    resource_config_data = []

    # 1. DEPARTMENTS
    if "Departments" in sheetnames:
        sheet = workbook["Departments"]
        for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            if all(c is None for c in row):
                continue
            code = str(row[0]).strip() if len(row) > 0 and row[0] else ""
            name = str(row[1]).strip() if len(row) > 1 and row[1] else ""
            if not code or not name:
                errors.append(f"Departments sheet, Row {row_num}: Department code and name required.")
                continue
            departments_data.append({"code": code, "name": name})

    # 2. DIVISIONS
    if "Divisions" in sheetnames:
        sheet = workbook["Divisions"]
        for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            if all(c is None for c in row):
                continue
            name = str(row[0]).strip() if len(row) > 0 and row[0] else ""
            strength = row[1] if len(row) > 1 and row[1] is not None else 60
            dept = str(row[2]).strip() if len(row) > 2 and row[2] else "CSE"
            year = str(row[3]).strip() if len(row) > 3 and row[3] else "Second Year"
            sem = str(row[4]).strip() if len(row) > 4 and row[4] else "Semester III"

            if not name:
                errors.append(f"Divisions sheet, Row {row_num}: Division name is missing.")
                continue
            try:
                strength = int(strength)
                if strength <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                errors.append(f"Divisions sheet, Row {row_num}: Strength must be a positive integer.")
                continue

            divisions_data.append({
                "name": name,
                "strength": strength,
                "department_code": dept,
                "year": year,
                "semester": sem
            })
            sections_data.append({"name": name, "strength": strength, "department": dept})

    # Legacy SECTIONS sheet
    if "Sections" in sheetnames and not divisions_data:
        sheet = workbook["Sections"]
        for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            if all(c is None for c in row):
                continue
            sec_name = str(row[0]).strip() if len(row) > 0 and row[0] else ""
            strength = row[1] if len(row) > 1 and row[1] is not None else 60
            dept = str(row[2]).strip() if len(row) > 2 and row[2] else "CSE"

            if not sec_name:
                errors.append(f"Sections sheet, Row {row_num}: Section name is missing.")
                continue
            try:
                strength = int(strength)
            except (ValueError, TypeError):
                errors.append(f"Sections sheet, Row {row_num}: Strength must be a number.")
                continue

            sections_data.append({"name": sec_name, "strength": strength, "department": dept})
            divisions_data.append({
                "name": sec_name,
                "strength": strength,
                "department_code": dept,
                "year": "Second Year",
                "semester": "Semester III"
            })

    # 3. BATCHES
    if "Batches" in sheetnames:
        sheet = workbook["Batches"]
        for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            if all(c is None for c in row):
                continue
            div_name = str(row[0]).strip() if len(row) > 0 and row[0] else ""
            batch_name = str(row[1]).strip() if len(row) > 1 and row[1] else ""
            strength = row[2] if len(row) > 2 and row[2] is not None else 30

            if not div_name or not batch_name:
                errors.append(f"Batches sheet, Row {row_num}: Division and Batch name are required.")
                continue
            try:
                strength = int(strength)
            except (ValueError, TypeError):
                errors.append(f"Batches sheet, Row {row_num}: Strength must be a number.")
                continue

            batches_data.append({
                "division_name": div_name,
                "name": batch_name,
                "strength": strength
            })

    # If batches were not specified in Excel, auto-create 2 batches per division (e.g. A1, A2)
    if not batches_data and divisions_data:
        for div in divisions_data:
            div_name = div["name"]
            half = div["strength"] // 2
            batches_data.append({"division_name": div_name, "name": f"{div_name}-1", "strength": half})
            batches_data.append({"division_name": div_name, "name": f"{div_name}-2", "strength": div["strength"] - half})

    # 4. FACULTY
    if "Faculty" in sheetnames:
        sheet = workbook["Faculty"]
        for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            if all(c is None for c in row):
                continue
            name           = str(row[0]).strip() if len(row) > 0 and row[0] else ""
            subjects_raw   = str(row[1]).strip() if len(row) > 1 and row[1] else ""
            available_from = str(row[2]).strip() if len(row) > 2 and row[2] else "09:00"
            available_to   = str(row[3]).strip() if len(row) > 3 and row[3] else "17:00"
            preferred_time = str(row[4]).strip() if len(row) > 4 and row[4] else "Any"
            max_load       = row[5] if len(row) > 5 and row[5] is not None else 20
            designation    = str(row[6]).strip() if len(row) > 6 and row[6] else "Assistant Professor"
            dept           = str(row[7]).strip() if len(row) > 7 and row[7] else "CSE"

            if not name or name == "None":
                errors.append(f"Faculty sheet, Row {row_num}: Faculty name is missing.")
                continue

            subjects = [s.strip() for s in subjects_raw.split(",") if s.strip()]
            preferred_time = preferred_time.capitalize()
            if preferred_time not in ("Morning", "Afternoon", "Any"):
                preferred_time = "Any"

            try:
                max_load = int(max_load)
            except (ValueError, TypeError):
                max_load = 20

            faculty_data.append({
                "name":           name,
                "subjects":       subjects,
                "available_from": available_from,
                "available_to":   available_to,
                "preferred_time": preferred_time,
                "max_load":       max_load,
                "designation":    designation,
                "department":     dept,
                "code":           "",
            })
    else:
        errors.append("Sheet 'Faculty' is missing from the Excel file.")

    faculty_data = generate_faculty_codes(faculty_data)

    # 5. ROOMS & LABS
    if "Rooms" in sheetnames:
        sheet = workbook["Rooms"]
        for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            if all(c is None for c in row):
                continue
            room_name = str(row[0]).strip() if len(row) > 0 and row[0] else ""
            room_type = str(row[1]).strip() if len(row) > 1 and row[1] else "Classroom"
            capacity  = row[2] if len(row) > 2 and row[2] is not None else 60
            dept      = str(row[3]).strip() if len(row) > 3 and row[3] else "CSE"
            num_pcs   = row[4] if len(row) > 4 and row[4] is not None else (35 if room_type == "Lab" else 0)
            is_res    = str(row[5]).strip().lower() in ("yes", "true", "1") if len(row) > 5 and row[5] else False
            res_reason= str(row[6]).strip() if len(row) > 6 and row[6] else ""

            if not room_name or room_name == "None":
                errors.append(f"Rooms sheet, Row {row_num}: Room name is missing.")
                continue
            if room_type not in ("Classroom", "Lab"):
                errors.append(f"Rooms sheet, Row {row_num}: Type must be 'Classroom' or 'Lab'.")
                continue
            try:
                capacity = int(capacity)
                num_pcs = int(num_pcs)
            except (ValueError, TypeError):
                errors.append(f"Rooms sheet, Row {row_num}: Capacity and PCs must be integers.")
                continue

            rooms_data.append({
                "name": room_name,
                "type": room_type,
                "capacity": capacity,
                "department": dept,
                "lab_type": "Computer Lab" if room_type == "Lab" else "",
                "num_pcs": num_pcs,
                "equipment": f"{num_pcs} PCs, Projector" if room_type == "Lab" else "Projector",
                "is_reserved": is_res,
                "reservation_reason": res_reason
            })
    else:
        errors.append("Sheet 'Rooms' is missing from the Excel file.")

    # Optional separate 'Labs' sheet
    if "Labs" in sheetnames:
        sheet = workbook["Labs"]
        for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            if all(c is None for c in row):
                continue
            lab_name = str(row[0]).strip() if len(row) > 0 and row[0] else ""
            cap = row[1] if len(row) > 1 and row[1] is not None else 40
            pcs = row[2] if len(row) > 2 and row[2] is not None else 40
            dept = str(row[3]).strip() if len(row) > 3 and row[3] else "CSE"
            lab_type = str(row[4]).strip() if len(row) > 4 and row[4] else "Computer Lab"
            is_res = str(row[5]).strip().lower() in ("yes", "true", "1") if len(row) > 5 and row[5] else False

            if not lab_name:
                continue
            rooms_data.append({
                "name": lab_name,
                "type": "Lab",
                "capacity": int(cap),
                "department": dept,
                "lab_type": lab_type,
                "num_pcs": int(pcs),
                "equipment": f"{pcs} PCs, Gigabit LAN",
                "is_reserved": is_res,
                "reservation_reason": "Reserved Lab" if is_res else ""
            })

    # 6. SUBJECTS
    if "Subjects" in sheetnames:
        sheet = workbook["Subjects"]
        for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            if all(c is None for c in row):
                continue
            subject_name = str(row[0]).strip() if len(row) > 0 and row[0] else ""
            lec_pw       = row[1] if len(row) > 1 and row[1] is not None else 0
            lab_pw       = row[2] if len(row) > 2 and row[2] is not None else 0
            req_lab      = str(row[3]).strip().lower() in ("yes", "true", "1") if len(row) > 3 and row[3] else False
            dept         = str(row[4]).strip() if len(row) > 4 and row[4] else "CSE"
            lab_type     = str(row[5]).strip() if len(row) > 5 and row[5] else ("Computer Lab" if req_lab or lab_pw > 0 else "")

            if not subject_name or subject_name == "None":
                errors.append(f"Subjects sheet, Row {row_num}: Subject name is missing.")
                continue
            try:
                lec_pw = int(lec_pw)
                lab_pw = int(lab_pw)
            except (ValueError, TypeError):
                errors.append(f"Subjects sheet, Row {row_num}: Lectures and Labs per week must be numbers.")
                continue

            subjects_data.append({
                "name": subject_name,
                "code": f"CS-{subject_name[:4].upper()}",
                "department": dept,
                "lectures_per_week": lec_pw,
                "labs_per_week": lab_pw,
                "requires_lab": req_lab or lab_pw > 0,
                "lab_type": lab_type,
                "student_pc_ratio": 1.0
            })
    else:
        errors.append("Sheet 'Subjects' is missing from the Excel file.")

    summary = {
        "departments": len(departments_data),
        "divisions": len(divisions_data),
        "batches": len(batches_data),
        "faculty": len(faculty_data),
        "rooms": len(rooms_data),
        "subjects": len(subjects_data),
        "sections": len(sections_data)
    }

    data_dict = {
        "departments": departments_data,
        "academic_structure": academic_structure_data,
        "divisions": divisions_data,
        "batches": batches_data,
        "sections": sections_data,
        "faculty": faculty_data,
        "rooms": rooms_data,
        "subjects": subjects_data,
        "resource_config": resource_config_data
    }

    return data_dict, errors, warnings, summary
