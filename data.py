# data.py
# This file stores all the project data after it is loaded from Excel.
# Think of it as a central "memory" that other files can read and write to.

# ---------------------------------------------------------------------------
# All project data lives in these simple lists / dictionaries.
# ---------------------------------------------------------------------------

# List of faculty members.
# Each entry is a dict, e.g.:
#   {
#       "name": "Karn Mishra",
#       "code": "KP1",
#       "subjects": ["DSA", "OS"],
#       "available_from": "09:00",
#       "available_to":   "16:00",
#       "preferred_time": "Morning"   # "Morning", "Afternoon", or "Any"
#   }
faculty_list = []

# List of rooms and labs.
# Each entry is a dict, e.g.:
#   {
#       "name": "Room101",
#       "type": "Classroom",   # "Classroom" or "Lab"
#       "capacity": 60
#   }
room_list = []

# List of subjects.
# Each entry is a dict, e.g.:
#   {
#       "name": "DSA",
#       "lectures_per_week": 4,
#       "labs_per_week": 0,
#       "requires_lab": False
#   }
subject_list = []

# List of sections.
# Each entry is a dict, e.g.:
#   {
#       "name": "CSE-A",
#       "strength": 60
#   }
section_list = []

# The last generated timetable.
# This is a list of scheduled entries.
# Each entry is a dict, e.g.:
#   {
#       "day": "Monday",
#       "period": "09:00-10:00",
#       "section": "CSE-A",
#       "subject": "DSA",
#       "faculty_code": "KP1",
#       "room": "Room101"
#   }
timetable = []

# Helper flag: has data been loaded?
data_loaded = False


def clear_all():
    """Reset everything so a fresh Excel upload starts clean."""
    global faculty_list, room_list, subject_list, section_list, timetable, data_loaded
    faculty_list = []
    room_list = []
    subject_list = []
    section_list = []
    timetable = []
    data_loaded = False


def generate_faculty_codes(faculty_data):
    """
    Automatically create a short unique code for each faculty member.

    Algorithm:
      1. Take the first letter of the first name and the first letter of the last name.
         Example: "Kunal Patil" → "KP"
      2. If two faculty members produce the same short code, add a number:
         "KP1", "KP2", etc.

    Returns the same list with a "code" key added to each faculty dict.
    """
    code_count = {}  # track how many times each base code appears

    for faculty in faculty_data:
        name_parts = faculty["name"].strip().split()

        if len(name_parts) >= 2:
            # Take first letter of first name + first letter of last name
            base_code = (name_parts[0][0] + name_parts[-1][0]).upper()
        else:
            # Only one word — use first two letters
            base_code = name_parts[0][:2].upper()

        # Count how many times this base code has appeared so far
        if base_code not in code_count:
            code_count[base_code] = 0
        code_count[base_code] += 1

    # Now assign unique codes (with numbers if needed)
    seen = {}
    occurrence = {}

    for faculty in faculty_data:
        name_parts = faculty["name"].strip().split()

        if len(name_parts) >= 2:
            base_code = (name_parts[0][0] + name_parts[-1][0]).upper()
        else:
            base_code = name_parts[0][:2].upper()

        if code_count[base_code] == 1:
            # Only one faculty with this code — no number needed
            faculty["code"] = base_code
        else:
            # Multiple faculty share this base code — add a number
            occurrence[base_code] = occurrence.get(base_code, 0) + 1
            faculty["code"] = base_code + str(occurrence[base_code])

    return faculty_data
