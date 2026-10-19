# create_sample.py
# Generates the official human-friendly single-sheet Excel template:
# Sheet: CLASHFREE_INPUT
# Contains 3 clearly separated sections:
# 1. Main Teaching Requirements table (18 columns)
# 2. RESOURCE CONFIGURATION (Resource Type, Resource Name, Capacity, Equipment, Active)
# 3. TIME CONFIGURATION (Day, Start Time, End Time, Type)

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "CLASHFREE_INPUT"
ws.views.sheetView[0].showGridLines = True

# Styles
FONT_TITLE = Font(name="Calibri", size=14, bold=True, color="1E3A8A")
FONT_SUBTITLE = Font(name="Calibri", size=10, italic=True, color="475569")
FONT_SEC_HEADER = Font(name="Calibri", size=12, bold=True, color="FFFFFF")
FONT_TH = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
FONT_REGULAR = Font(name="Calibri", size=10, color="0F172A")
FONT_BOLD = Font(name="Calibri", size=10, bold=True, color="0F172A")

FILL_NAVY = PatternFill("solid", fgColor="1E3A8A")
FILL_TEAL = PatternFill("solid", fgColor="0F766E")
FILL_SLATE = PatternFill("solid", fgColor="334155")
FILL_AMBER = PatternFill("solid", fgColor="B45309")
FILL_ZEBRA = PatternFill("solid", fgColor="F8FAFC")
FILL_SECTION_BANNER = PatternFill("solid", fgColor="0F172A")

THIN_BORDER = Border(
    left=Side(style='thin', color='CBD5E1'),
    right=Side(style='thin', color='CBD5E1'),
    top=Side(style='thin', color='CBD5E1'),
    bottom=Side(style='thin', color='CBD5E1')
)

# ---------------------------------------------------------------------------
# 1. TEACHING REQUIREMENTS (MAIN TABLE)
# ---------------------------------------------------------------------------
teaching_headers = [
    "Year",
    "Semester",
    "Division",
    "Batch",
    "Strength",
    "Subject Code",
    "Subject",
    "Type",
    "Sessions/Week",
    "Duration",
    "Faculty Name",
    "Faculty Code",
    "Weekly Max Load",
    "Preference",
    "Availability",
    "Resource Type",
    "Capacity Required",
    "Equipment"
]

