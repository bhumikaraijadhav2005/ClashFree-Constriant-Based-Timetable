# ClashFree – Constraint-Based Timetable & Lab Scheduling System
### College Mini Project | BTech CSE (2nd Year)

---

## 🚀 Architecture Overview

ClashFree is built using a clean, modern, and viva-friendly full-stack architecture:

- **Frontend**: React + Modern CSS (Vite build system)
- **Backend**: Python + Flask REST API
- **Database**: Supabase PostgreSQL
- **Excel Processing**: `openpyxl`
- **Scheduling Engine**: CSP (Constraint Satisfaction Problem) + MRV + Backtracking

```
Browser (React Frontend)
          ↓ (REST API / CORS)
    Flask Backend
          ↓
 Supabase PostgreSQL ↔ Python CSP Scheduling Engine
```

---

## 📁 Project Structure

```
ClashFree/
│
├── backend/
│   ├── app.py             ← Flask REST API endpoints
│   ├── db.py              ← Supabase PostgreSQL connection & CRUD
│   ├── scheduler.py       ← CSP + MRV + Backtracking engine
│   ├── excel_reader.py    ← Excel (.xlsx) parser & validator
│   └── schema.sql         ← Database schema for Supabase SQL Editor
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx        ← React application & 9 sidebar views
│   │   ├── api.js         ← API client connecting to Flask
│   │   └── index.css      ← Clean, professional design stylesheet
│   └── package.json       ← Frontend dependencies
│
├── .env.example           ← Environment variables template
├── sample_data.xlsx       ← Sample test dataset
├── requirements.txt       ← Python dependencies
└── README.md
```

---

## ⚡ How to Setup & Run

### 1. Database Setup (Supabase)
1. Go to [supabase.com](https://supabase.com) and create a free project.
2. In your Supabase dashboard, open the **SQL Editor**.
3. Copy the contents of [`backend/schema.sql`](backend/schema.sql) and click **Run**.
4. In your project root, create a `.env` file (copy from `.env.example`):
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

---

## 🎯 55–60% Completed Functionality
- ✅ **React Dashboard & Navigation**: Full 9-item sidebar navigation (Dashboard, Timetable, Faculty, Rooms, Subjects, Sections, Preferences, Conflicts, Import).
- ✅ **Supabase PostgreSQL Integration**: Real cloud database storage for all entities.
- ✅ **Excel Import & Validation**: One-click upload of `.xlsx` files with row validation.
- ✅ **Faculty Short-Code Engine**: Automatic generation of unique initials (e.g. `Kunal Patil` → `KP1`, `Kiran Patil` → `KP2`).
- ✅ **Customization & Preferences**: Hard availability restrictions vs. soft morning preferences.
- ✅ **CSP Scheduling Engine**: Variables, Domains, MRV (Minimum Remaining Values), Backtracking, and Hard Constraint verification.
- ✅ **Conflict Diagnostics**: Clear explanations for timetable conflicts.

---

## 🔮 Future Work (Remaining ~40%)
- Advanced multi-objective soft optimization (minimizing gaps, instructor idle time).
- Export to PDF and Excel formats.
- Role-based user authentication (HOD vs. Faculty).
