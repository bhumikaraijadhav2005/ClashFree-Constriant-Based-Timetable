import data as db
import excel_reader
import scheduler

# Load data
all_data, errors = excel_reader.read_excel("sample_data.xlsx")
if errors:
    print("ERRORS:", errors)
else:
    all_data["faculty"] = db.generate_faculty_codes(all_data["faculty"])
    db.faculty_list  = all_data["faculty"]
    db.room_list     = all_data["rooms"]
    db.subject_list  = all_data["subjects"]
    db.section_list  = all_data["sections"]
    db.data_loaded   = True

    print("Faculty codes:")
    for f in db.faculty_list:
        print("  " + f["name"] + " -> " + f["code"] + " | preferred: " + f["preferred_time"])

    print()
    print("Running scheduler...")
    success, msg = scheduler.generate_timetable()
    print("Success:", success)
    print("Message:", msg)
    if success:
        print("Total entries:", len(db.timetable))
        print()
        print("First 15 entries:")
        for row in db.timetable[:15]:
            t = row["is_lab"] and "LAB" or "LEC"
            print("  " + row["day"].ljust(10) + row["period"].ljust(14) +
                  row["section"].ljust(7) + row["subject"].ljust(10) +
                  row["faculty_code"].ljust(6) + row["room"].ljust(10) + t)
