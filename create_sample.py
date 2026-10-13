# create_sample.py
# Generates a comprehensive, styled sample_data.xlsx file for ClashFree.
# Includes: README, Departments, Divisions, Batches, Faculty, Rooms, Labs, Subjects, Sections.

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()

# Styling helpers
FONT_HEADER = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
FONT_TITLE = Font(name="Calibri", size=14, bold=True, color="1E3A8A")
FONT_SUBTITLE = Font(name="Calibri", size=10, italic=True, color="475569")
FONT_REGULAR = Font(name="Calibri", size=11, color="0F172A")
FONT_BOLD = Font(name="Calibri", size=11, bold=True, color="0F172A")

FILL_HEADER_BLUE = PatternFill("solid", fgColor="1D4ED8")   # Royal Blue
FILL_HEADER_TEAL = PatternFill("solid", fgColor="0F766E")   # Teal
FILL_HEADER_PURPLE = PatternFill("solid", fgColor="6D28D9") # Purple
FILL_HEADER_AMBER = PatternFill("solid", fgColor="B45309")  # Amber
FILL_ZEBRA = PatternFill("solid", fgColor="F8FAFC")

THIN_BORDER = Border(
    left=Side(style='thin', color='E2E8F0'),
    right=Side(style='thin', color='E2E8F0'),
    top=Side(style='thin', color='E2E8F0'),
    bottom=Side(style='thin', color='E2E8F0')
)

def apply_table_styles(ws, header_fill):
    ws.views.sheetView[0].showGridLines = True
    for cell in ws[1]:
        cell.font = FONT_HEADER
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER
    ws.row_dimensions[1].height = 28

    for row_idx, row in enumerate(ws.iter_rows(min_row=2), start=2):
        ws.row_dimensions[row_idx].height = 20
        is_even = (row_idx % 2 == 0)
        for cell in row:
            cell.font = FONT_REGULAR
            cell.border = THIN_BORDER
            if is_even:
                cell.fill = FILL_ZEBRA
            if isinstance(cell.value, (int, float)):
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

    # Auto-adjust column widths
    for col in ws.columns:
        max_len = max(len(str(c.value or "")) for c in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 5, 14)

# ---------------------------------------------------------------------------
# SHEET 1: README (User Guide)
# ---------------------------------------------------------------------------
ws_readme = wb.active
ws_readme.title = "README"
ws_readme.views.sheetView[0].showGridLines = True
ws_readme.column_dimensions['A'].width = 8
ws_readme.column_dimensions['B'].width = 30
ws_readme.column_dimensions['C'].width = 65

ws_readme.append(["", "CLASHFREE TIMETABLE SYSTEM - EXCEL IMPORT GUIDE", ""])
ws_readme['B1'].font = FONT_TITLE
ws_readme.row_dimensions[1].height = 30

ws_readme.append(["", "Mini Project | B.Tech CSE (2nd Year)", ""])
ws_readme['B2'].font = FONT_SUBTITLE
ws_readme.append([])

readme_instructions = [
    ("Sheet Name", "Purpose & Required Fields", "Description / Constraints"),
    ("Departments", "Code, DepartmentName", "Lists all participating departments (e.g., CSE, E&TC, MECH)."),
    ("Divisions", "DivisionName, Strength, Department, Year, Semester", "Configures divisions with individual student strengths (e.g. Div A = 75, Div B = 72)."),
    ("Batches", "DivisionName, BatchName, Strength", "Defines lab batches (e.g., A1, A2). Lab sessions are scheduled at batch level."),
    ("Faculty", "Name, Subjects, AvailableFrom, AvailableTo, PreferredTime, MaxLoad, Designation, Department", "Faculty details. System auto-generates initials (Vishal H. Pundikar -> VHP, duplicates -> KP1, KP2)."),
    ("Rooms", "RoomName, Type, Capacity, Department, PCs, IsReserved, ReservationReason", "Classrooms inventory. Supports HOD reservation flag and capacity constraints."),
    ("Labs", "LabName, Capacity, PCs, Department, LabType, IsReserved", "Laboratories with PC count. Enforces Student:PC ratio (default 1:1) and reservation."),
    ("Subjects", "Subject, LecturesPerWeek, LabsPerWeek, RequiresLab, Department, LabType", "Subjects. Automatically splits theory into lecture sessions & labs into batch sessions."),
    ("Sections", "SectionName, Strength", "Legacy support for backward compatibility.")
]

