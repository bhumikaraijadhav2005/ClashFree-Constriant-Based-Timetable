# Run and deployment notes

## Local verification

1. Create a Python virtual environment and install `requirements.txt`.
2. Copy `.env.example` to `.env`; configure a server-side Supabase URL and key only when using Supabase.
3. Apply `backend/schema.sql` to a disposable Supabase project before testing database-backed behavior. This project currently includes permissive legacy grants and does not have login or college membership authorization; do not expose it publicly with real college data.
4. Run the API with `python backend/app.py` and the UI from `frontend` with `npm install` followed by `npm run dev`.
5. Run checks from the project root with `pytest -q`, and build the UI from `frontend` with `npm run build`.

The official workbook is `assets/templates/CLASHFREE_Input_Template.xlsx`; regenerate it with `python -B scripts/create_excel_template.py`. It includes a faculty directory, one tab per year, a reusable year template, resources, and per-day time slots. Numbered year tabs are discovered dynamically. Validate a workbook before importing it.

## Production process entry point

Build the frontend with `npm run build` from `frontend`. Configure the hosting layer to serve `frontend/dist` and route `/api/*` to the Flask application, or set `VITE_API_BASE_URL` at frontend build time to the API base ending in `/api`. Run Flask through a WSGI server, for example on Linux:

```sh
gunicorn --bind 0.0.0.0:${PORT:-5000} backend.wsgi:app
```

Set `CORS_ORIGINS` to the exact browser origins if the UI and API use different origins. `FLASK_DEBUG` defaults to false. Set a request size limit with `MAX_UPLOAD_BYTES` as needed.

## Deployment blockers to resolve first

- Authentication and college/department membership checks are not implemented.
- The existing schema disables RLS and grants broad access to `anon`; inspect and replace those policies only after the ownership model is designed.
- Most schema rows are department-scoped by text rather than stable college and academic context IDs. Several data helpers still have local fallback behavior, and Excel writes are not an atomic database transaction.
- Timetable version uniqueness/activation is not protected by a database constraint, and version scoping is incomplete for academic year, semester, year, and division.
- The UI still contains fixed academic-year/semester defaults. Full multi-college operation has not been verified against a live Supabase instance.

Use a disposable database and synthetic data for integration tests until these controls exist. Never use this deployment configuration as a substitute for authorization or RLS.
