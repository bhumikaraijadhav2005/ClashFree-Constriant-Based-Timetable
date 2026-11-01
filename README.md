# ClashFree Timetable

ClashFree is a React and Flask application for configuring college teaching data, generating timetables with CSP, MRV and backtracking, and viewing timetable and resource reports. Supabase is the intended database; a local JSON fallback remains in the current implementation.

## Current capabilities

- Department-aware pages and API operations, with year and semester filters discovered from configured records.
- A styled multi-sheet Excel setup workbook with a master Faculty directory, separate year tabs, a reusable Year Template, Resources, and Time Slots.
- Workbook validation before import, faculty/resource suitability checks, automatic lab group creation for oversized divisions, and explicit batch coverage checks.
- Duration-aware scheduling that excludes breaks/lunch and requires contiguous teaching periods with no clock gap.
- Timetable version creation and restore support in the existing application.
- Department-scoped imported bell schedules. Apply the additive migration in `backend/schema.sql` before using this feature with Supabase.

## Project layout

```text
backend/                 Flask API, scheduler, database access, schema, local store
frontend/                React application and frontend package files
assets/templates/        Official Excel workbook served by the API
tests/                   Automated backend regression and scheduler tests
tests/manual/            Manual acceptance flow that writes local test data
scripts/                 Template generator and explicit maintenance tools
docs/                    Deployment notes and deployment blockers
```

## Local development

From the project root, create and activate a Python virtual environment, then install backend dependencies:

```sh
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env`. Supabase credentials are read by Flask only; keep `.env` local and untracked, and never put credentials in frontend variables. If real credentials were committed previously, rotate them in Supabase. Start both local services with:

```sh
python run.py
```

If frontend packages are not installed yet, run `npm install` from `frontend` first. You can also start the API with `python backend/app.py` and start Vite separately with `npm run dev` from `frontend`.

The API listens on port 5000 and Vite serves the UI on port 5173. The default development API URL is `http://127.0.0.1:5000/api`. To use a different API base, set `VITE_API_BASE_URL` at frontend build time, including the `/api` suffix.

## Excel setup workbook

Download the workbook from the Import page or regenerate the example with:

```sh
python -B scripts/create_excel_template.py
```

The official workbook is `assets/templates/CLASHFREE_Input_Template.xlsx`. It contains `Instructions`, `Faculty`, `Year 1`, `Year 2`, `Year 3`, `Year Template`, `Resources`, and `Time Slots`. Faculty codes are defined once and reused in the year tabs. To add a year, duplicate `Year Template` and rename it to the next `Year N`. Validate the workbook in the application before importing it.

## Checks

Run backend regression tests from the project root:

```sh
pytest -q
```

Run the frontend production build from `frontend`:

```sh
npm run build
```

`npm run lint` currently reports existing warnings in `App.jsx` and `api.js`; it is not yet warning-free.

## Deployment status

For a WSGI server on Linux, build `frontend/dist`, serve it through a static host or reverse proxy, and run the Flask API with:

```sh
gunicorn --bind 0.0.0.0:${PORT:-5000} backend.wsgi:app
```

Set `CORS_ORIGINS` to exact UI origins when using separate hosts. `FLASK_DEBUG` defaults to false, and uploads are limited by `MAX_UPLOAD_BYTES`.

**This codebase is not yet safe for public production deployment with real college data.** Authentication, college membership authorization, full college-level schema scope, restrictive RLS policies, atomic Excel persistence, and complete active-version scope guarantees are not implemented. The existing schema grants broad access to `anon` and disables RLS; do not expose the current database publicly. See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for the blockers and migration notes.