for row in readme_instructions:
    ws_readme.append(["", row[0], row[1] if len(row) > 2 else "", row[2] if len(row) > 2 else ""])

for r_idx in range(4, len(readme_instructions) + 4):
    ws_readme.row_dimensions[r_idx].height = 22
    for c_idx in [2, 3, 4]:
        cell = ws_readme.cell(row=r_idx, column=c_idx)
        cell.border = THIN_BORDER
        if r_idx == 4:
            cell.font = FONT_HEADER
            cell.fill = FILL_HEADER_BLUE
            cell.alignment = Alignment(horizontal="center", vertical="center")
        else:
            cell.font = FONT_BOLD if c_idx == 2 else FONT_REGULAR
            cell.alignment = Alignment(horizontal="left", vertical="center")
            if r_idx % 2 == 0:
                cell.fill = FILL_ZEBRA

# ---------------------------------------------------------------------------
# SHEET 2: Departments
# ---------------------------------------------------------------------------
ws_depts = wb.create_sheet("Departments")
ws_depts.append(["Code", "DepartmentName"])
for row in [
    ["CSE",  "Computer Science and Engineering"],
    ["E&TC", "Electronics & Telecommunication Engineering"],
    ["MECH", "Mechanical Engineering"]
]:
    ws_depts.append(row)
apply_table_styles(ws_depts, FILL_HEADER_BLUE)

# ---------------------------------------------------------------------------
# SHEET 3: Divisions
# ---------------------------------------------------------------------------
ws_divs = wb.create_sheet("Divisions")
ws_divs.append(["DivisionName", "Strength", "Department", "Year", "Semester"])
for row in [
    ["Division A", 75, "CSE",  "Second Year", "Semester III"],
    ["Division B", 72, "CSE",  "Second Year", "Semester III"],
    ["Div E1",     65, "E&TC", "Second Year", "Semester III"]
]:
    ws_divs.append(row)
apply_table_styles(ws_divs, FILL_HEADER_BLUE)

# ---------------------------------------------------------------------------
# SHEET 4: Batches
# ---------------------------------------------------------------------------
ws_batches = wb.create_sheet("Batches")
ws_batches.append(["DivisionName", "BatchName", "Strength"])
for row in [
    ["Division A", "A1", 38],
    ["Division A", "A2", 37],
    ["Division B", "B1", 36],
    ["Division B", "B2", 36],
    ["Div E1",     "E1-1", 33],
    ["Div E1",     "E1-2", 32]
]:
    ws_batches.append(row)
apply_table_styles(ws_batches, FILL_HEADER_BLUE)

# ---------------------------------------------------------------------------
# SHEET 5: Faculty
# ---------------------------------------------------------------------------
ws_fac = wb.create_sheet("Faculty")
ws_fac.append(["Name", "Subjects", "AvailableFrom", "AvailableTo", "PreferredTime", "MaxLoad", "Designation", "Department"])
for row in [
    ["Mr. Vishal H. Pundikar", "DSA, DS Lab",    "09:00", "17:00", "Morning",   18, "Assistant Professor", "CSE"],
    ["Dr. Vikas L. Bhise",     "DS Lab, DBMS",   "09:00", "17:00", "Morning",   18, "Associate Professor", "CSE"],
    ["Dr. Amit R. Sharma",     "TOC, Maths",     "09:00", "13:00", "Morning",   12, "Professor & HOD",     "CSE"],
    ["Mrs. Sneha P. Desai",    "OS, CN",         "11:00", "17:00", "Afternoon", 18, "Assistant Professor", "CSE"],
    ["Mr. Rahul K. Mehta",     "OS, TOC",        "09:00", "17:00", "Any",       18, "Assistant Professor", "CSE"],
    ["Ms. Priya S. Joshi",     "DBMS, Maths",    "09:00", "15:00", "Morning",   16, "Assistant Professor", "CSE"],
    ["Mr. Kunal Patil",        "DSA, CN",        "09:00", "17:00", "Morning",   18, "Assistant Professor", "CSE"],
    ["Mr. Kiran Patil",        "DBMS, OS",       "09:00", "17:00", "Any",       18, "Assistant Professor", "CSE"]
]:
    ws_fac.append(row)
