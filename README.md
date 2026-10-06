# ClashFree – Constraint-Based Timetable & Lab Scheduling System
### College Mini Project | BTech CSE (2nd Year)

---

## What is ClashFree?

ClashFree is a **web-based timetable scheduling system** that automatically generates a conflict-free weekly timetable for a college.

Instead of manually placing every lecture, the admin uploads an Excel file with faculty, rooms, subjects, and sections — and the system figures out the schedule automatically using:

- **CSP** (Constraint Satisfaction Problem)
- **MRV** (Minimum Remaining Values heuristic)
- **Backtracking**

---

## Folder Structure

```
ClashFree/
│
├── app.py              ← Starts the Flask website
├── scheduler.py        ← Core scheduling logic (CSP + MRV + Backtracking)
├── excel_reader.py     ← Reads the uploaded Excel file
├── data.py             ← Stores all project data in memory
├── create_sample.py    ← Creates sample_data.xlsx for testing
├── test_scheduler.py   ← Quick test script (not needed for demo)
├── requirements.txt    ← Python packages needed
├── sample_data.xlsx    ← Sample Excel file for testing
│
├── templates/
│   ├── index.html          ← Home / Dashboard page
│   ├── upload.html         ← Upload Excel page
│   ├── data.html           ← View loaded data page
│   ├── faculty_codes.html  ← Faculty short codes page
│   └── timetable.html      ← Generate & view timetable page
│
└── static/
    └── style.css       ← Styling for all web pages
```

---

## File Explanations (Beginner-Friendly)

### `app.py`
> **"Starts the Flask website and connects the web pages to the Python functions."**

This is the main file. When you run `python app.py`, it starts a local web server.
Each web page (like `/upload`, `/generate`) is linked to a Python function here.
It receives data from HTML forms, calls `excel_reader.py` and `scheduler.py`, and sends results back to the browser.

---

### `scheduler.py`
> **"Contains the CSP, MRV, Backtracking and constraint checking logic."**

This is the "brain" of the project. It:
1. Builds a list of sessions to schedule (CSP Variables)
2. Builds a list of valid options for each session (CSP Domains)
3. Uses MRV to pick which session to schedule first
4. Uses Backtracking to try options and undo bad choices
5. Checks hard constraints (no double-booking of faculty, rooms, or sections)

---

### `excel_reader.py`
> **"Reads the uploaded Excel file and converts it into Python data."**

It opens the `.xlsx` file using `openpyxl` and reads 4 sheets:
- **Faculty** sheet → list of faculty with availability and preferences
- **Rooms** sheet → list of classrooms and labs
- **Subjects** sheet → list of subjects with weekly session counts
- **Sections** sheet → list of student sections

It also validates the data and returns easy-to-understand error messages.

---

### `data.py`
> **"Stores and manages the loaded project data."**

Think of this as the project's "memory".
All data (faculty, rooms, subjects, sections, timetable) lives here in simple Python lists.
Other files import from `data.py` to read or write data.

It also contains `generate_faculty_codes()` which automatically creates short unique codes like `KP1`, `KP2` from full names.

---

### `templates/`
> **"Contains the HTML pages shown in the browser."**

- `index.html` — Home dashboard with quick-action cards
- `upload.html` — Upload Excel file form + post-upload summary
- `data.html` — Tables showing all loaded faculty, rooms, subjects, sections
- `faculty_codes.html` — Table showing Full Name → Short Code mapping
- `timetable.html` — Generate button + filterable timetable display

---

### `static/style.css`
> **"Controls the appearance (colors, layout, fonts) of all web pages."**

Simple CSS with no external framework. Easy to read and modify.

---

## How to Run the Project

### Step 1 — Make sure Python is installed
Open Command Prompt and type:
```
python --version
```
You should see something like `Python 3.12.x`. If not, download Python from https://python.org

---

### Step 2 — Open the project folder in VS Code
Open VS Code → File → Open Folder → select the `ClashFree` folder.

---

### Step 3 — Open Terminal in VS Code
Press `` Ctrl + ` `` to open the built-in terminal.

---

### Step 4 — (Optional) Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```
This creates an isolated Python environment. Recommended but not required.

---

### Step 5 — Install required packages
```bash
pip install -r requirements.txt
```
This installs Flask and openpyxl.

---

### Step 6 — Create the sample Excel file
```bash
python create_sample.py
```
This creates `sample_data.xlsx` in the project folder.

---

### Step 7 — Run the application
```bash
python app.py
```

You will see:
```
===============================================
  ClashFree – Timetable Scheduling System
===============================================
  Open this address in Chrome:
  http://127.0.0.1:5000
===============================================
```

---

### Step 8 — Open in Chrome
Open Chrome and go to:
```
http://127.0.0.1:5000
```

---

## How to Test the Project

### Step 1 — Upload the sample Excel
1. Click **"Upload Excel"** on the home page
2. Click **"Choose File"** and select `sample_data.xlsx`
3. Click **"Upload Excel"**
4. You should see: `Excel uploaded successfully!`
5. Summary shows: Faculty: 6 | Rooms: 6 | Subjects: 6 | Sections: 2

### Step 2 — View the Data
Click **"View Data"** to see all faculty, rooms, subjects, and sections in tables.

