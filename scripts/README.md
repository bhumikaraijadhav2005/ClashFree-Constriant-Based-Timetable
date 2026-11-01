# Project scripts

- `create_excel_template.py` rebuilds the official workbook in `assets/templates/`.
- `manual/seed_multi_dept.py` mutates `backend/data_store.json` to add sample department data. Run only against disposable local data.
- `archive/legacy_patch_db.py` is a historical source-edit script retained for reference. Do not run it.

Normal application startup and tests do not execute scripts in `manual/` or `archive/`.
