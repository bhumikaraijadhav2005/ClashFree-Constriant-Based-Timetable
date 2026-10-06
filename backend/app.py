# backend/app.py
# Flask RESTful API server for ClashFree
# Connects to Supabase PostgreSQL (or fallback storage), processes Excel files, and runs CSP Scheduling.

import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
from dotenv import load_dotenv

# Explicitly load .env from project root directory
root_dir = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=root_dir / ".env")
load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import db
import excel_reader
import scheduler

load_dotenv()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------------------------------------------------------------------
# HEALTH & CONFIG STATUS
# ---------------------------------------------------------------------------
@app.route("/api/status", methods=["GET"])
def get_status():
    configured = db.is_configured()
    return jsonify({
        "status": "online",
        "supabase_configured": configured,
        "message": "Connected to Supabase" if configured else "Running with in-memory storage (add Supabase credentials anytime)"
    })


# ---------------------------------------------------------------------------
# DASHBOARD SUMMARY
# ---------------------------------------------------------------------------
@app.route("/api/dashboard", methods=["GET"])
def get_dashboard():
    try:
        faculty = db.get_all_faculty()
        rooms = db.get_all_rooms()
        subjects = db.get_all_subjects()
        sections = db.get_all_sections()
        timetable = db.get_timetable()
        
        return jsonify({
            "configured": db.is_configured(),
            "counts": {
                "faculty": len(faculty),
                "rooms": len(rooms),
                "subjects": len(subjects),
                "sections": len(sections),
                "scheduled": len(timetable),
                "conflicts": 0
            }
        })
    except Exception as e:
        return jsonify({"error": str(e), "configured": db.is_configured()}), 500


# ---------------------------------------------------------------------------
# FACULTY CRUD
# ---------------------------------------------------------------------------
@app.route("/api/faculty", methods=["GET", "POST"])
def manage_faculty():
    if request.method == "GET":
        try:
            data = db.get_all_faculty()
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == "POST":
        try:
            payload = request.json
            if not payload.get("code"):
                name = payload.get("name", "")
                parts = name.strip().split()
                base = (parts[0][0] + parts[-1][0]).upper() if len(parts) >= 2 else parts[0][:2].upper()
                payload["code"] = base

            res = db.upsert_faculty(payload)
            return jsonify({"success": True, "data": getattr(res, "data", [payload])})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route("/api/faculty/<int:fid>", methods=["DELETE"])
def delete_faculty_item(fid):
    try:
        db.delete_faculty(fid)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# ROOMS CRUD
# ---------------------------------------------------------------------------
@app.route("/api/rooms", methods=["GET", "POST"])
def manage_rooms():
    if request.method == "GET":
        try:
            data = db.get_all_rooms()
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == "POST":
        try:
            payload = request.json
            res = db.upsert_room(payload)
            return jsonify({"success": True, "data": getattr(res, "data", [payload])})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route("/api/rooms/<int:rid>", methods=["DELETE"])
def delete_room_item(rid):
    try:
        db.delete_room(rid)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# SUBJECTS CRUD
# ---------------------------------------------------------------------------
@app.route("/api/subjects", methods=["GET", "POST"])
def manage_subjects():
    if request.method == "GET":
        try:
            data = db.get_all_subjects()
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == "POST":
        try:
            payload = request.json
            res = db.upsert_subject(payload)
            return jsonify({"success": True, "data": getattr(res, "data", [payload])})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route("/api/subjects/<int:sid>", methods=["DELETE"])
def delete_subject_item(sid):
    try:
        db.delete_subject(sid)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# SECTIONS CRUD
# ---------------------------------------------------------------------------
@app.route("/api/sections", methods=["GET", "POST"])
def manage_sections():
    if request.method == "GET":
        try:
            data = db.get_all_sections()
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == "POST":
        try:
            payload = request.json
            res = db.upsert_section(payload)
            return jsonify({"success": True, "data": getattr(res, "data", [payload])})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route("/api/sections/<int:sec_id>", methods=["DELETE"])
def delete_section_item(sec_id):
    try:
        db.delete_section(sec_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# EXCEL IMPORT
# ---------------------------------------------------------------------------
@app.route("/api/import-excel", methods=["POST"])
def import_excel():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    if not file.filename.endswith(".xlsx"):
        return jsonify({"error": "Only .xlsx files are supported"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, "temp_import.xlsx")
    file.save(filepath)

    data_dict, errors = excel_reader.read_excel(filepath)
    if errors:
        return jsonify({"errors": errors}), 400

    data_dict["faculty"] = excel_reader.generate_faculty_codes(data_dict["faculty"])

    try:
        db.insert_faculty(data_dict["faculty"])
        db.insert_rooms(data_dict["rooms"])
        db.insert_subjects(data_dict["subjects"])
        db.insert_sections(data_dict["sections"])
    except Exception as e:
        return jsonify({"error": f"Database insertion failed: {str(e)}"}), 500

    return jsonify({
        "success": True,
        "summary": {
            "faculty": len(data_dict["faculty"]),
            "rooms": len(data_dict["rooms"]),
            "subjects": len(data_dict["subjects"]),
            "sections": len(data_dict["sections"])
        }
    })


# ---------------------------------------------------------------------------
# TIMETABLE & SCHEDULER
# ---------------------------------------------------------------------------
@app.route("/api/timetable", methods=["GET"])
def get_timetable_data():
    try:
        data = db.get_timetable()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-timetable", methods=["POST"])
def run_scheduler():
    try:
        faculty = db.get_all_faculty()
        rooms = db.get_all_rooms()
        subjects = db.get_all_subjects()
        sections = db.get_all_sections()

        success, message, timetable_rows, conflicts = scheduler.generate_timetable(
            faculty, rooms, subjects, sections
        )

        if success:
            db.save_timetable(timetable_rows)
            return jsonify({
                "success": True,
                "message": message,
                "count": len(timetable_rows),
                "timetable": timetable_rows,
                "conflicts": []
            })
        else:
            return jsonify({
                "success": False,
                "message": message,
                "conflicts": conflicts
            }), 422
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "conflicts": [str(e)]}), 500


# ---------------------------------------------------------------------------
# CONFLICTS CHECK
# ---------------------------------------------------------------------------
@app.route("/api/conflicts", methods=["GET"])
def get_conflicts():
    try:
        faculty = db.get_all_faculty()
        rooms = db.get_all_rooms()
        subjects = db.get_all_subjects()
        sections = db.get_all_sections()

        _, _, _, conflicts = scheduler.generate_timetable(faculty, rooms, subjects, sections)
        return jsonify({"conflicts": conflicts})
    except Exception as e:
        return jsonify({"conflicts": [f"Error checking conflicts: {str(e)}"]})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"ClashFree Backend API running on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
