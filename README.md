# ClashFree – Constraint-Based Timetable & Academic Resource Management System
### College Mini Project | BTech CSE (2nd Year)

---

## 🚀 Architecture Overview

ClashFree is built using a clean, modern, and viva-friendly full-stack architecture:

- **Frontend**: React + Modern CSS (Vite build system)
- **Backend**: Python + Flask REST API
- **Database**: Supabase PostgreSQL
- **Excel Processing**: `openpyxl`
- **Scheduling Engine**: CSP (Constraint Satisfaction Problem) + MRV (Minimum Remaining Values) + Backtracking

```
Browser (React Frontend - 11 Views & Role Switcher)
          ↓ (REST API / CORS)
     Flask Backend (app.py)
          ↓
 Supabase PostgreSQL ↔ Python CSP+MRV Scheduling Engine
```

---

## 📁 Project Structure

```
ClashFree/
│
├── backend/
│   ├── app.py             ← Flask REST API endpoints (Occupancy, Sharing, Workload, Timetable)
│   ├── db.py              ← Supabase PostgreSQL connection & resilient CRUD
│   ├── scheduler.py       ← CSP + MRV + Backtracking engine with HOD reservations
│   ├── excel_reader.py    ← Multi-sheet Excel parser & validator (.xlsx)
│   └── schema.sql         ← Complete database schema for Supabase SQL Editor
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx        ← React application & 11 ERP navigation views
│   │   ├── api.js         ← API client connecting to Flask backend
│   │   └── index.css      ← Clean, professional stylesheet & print styles
│   └── package.json       ← Frontend dependencies
│
├── .env                   ← Configured Supabase credentials
├── .env.example           ← Environment variables template
├── sample_data.xlsx       ← Comprehensive multi-sheet test dataset (8 sheets)
├── create_sample.py       ← Script to generate sample_data.xlsx
├── test_scheduler.py      ← Automated verification test suite
├── requirements.txt       ← Python dependencies
├── run.bat                ← One-click Windows launch script
└── README.md
```

---

## ⚡ How to Setup & Run

### 1. Database Setup (Supabase)
1. Go to [supabase.com](https://supabase.com) and create or open your project.
2. In your Supabase dashboard, open the **SQL Editor**.
3. Copy the contents of [`backend/schema.sql`](backend/schema.sql) and click **Run**.
4. In your project root, verify your `.env` file:
   ```ini
   SUPABASE_URL=https://your-project-ref.supabase.co
   SUPABASE_KEY=your-supabase-anon-or-service-key
   PORT=5000
   ```

### 2. Backend Setup
1. In the root directory, install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the Flask backend:
   ```bash
   python backend/app.py
   ```
   *Runs at `http://127.0.0.1:5000`*

### 3. Frontend Setup
1. Open a new terminal and navigate to `frontend`:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
2. Open your browser at `http://localhost:5173`.

### 4. Run Automated Tests
```bash
python test_scheduler.py
```

---

## 🎯 Completed Upgrades & Features

### 1. HOD Resource Reservation Policy
- Configurable reserved count for classrooms and labs (e.g. 1 out of 10 classrooms reserved, 1 out of 6 labs reserved).
- Scheduler strictly considers `Total - Reserved` resources and keeps reserved rooms untouched for seminars, electives, or emergency use.

### 2. Slot-Wise Resource Occupancy Module
- Real-time slot matrix: user selects **Day**, **Time Slot**, **Department**, and **Resource Type**.
- Live indicators: **OCCUPIED**, **AVAILABLE**, **RESERVED**.
- Detailed allocation cards showing Division/Batch, Faculty, Subject, and Room capacity.
- Slot-wise occupancy percentages for classrooms and labs.

### 3. Inter-Department Resource Sharing
- Free/available resources identifiable across departments (e.g. E&TC can request free CSE classroom CR-03).
- Complete workflow: **PENDING** → **APPROVED** / **REJECTED** with HOD approval controls.
- Structural clash prevention across departments.

### 4. Academic Structure & Batch-Level Lab Scheduling
- Hierarchical structure: Department → Degree → Year → Semester → Division → Batch.
- Individual student strengths per division (e.g. Div A = 75 students, Div B = 72 students).
- Lab sessions scheduled **batch-wise** (e.g. Batch A1 in Lab 1, Batch A2 in Lab 2) with Student:PC ratio constraints.

### 5. Central Master Timetable & Filtered Views
- Single source of truth containing Academic Year, Department, Semester, Day, Period, Division, Batch, Subject, Faculty, and Room.
- Filtered views generated from the same dataset:
  1. Master Timetable
  2. Division-wise Timetable
  3. Batch-wise Timetable
  4. Faculty-wise Timetable
  5. Classroom-wise Timetable
  6. Lab-wise Timetable

### 6. Faculty Initials & Workload Analysis
- Automatic initials generation with honorific stripping:
  - `Mr. Vishal H. Pundikar` → `VHP`
  - `Dr. Vikas L. Bhise` → `VLB`
  - `Dr. Amit R. Sharma` → `ARS`
- Weekly workload tracking (Lecture hours, Lab hours, Max allowed load, Overload/Underload status).
- Standardized college Academic Load Report table.

### 7. Break and Lunch Handling
- Breaks and lunch periods configured as `SHORT_BREAK` and `LUNCH`.
- Structurally impossible for the CSP engine to schedule classes during non-teaching intervals.

### 8. Timetable Version History & Auditing
- Version tracking (`v1`, `v2`, `v3`) with created date, description, and active status toggle.

### 9. Multi-Sheet Excel Import & Export
- Import support for: `Departments`, `Divisions`, `Batches`, `Faculty`, `Rooms`, `Labs`, `Subjects`, `Sections`.
- Comprehensive validation report showing imported rows, rejected rows, and missing fields.
- Excel `.xlsx` download for Master Timetable and Academic Load Report.
- Clean printable PDF layouts via browser print preview.

### 10. Role-Based Access Control
- Live role switcher in header: `ADMIN`, `HOD`, `TIMETABLE_COORDINATOR`, `DEPARTMENT_COORDINATOR`.