apply_table_styles(ws_fac, FILL_HEADER_TEAL)

# ---------------------------------------------------------------------------
# SHEET 6: Rooms (Classrooms)
# ---------------------------------------------------------------------------
ws_rooms = wb.create_sheet("Rooms")
ws_rooms.append(["RoomName", "Type", "Capacity", "Department", "PCs", "IsReserved", "ReservationReason"])
for row in [
    ["CR-01", "Classroom", 80, "CSE",  0, "No",  ""],
    ["CR-02", "Classroom", 80, "CSE",  0, "No",  ""],
    ["CR-03", "Classroom", 80, "CSE",  0, "No",  ""],
    ["CR-04", "Classroom", 80, "CSE",  0, "No",  ""],
    ["CR-05", "Classroom", 80, "CSE",  0, "Yes", "HOD Seminar & Electives Reserve"],
    ["CR-11", "Classroom", 75, "E&TC", 0, "No",  ""]
]:
    ws_rooms.append(row)
apply_table_styles(ws_rooms, FILL_HEADER_AMBER)

# ---------------------------------------------------------------------------
# SHEET 7: Labs
# ---------------------------------------------------------------------------
ws_labs = wb.create_sheet("Labs")
ws_labs.append(["LabName", "Capacity", "PCs", "Department", "LabType", "IsReserved"])
for row in [
    ["LAB-01", 45, 45, "CSE",  "Computer Lab",    "No"],
    ["LAB-02", 45, 45, "CSE",  "Computer Lab",    "No"],
    ["LAB-03", 45, 45, "CSE",  "Computer Lab",    "No"],
    ["LAB-04", 45, 45, "CSE",  "Computer Lab",    "Yes"],
    ["LAB-05", 40, 25, "E&TC", "Electronics Lab", "No"]
]:
    ws_labs.append(row)
apply_table_styles(ws_labs, FILL_HEADER_PURPLE)

# ---------------------------------------------------------------------------
# SHEET 8: Subjects
# ---------------------------------------------------------------------------
ws_subjects = wb.create_sheet("Subjects")
ws_subjects.append(["Subject", "LecturesPerWeek", "LabsPerWeek", "RequiresLab", "Department", "LabType"])
for row in [
    ["DSA",    4, 0, "No",  "CSE", ""],
    ["DS Lab", 0, 2, "Yes", "CSE", "Computer Lab"],
    ["DBMS",   3, 0, "No",  "CSE", ""],
    ["OS",     3, 0, "No",  "CSE", ""],
    ["CN",     3, 0, "No",  "CSE", ""],
    ["Maths",  3, 0, "No",  "CSE", ""],
    ["TOC",    3, 0, "No",  "CSE", ""]
]:
    ws_subjects.append(row)
apply_table_styles(ws_subjects, FILL_HEADER_BLUE)

# ---------------------------------------------------------------------------
# SHEET 9: Sections (Legacy Compatibility)
# ---------------------------------------------------------------------------
ws_sections = wb.create_sheet("Sections")
ws_sections.append(["SectionName", "Strength"])
for row in [
    ["Division A", 75],
    ["Division B", 72]
]:
    ws_sections.append(row)
apply_table_styles(ws_sections, FILL_HEADER_BLUE)

# Save to project folder
output_path = "sample_data.xlsx"
wb.save(output_path)
print(f"Sample Excel generated successfully at: {output_path}")

# Also save to parent directory if running from inside ClashFree-Constriant-Based-Timetable
try:
    import os
    parent_path = os.path.join("..", "sample_data.xlsx")
    wb.save(parent_path)
    print(f"Also copied to parent directory: {parent_path}")
except Exception:
    pass
