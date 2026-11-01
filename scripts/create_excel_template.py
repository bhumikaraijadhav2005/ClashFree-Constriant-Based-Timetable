"""Build the official multi-sheet ClashFree timetable setup workbook."""

from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo


NAVY = "17365D"
BLUE = "245A81"
TEAL = "168C8C"
PALE_BLUE = "EAF2F8"
PALE_TEAL = "E6F4F1"
INK = "203040"
MUTED = "5C6B78"
WHITE = "FFFFFF"
LINE = "D5DEE7"
THIN_BORDER = Border(*(Side(style="thin", color=LINE) for _ in range(4)))


def add_title(ws, title, subtitle, column_count):
    ws.sheet_view.showGridLines = False
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=column_count)
    cell = ws.cell(1, 1, title)
    cell.font = Font(name="Aptos Display", size=18, bold=True, color=WHITE)
    cell.fill = PatternFill("solid", fgColor=NAVY)
    cell.alignment = Alignment(vertical="center")
    ws.row_dimensions[1].height = 34
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=column_count)
    cell = ws.cell(2, 1, subtitle)
    cell.font = Font(name="Aptos", size=10, color=MUTED, italic=True)
    cell.fill = PatternFill("solid", fgColor=PALE_BLUE)
    cell.alignment = Alignment(wrap_text=True, vertical="center")
    ws.row_dimensions[2].height = 30


def add_table(ws, headers, rows, name, widths):
    header_row = 4
    for column, header in enumerate(headers, 1):
        cell = ws.cell(header_row, column, header)
        cell.font = Font(name="Aptos", size=10, bold=True, color=WHITE)
        cell.fill = PatternFill("solid", fgColor=BLUE)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER
    ws.row_dimensions[header_row].height = 32
    for row_num, values in enumerate(rows, header_row + 1):
        for column, value in enumerate(values, 1):
            cell = ws.cell(row_num, column, value)
            cell.font = Font(name="Aptos", size=10, color=INK)
            cell.fill = PatternFill("solid", fgColor=WHITE if row_num % 2 else "F6F9FB")
            cell.alignment = Alignment(vertical="center", wrap_text=True)
            cell.border = THIN_BORDER
        ws.row_dimensions[row_num].height = 23
    last_row = header_row + max(1, len(rows))
    ref = f"A{header_row}:{openpyxl.utils.get_column_letter(len(headers))}{last_row}"
    table = Table(displayName=name, ref=ref)
    table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
    ws.add_table(table)
    ws.freeze_panes = f"A{header_row + 1}"
    ws.auto_filter.ref = ref
    for column, width in enumerate(widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(column)].width = width
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.tabColor = TEAL


def add_dropdown(ws, column, first_row, last_row, formula, prompt):
    rule = DataValidation(type="list", formula1=formula, allow_blank=True)
    rule.promptTitle = "Choose a configured value"
    rule.prompt = prompt
    rule.errorTitle = "Invalid value"
    rule.error = "Choose one of the listed values."
    ws.add_data_validation(rule)
    rule.add(f"{column}{first_row}:{column}{last_row}")