teaching_data = [
    # Division A - Theory & Labs
    [2, 3, "A", "-", 60, "DS", "Data Structures", "Lecture", 4, "1 hr", "Vishal H. Pundikar", "VHP", 18, "Morning", "Mon-Fri 9:00 AM-4:00 PM", "Classroom", 60, "-"],
    [2, 3, "A", "A1", 30, "DSL", "Data Structures Lab", "Lab", 2, "2 hr", "Naresh A. Kamble", "NAK", 18, "Morning", "Mon-Fri 9:00 AM-1:00 PM", "Lab", 30, "Computer"],
    [2, 3, "A", "A2", 30, "DSL", "Data Structures Lab", "Lab", 2, "2 hr", "Naresh A. Kamble", "NAK", 18, "Morning", "Mon-Fri 9:00 AM-1:00 PM", "Lab", 30, "Computer"],
    [2, 3, "A", "-", 60, "OOP", "Object Oriented Programming", "Lecture", 3, "1 hr", "Dr. Amit R. Sharma", "ARS", 14, "Morning", "Mon-Fri 9:00 AM-2:00 PM", "Classroom", 60, "Projector"],
    [2, 3, "A", "A1", 30, "OOPL", "OOP Lab", "Lab", 2, "2 hr", "Priya S. Joshi", "PSJ", 16, "Afternoon", "Mon-Fri 11:00 AM-5:00 PM", "Lab", 30, "Computer"],
    [2, 3, "A", "A2", 30, "OOPL", "OOP Lab", "Lab", 2, "2 hr", "Priya S. Joshi", "PSJ", 16, "Afternoon", "Mon-Fri 11:00 AM-5:00 PM", "Lab", 30, "Computer"],
    [2, 3, "A", "-", 60, "DBMS", "Database Management Systems", "Lecture", 3, "1 hr", "Dr. Vikas L. Bhise", "VLB", 18, "Morning", "Mon-Fri 9:00 AM-4:00 PM", "Classroom", 60, "-"],
    [2, 3, "A", "A1", 30, "DBMSL", "DBMS Lab", "Lab", 2, "2 hr", "Sneha P. Desai", "SPD", 18, "Afternoon", "Mon-Fri 10:00 AM-4:00 PM", "Lab", 30, "Computer"],
    [2, 3, "A", "A2", 30, "DBMSL", "DBMS Lab", "Lab", 2, "2 hr", "Sneha P. Desai", "SPD", 18, "Afternoon", "Mon-Fri 10:00 AM-4:00 PM", "Lab", 30, "Computer"],
    [2, 3, "A", "-", 60, "OS", "Operating Systems", "Lecture", 3, "1 hr", "Rahul K. Mehta", "RKM", 18, "Any", "Mon-Fri 9:00 AM-4:00 PM", "Classroom", 60, "-"],
    [2, 3, "A", "-", 60, "TOC", "Theory of Computation", "Lecture", 3, "1 hr", "K. P. Kulkarni", "KPK", 18, "Morning", "Mon-Fri 9:00 AM-3:00 PM", "Classroom", 60, "-"],

    # Division B - Theory & Labs
    [2, 3, "B", "-", 60, "DS", "Data Structures", "Lecture", 4, "1 hr", "Vishal H. Pundikar", "VHP", 18, "Morning", "Mon-Fri 9:00 AM-4:00 PM", "Classroom", 60, "-"],
    [2, 3, "B", "B1", 30, "DSL", "Data Structures Lab", "Lab", 2, "2 hr", "Naresh A. Kamble", "NAK", 18, "Morning", "Mon-Fri 9:00 AM-1:00 PM", "Lab", 30, "Computer"],
    [2, 3, "B", "B2", 30, "DSL", "Data Structures Lab", "Lab", 2, "2 hr", "Naresh A. Kamble", "NAK", 18, "Morning", "Mon-Fri 9:00 AM-1:00 PM", "Lab", 30, "Computer"],
    [2, 3, "B", "-", 60, "OOP", "Object Oriented Programming", "Lecture", 3, "1 hr", "Dr. Amit R. Sharma", "ARS", 14, "Morning", "Mon-Fri 9:00 AM-2:00 PM", "Classroom", 60, "Projector"],
    [2, 3, "B", "B1", 30, "OOPL", "OOP Lab", "Lab", 2, "2 hr", "Priya S. Joshi", "PSJ", 16, "Afternoon", "Mon-Fri 11:00 AM-5:00 PM", "Lab", 30, "Computer"],
    [2, 3, "B", "B2", 30, "OOPL", "OOP Lab", "Lab", 2, "2 hr", "Priya S. Joshi", "PSJ", 16, "Afternoon", "Mon-Fri 11:00 AM-5:00 PM", "Lab", 30, "Computer"],
    [2, 3, "B", "-", 60, "DBMS", "Database Management Systems", "Lecture", 3, "1 hr", "Dr. Vikas L. Bhise", "VLB", 18, "Morning", "Mon-Fri 9:00 AM-4:00 PM", "Classroom", 60, "-"],
    [2, 3, "B", "B1", 30, "DBMSL", "DBMS Lab", "Lab", 2, "2 hr", "Sneha P. Desai", "SPD", 18, "Afternoon", "Mon-Fri 10:00 AM-4:00 PM", "Lab", 30, "Computer"],
    [2, 3, "B", "B2", 30, "DBMSL", "DBMS Lab", "Lab", 2, "2 hr", "Sneha P. Desai", "SPD", 18, "Afternoon", "Mon-Fri 10:00 AM-4:00 PM", "Lab", 30, "Computer"],
    [2, 3, "B", "-", 60, "OS", "Operating Systems", "Lecture", 3, "1 hr", "Rahul K. Mehta", "RKM", 18, "Any", "Mon-Fri 9:00 AM-4:00 PM", "Classroom", 60, "-"],
    [2, 3, "B", "-", 60, "TOC", "Theory of Computation", "Lecture", 3, "1 hr", "K. P. Kulkarni", "KPK", 18, "Morning", "Mon-Fri 9:00 AM-3:00 PM", "Classroom", 60, "-"]
]

# Row 1: Header
ws.append(teaching_headers)
ws.row_dimensions[1].height = 28
for col_idx, cell in enumerate(ws[1], start=1):
    cell.font = FONT_TH
    cell.fill = FILL_NAVY
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = THIN_BORDER

current_row = 2
for r_data in teaching_data:
    ws.append(r_data)
    ws.row_dimensions[current_row].height = 20
    is_even = (current_row % 2 == 0)
    for col_idx, cell in enumerate(ws[current_row], start=1):
        cell.font = FONT_REGULAR
        cell.border = THIN_BORDER
        if is_even:
            cell.fill = FILL_ZEBRA
        if col_idx in [1, 2, 5, 9, 13, 17]:
            cell.alignment = Alignment(horizontal="center", vertical="center")
        elif col_idx in [3, 4, 6, 8, 12, 14, 16]:
            cell.alignment = Alignment(horizontal="center", vertical="center")
        else:
            cell.alignment = Alignment(horizontal="left", vertical="center")
    current_row += 1

# Blank row separator
ws.append([])
current_row += 1

# ---------------------------------------------------------------------------
# 2. RESOURCE CONFIGURATION
# ---------------------------------------------------------------------------
res_banner = ["RESOURCE CONFIGURATION", "", "", "", ""]
ws.append(res_banner)
ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=5)
ws.row_dimensions[current_row].height = 26
ws.cell(row=current_row, column=1).font = FONT_SEC_HEADER
ws.cell(row=current_row, column=1).fill = FILL_TEAL
ws.cell(row=current_row, column=1).alignment = Alignment(horizontal="left", vertical="center", indent=1)
current_row += 1

