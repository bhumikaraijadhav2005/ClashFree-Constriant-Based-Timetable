with open("backend/app.py", "r", encoding="utf-8") as f:
    code = f.read()

target = """        if data_dict.get("requirements"):
            db.save_requirements(data_dict["requirements"])
        if data_dict.get("time_slots"):
            db.save_time_slots(data_dict["time_slots"])"""

replacement = """        if data_dict.get("requirements"):
            db.save_requirements(data_dict["requirements"])
        # Timetable structure/bell schedule is predefined in ClashFree and is not overwritten by data file uploads."""

assert target in code, "target not found in backend/app.py"
code = code.replace(target, replacement)

with open("backend/app.py", "w", encoding="utf-8") as f:
    f.write(code)

print("[OK] backend/app.py updated!")