def build_workbook():
    wb = openpyxl.Workbook()
    guide = wb.active
    guide.title = "Instructions"
    guide.sheet_view.showGridLines = False
    guide.sheet_properties.tabColor = NAVY
    for column, width in {"A": 23, "B": 34, "C": 35, "D": 28, "E": 20, "F": 18}.items():
        guide.column_dimensions[column].width = width
    guide.merge_cells("A1:F1")
    guide["A1"] = "CLASHFREE | TIMETABLE SETUP WORKBOOK"
    guide["A1"].font = Font(name="Aptos Display", size=20, bold=True, color=WHITE)
    guide["A1"].fill = PatternFill("solid", fgColor=NAVY)
    guide["A1"].alignment = Alignment(vertical="center")
    guide.row_dimensions[1].height = 42
    guide.merge_cells("A2:F2")
    guide["A2"] = "Complete the blue-header tables, validate the workbook in ClashFree, then import it for the selected college and department."
    guide["A2"].font = Font(name="Aptos", size=11, color=MUTED, italic=True)
    guide["A2"].fill = PatternFill("solid", fgColor=PALE_BLUE)
    guide["A2"].alignment = Alignment(wrap_text=True, vertical="center")
    guide.row_dimensions[2].height = 34
    instructions = [
        ("1  Faculty", "Add every faculty member once on the Faculty sheet. Use a unique Faculty Code. The same code can be assigned to subjects on any number of year sheets."),
        ("2  Year sheets", "Fill Year 1, Year 2, Year 3, or duplicate the Year Template and rename it Year 4, Year 5, and so on. The importer discovers numbered year sheets dynamically."),
        ("3  Subject rows", "Add one row per division, subject, and lab batch when batches are explicitly configured. For a lab without a Batch value, ClashFree can split the division using active lab capacity."),
        ("4  Resources", "Enter actual rooms and labs, positive capacities, equipment, and active/shared status. Do not include unavailable or placeholder rooms."),
        ("5  Time Slots", "Enter each day's periods in order. Mark each row Teaching, Break, or Lunch. A multi-period lab must fit consecutive Teaching rows without a break or lunch between them."),
        ("6  Import context", "Choose College, Department, Academic Year, and Semester in the application before validation/import. These workbook rows do not override the selected department."),
        ("7  Safe import", "The application validates the whole workbook before importing. Fix every error shown in the validation report, then validate again before import."),
        ("Required values", "Use real division strengths, batch strengths, faculty codes, resource capacities, and durations. Do not merge cells or rename required headers."),
        ("Duration", "Duration is a number of timetable periods (1, 2, or 3). Sessions/Week is the number of occurrences for that row's division or batch."),
        ("Semester", "Use a consistent value such as Semester I or Semester 1. Each numbered year sheet may contain more than one semester."),
    ]
    for row_num, (label, text) in enumerate(instructions, 4):
        guide.cell(row_num, 1, label)
        guide.cell(row_num, 1).font = Font(name="Aptos", bold=True, color=NAVY)
        guide.cell(row_num, 1).fill = PatternFill("solid", fgColor=PALE_TEAL)
        guide.cell(row_num, 1).alignment = Alignment(vertical="top", wrap_text=True)
        guide.merge_cells(start_row=row_num, start_column=2, end_row=row_num, end_column=6)
        guide.cell(row_num, 2, text)
        guide.cell(row_num, 2).font = Font(name="Aptos", color=INK)
        guide.cell(row_num, 2).alignment = Alignment(vertical="top", wrap_text=True)
        for column in range(1, 7):
            guide.cell(row_num, column).border = THIN_BORDER
        guide.row_dimensions[row_num].height = 43
    guide.freeze_panes = "A4"

    faculty = wb.create_sheet("Faculty")
    add_title(faculty, "Faculty Directory", "One row per person. Faculty codes are referenced by every year sheet.", 5)
    add_table(faculty,
              ["Faculty Code", "Faculty Name", "Maximum Weekly Load", "Preference", "Availability"],
              [["FAC001", "Aarav Mehta", 16, "Morning", "Mon-Fri 9:00 AM-4:00 PM"],
               ["FAC002", "Diya Kulkarni", 16, "Any", "Mon-Fri 9:00 AM-5:00 PM"],
               ["FAC003", "Kabir Shah", 14, "Afternoon", "Mon-Fri 10:00 AM-5:00 PM"],
               ["FAC004", "Mira Rao", 16, "Morning", "Mon-Fri 9:00 AM-3:00 PM"],
               ["FAC005", "Ishan Patil", 14, "Any", "Mon-Fri 9:00 AM-4:00 PM"]],
              "FacultyDirectory", [18, 28, 24, 18, 34])
    add_dropdown(faculty, "D", 5, 504, '"Morning,Afternoon,Any"', "Choose a time preference.")

    headers = ["Semester", "Division", "Division Strength", "Batch", "Batch Strength", "Subject Code",
               "Subject Name", "Type", "Sessions/Week", "Duration", "Faculty Code",
               "Required Resource Type", "Required Equipment"]
    widths = [18, 14, 20, 14, 18, 18, 32, 14, 18, 14, 18, 24, 24]
    examples = {
        "Year 1": [
            ["Semester I", "A", 60, "", "", "MTH101", "Engineering Mathematics", "Lecture", 3, 1, "FAC001", "Classroom", "Projector"],
            ["Semester I", "A", 60, "", "", "PHY101", "Applied Physics", "Lecture", 2, 1, "FAC004", "Classroom", ""],
            ["Semester I", "A", 60, "", "", "CPL101", "Programming Lab", "Lab", 1, 2, "FAC002", "Lab", "Computer"],
        ],
        "Year 2": [
            ["Semester III", "A", 60, "", "", "CSE201", "Data Structures", "Lecture", 3, 1, "FAC001", "Classroom", "Projector"],
            ["Semester III", "A", 60, "", "", "CSE202L", "Data Structures Lab", "Lab", 1, 2, "FAC002", "Lab", "Computer"],
            ["Semester III", "B", 58, "", "", "CSE201", "Data Structures", "Lecture", 3, 1, "FAC001", "Classroom", "Projector"],
            ["Semester III", "B", 58, "", "", "CSE202L", "Data Structures Lab", "Lab", 1, 2, "FAC002", "Lab", "Computer"],
        ],
        "Year 3": [
            ["Semester V", "A", 55, "", "", "CSE301", "Computer Networks", "Lecture", 3, 1, "FAC005", "Classroom", "Projector"],
            ["Semester V", "A", 55, "", "", "CSE302L", "Networks Lab", "Lab", 1, 2, "FAC003", "Lab", "Computer"],
        ],
    }
    for sheet_name, rows in examples.items():
        ws = wb.create_sheet(sheet_name)
        add_title(ws, f"{sheet_name} Requirements", "One row per subject and division. Leave Batch blank to use division strength; lab groups may be split to fit configured labs.", len(headers))
        add_table(ws, headers, rows, sheet_name.replace(" ", "") + "Requirements", widths)
        add_dropdown(ws, "H", 5, 1004, '"Lecture,Lab"', "Choose Lecture or Lab.")
        add_dropdown(ws, "L", 5, 1004, '"Classroom,Lab"', "Choose the required room type.")
        add_dropdown(ws, "K", 5, 1004, "=Faculty!$A$5:$A$504", "Choose a code from the Faculty sheet.")
        add_dropdown(ws, "J", 5, 1004, '"1,2,3"', "Duration is measured in periods.")

    template = wb.create_sheet("Year Template")
    add_title(template, "Copy this sheet for another year", "Duplicate this tab, rename it Year 4 (or the next configured year), and add rows. Do not edit the required column names.", len(headers))
    add_table(template, headers, [], "YearTemplateRequirements", widths)
    add_dropdown(template, "H", 5, 1004, '"Lecture,Lab"', "Choose Lecture or Lab.")
    add_dropdown(template, "K", 5, 1004, "=Faculty!$A$5:$A$504", "Choose a code from the Faculty sheet.")

    resources = wb.create_sheet("Resources")
    add_title(resources, "Rooms and Labs", "List real, schedulable resources. Capacity is the maximum number of students in the room.", 7)
    add_table(resources,
              ["Resource Code", "Resource Name", "Type", "Capacity", "Equipment", "Active", "Shared"],
              [["CR001", "CR-01", "Classroom", 70, "Projector", "Yes", "No"],
               ["CR002", "CR-02", "Classroom", 60, "Projector, Whiteboard", "Yes", "No"],
               ["CR003", "CR-03", "Classroom", 60, "Whiteboard", "Yes", "No"],
               ["CR004", "CR-04", "Classroom", 70, "Projector", "Yes", "No"],
               ["CR005", "CR-05", "Classroom", 65, "Whiteboard", "Yes", "No"],
               ["LAB001", "LAB-01", "Lab", 30, "Computer, LAN", "Yes", "No"],
               ["LAB002", "LAB-02", "Lab", 30, "Computer, LAN", "Yes", "No"],
               ["LAB003", "LAB-03", "Lab", 30, "Electronics, DSO", "Yes", "No"],
               ["LAB004", "LAB-04", "Lab", 30, "Computer, LAN", "Yes", "No"]],
              "ResourceDirectory", [18, 22, 18, 14, 32, 14, 14])
    add_dropdown(resources, "C", 5, 504, '"Classroom,Lab"', "Choose the resource type.")
    add_dropdown(resources, "F", 5, 504, '"Yes,No"', "Set whether the resource is schedulable.")
    add_dropdown(resources, "G", 5, 504, '"Yes,No"', "Set whether the resource is shared.")

    slots = wb.create_sheet("Time Slots")
    add_title(slots, "Weekly Bell Schedule", "Order is per day. Breaks and lunch must be represented explicitly so labs cannot cross them.", 5)
    daily = [("9:00 AM", "10:00 AM", "Teaching"), ("10:00 AM", "11:00 AM", "Teaching"),
             ("11:00 AM", "11:15 AM", "Break"), ("11:15 AM", "12:15 PM", "Teaching"),
             ("12:15 PM", "1:15 PM", "Teaching"), ("1:15 PM", "2:00 PM", "Lunch"),
             ("2:00 PM", "3:00 PM", "Teaching"), ("3:00 PM", "4:00 PM", "Teaching")]
    time_rows = [[day, order, start, end, kind]
                 for day in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")
                 for order, (start, end, kind) in enumerate(daily, 1)]
    add_table(slots, ["Day", "Order", "Start Time", "End Time", "Type"], time_rows,
              "WeeklyTimeSlots", [18, 14, 18, 18, 18])
    add_dropdown(slots, "A", 5, 504, '"Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday"', "Choose a day.")
    add_dropdown(slots, "E", 5, 504, '"Teaching,Break,Lunch"', "Choose a period type.")

    wb.calculation.fullCalcOnLoad = True
    wb.properties.title = "ClashFree Academic Timetable Setup"
    wb.properties.subject = "Faculty, curriculum, resources, and weekly time slots"
    output = Path(__file__).resolve().parents[1] / "assets" / "templates" / "CLASHFREE_Input_Template.xlsx"
    output.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output)
    return output


if __name__ == "__main__":
    print(f"Created {build_workbook()}")