res_headers = ["Resource Type", "Resource Name", "Capacity", "Equipment", "Active"]
ws.append(res_headers)
ws.row_dimensions[current_row].height = 24
for col_idx in range(1, 6):
    cell = ws.cell(row=current_row, column=col_idx)
    cell.font = FONT_TH
    cell.fill = FILL_SLATE
    cell.alignment = Alignment(horizontal="center", vertical="center")
    cell.border = THIN_BORDER
current_row += 1

resources_data = [
    ["Classroom", "CR-1", 65, "-", "Yes"],
    ["Classroom", "CR-2", 65, "Projector", "Yes"],
    ["Classroom", "CR-3", 70, "Projector", "Yes"],
    ["Classroom", "CR-4", 65, "-", "Yes"],
    ["Classroom", "CR-5", 65, "-", "Yes"],
    ["Lab", "LAB-1", 35, "Computer", "Yes"],
    ["Lab", "LAB-2", 35, "Computer", "Yes"],
    ["Lab", "LAB-3", 35, "Computer", "Yes"],
    ["Lab", "LAB-4", 35, "Computer", "Yes"]
]

for r_data in resources_data:
    ws.append(r_data)
    ws.row_dimensions[current_row].height = 20
    is_even = (current_row % 2 == 0)
    for col_idx in range(1, 6):
        cell = ws.cell(row=current_row, column=col_idx)
        cell.font = FONT_REGULAR
        cell.border = THIN_BORDER
        if is_even:
            cell.fill = FILL_ZEBRA
        if col_idx in [1, 2, 3, 5]:
            cell.alignment = Alignment(horizontal="center", vertical="center")
        else:
            cell.alignment = Alignment(horizontal="left", vertical="center")
    current_row += 1

# Blank row separator
ws.append([])
current_row += 1

# ---------------------------------------------------------------------------
# 3. TIME CONFIGURATION
# ---------------------------------------------------------------------------
time_banner = ["TIME CONFIGURATION", "", "", ""]
ws.append(time_banner)
ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=4)
ws.row_dimensions[current_row].height = 26
ws.cell(row=current_row, column=1).font = FONT_SEC_HEADER
ws.cell(row=current_row, column=1).fill = FILL_AMBER
ws.cell(row=current_row, column=1).alignment = Alignment(horizontal="left", vertical="center", indent=1)
current_row += 1

time_headers = ["Day", "Start Time", "End Time", "Type"]
ws.append(time_headers)
ws.row_dimensions[current_row].height = 24
for col_idx in range(1, 5):
    cell = ws.cell(row=current_row, column=col_idx)
    cell.font = FONT_TH
    cell.fill = FILL_SLATE
    cell.alignment = Alignment(horizontal="center", vertical="center")
    cell.border = THIN_BORDER
current_row += 1

daily_slots = [
    ("9:00 AM", "10:00 AM", "Teaching"),
    ("10:00 AM", "11:00 AM", "Teaching"),
    ("11:00 AM", "11:15 AM", "Break"),
    ("11:15 AM", "12:15 PM", "Teaching"),
    ("12:15 PM", "1:15 PM", "Teaching"),
    ("1:15 PM", "2:00 PM", "Lunch"),
    ("2:00 PM", "3:00 PM", "Teaching"),
    ("3:00 PM", "4:00 PM", "Teaching")
]

for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
    for st, et, slot_type in daily_slots:
        ws.append([day, st, et, slot_type])
        ws.row_dimensions[current_row].height = 19
        is_even = (current_row % 2 == 0)
        for col_idx in range(1, 5):
            cell = ws.cell(row=current_row, column=col_idx)
            cell.font = FONT_REGULAR
            cell.border = THIN_BORDER
            if is_even:
                cell.fill = FILL_ZEBRA
            cell.alignment = Alignment(horizontal="center", vertical="center")
            if slot_type in ["Break", "Lunch"]:
                cell.font = FONT_BOLD
        current_row += 1

# Column width auto-adjustment
col_widths = {
    1: 8,   # Year
    2: 10,  # Semester
    3: 10,  # Division
    4: 10,  # Batch
    5: 10,  # Strength
    6: 14,  # Subject Code
    7: 28,  # Subject
    8: 12,  # Type
    9: 14,  # Sessions/Week
    10: 12, # Duration
    11: 24, # Faculty Name
    12: 14, # Faculty Code
    13: 16, # Weekly Max Load
    14: 14, # Preference
    15: 26, # Availability
    16: 16, # Resource Type
    17: 18, # Capacity Required
    18: 14  # Equipment
}

for col_idx, width in col_widths.items():
    col_letter = get_column_letter(col_idx)
    ws.column_dimensions[col_letter].width = width

wb.save("sample_data.xlsx")
print("Successfully generated official CLASHFREE_INPUT single-sheet template at sample_data.xlsx")