### Step 3 — View Faculty Codes
Click **"Faculty Codes"** to see:
| Full Name | Short Code |
|-----------|------------|
| Kunal Patil | KP1 |
| Kiran Patil | KP2 |
| Amit Sharma | AS |
| Sneha Desai | SD |
| Rahul Mehta | RM |
| Priya Joshi | PJ |

> Note: Kunal and Kiran both have initials KP, so the system automatically assigns **KP1** and **KP2**.

### Step 4 — Generate Timetable
1. Click **"Generate Timetable"**
2. Click the green **"Generate Timetable"** button
3. The system schedules all sessions using CSP + MRV + Backtracking
4. You will see a table with all scheduled classes and labs
5. Use the **Section** and **Day** filters to view specific results

---

## Where Key Concepts are Implemented

| Concept | File | What it does |
|---------|------|-------------|
| CSP Variables | `scheduler.py → build_sessions()` | Creates one session object per class/lab to be scheduled |
| CSP Domains | `scheduler.py → build_domain()` | Lists all valid (slot + room + faculty) options for each session |
| MRV | `scheduler.py → pick_next_session()` | Picks the session with the fewest remaining valid options |
| Backtracking | `scheduler.py → backtrack()` | Tries options, and undoes assignments when stuck |
| Hard Constraints | `scheduler.py → is_valid()` | Checks no faculty, room, or section clash |
| Faculty Availability | `scheduler.py → faculty_is_available()` | Skips slots outside faculty's available hours |
| Soft Preference | `scheduler.py → build_domain() → preference_key` | Sorts morning slots first for morning-preferring faculty |
| Excel Reading | `excel_reader.py → read_excel()` | Reads all 4 sheets with validation |
| Faculty Short Codes | `data.py → generate_faculty_codes()` | Generates unique short codes like KP1, KP2 |
| Data Storage | `data.py` | Stores all loaded data in simple Python lists |
| Web Routes | `app.py` | Connects URLs to Python functions |

---

## Complete Flow (Simple Explanation)

```
Excel File
    ↓
excel_reader.py reads Faculty, Rooms, Subjects, Sections
    ↓
data.py stores the data + generates faculty short codes (KP1, KP2...)
    ↓
scheduler.py: build_sessions() creates CSP Variables
    ↓
scheduler.py: build_domain() creates CSP Domains (all valid options per session)
    ↓
scheduler.py: pick_next_session() uses MRV to pick the hardest session first
    ↓
scheduler.py: backtrack() tries options one by one
    ↓
scheduler.py: is_valid() checks hard constraints (no clashes)
    ↓
If valid → assign it → move to next session
If stuck → undo last assignment → try another option (Backtracking)
    ↓
All sessions scheduled → Timetable stored in data.py
    ↓
app.py sends timetable to timetable.html → shown in browser
```

---

## Sample Data Details

| What | Value |
|------|-------|
| Sections | CSE-A (60 students), CSE-B (58 students) |
| Faculty | 6 faculty members |
| Subjects | DSA, DBMS, OS, CN, Maths, TOC |
| Classrooms | Room101, Room102, Room103, Room104 (capacity 60-65) |
| Labs | Lab1, Lab2 (capacity 65) |
| Faculty with same initials | Kunal Patil (KP1) + Kiran Patil (KP2) |
| Morning preference | Kunal Patil, Kiran Patil, Priya Joshi |
| Afternoon preference | Sneha Desai |
| DBMS has lab sessions | Yes (1 lab per week per section) |

---

## Short Viva Explanation

> **"ClashFree is a constraint-based timetable scheduling system. The admin uploads an Excel file with faculty, rooms, subjects, and sections. The system models each class or lab session as a CSP variable — a variable that needs to be assigned a time slot, room, and faculty. We use the MRV heuristic to always schedule the session with the fewest valid remaining options first, reducing the chance of getting stuck. We use backtracking to try options and undo bad assignments. Hard constraints ensure no faculty, room, or section is double-booked. Soft constraints try to place morning-preferring faculty in morning slots. The system generates a complete conflict-free weekly timetable automatically."**

---

## What is Completed (~60%)

✅ Excel file upload  
✅ Data validation with clear error messages  
✅ Faculty short-code generation (KP1, KP2 etc.)  
✅ Faculty hard availability  
✅ Faculty soft preference (morning/afternoon)  
✅ Multiple sections (CSE-A, CSE-B)  
✅ Classrooms and Labs with capacity  
✅ Subjects with weekly lecture and lab counts  
✅ Teaching periods only (no scheduling during breaks or lunch)  
✅ CSP modelling (variables + domains)  
✅ MRV heuristic  
✅ Backtracking search  
✅ Hard constraint checking (no clashes)  
✅ Timetable generation and display  
✅ Section and day filters on timetable  
✅ Faculty code lookup on timetable  

---

## Future Work (~40% remaining)

- [ ] PDF export of timetable
- [ ] Excel export of timetable
- [ ] Login / Authentication for admin
- [ ] Per-section subject assignment (currently all sections share all subjects)
- [ ] Advanced soft constraint optimization (minimize gaps, balance workload)
- [ ] Conflict explanation ("Faculty X has 3 clashes because...")
- [ ] Cloud / server deployment
- [ ] Advanced analytics and reports
- [ ] Mobile-friendly UI
- [ ] Edit data from the web interface (without re-uploading Excel)
