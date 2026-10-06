# app.py
# This is the main file that starts the Flask web server.
# It connects the web pages (HTML templates) to the Python functions.
# Run this file with:  python app.py

import os
from flask import Flask, render_template, request, redirect, url_for, flash, session

import data as db
import excel_reader
import scheduler

# Create the Flask application
app = Flask(__name__)
app.secret_key = "clashfree_secret_key_123"  # needed for flash messages

# Folder where uploaded Excel files are temporarily saved
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------------------------------------------------------------------
# HOME / DASHBOARD
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Show the home dashboard."""
    return render_template("index.html", data_loaded=db.data_loaded)


# ---------------------------------------------------------------------------
# UPLOAD EXCEL
# ---------------------------------------------------------------------------
@app.route("/upload", methods=["GET", "POST"])
def upload():
    """
    GET  → Show the upload form.
    POST → Handle the uploaded Excel file.
    """
    if request.method == "POST":
        # Check a file was actually selected
        if "excel_file" not in request.files:
            flash("No file selected. Please choose an Excel file.", "error")
            return redirect(url_for("upload"))

        file = request.files["excel_file"]

        if file.filename == "":
            flash("No Excel file selected.", "error")
            return redirect(url_for("upload"))

        if not file.filename.endswith(".xlsx"):
            flash("Invalid file format. Please upload a .xlsx file.", "error")
            return redirect(url_for("upload"))

        # Save the file temporarily
        filepath = os.path.join(UPLOAD_FOLDER, "uploaded_data.xlsx")
        file.save(filepath)

        # Read and validate the Excel file
        all_data, errors = excel_reader.read_excel(filepath)

        if errors:
            # Show all errors to the user
            for err in errors:
                flash(err, "error")
            return redirect(url_for("upload"))

        # Generate faculty short codes
        all_data["faculty"] = db.generate_faculty_codes(all_data["faculty"])

        # Store data in the global data module
        db.clear_all()
        db.faculty_list  = all_data["faculty"]
        db.room_list     = all_data["rooms"]
        db.subject_list  = all_data["subjects"]
        db.section_list  = all_data["sections"]
        db.data_loaded   = True

        # Build a summary to show the user
        summary = {
            "faculty":  len(db.faculty_list),
            "rooms":    len(db.room_list),
            "subjects": len(db.subject_list),
            "sections": len(db.section_list),
        }

        flash("Excel uploaded successfully!", "success")
        return render_template("upload.html", summary=summary)

    # GET request — just show the upload form
    return render_template("upload.html", summary=None)


# ---------------------------------------------------------------------------
# VIEW DATA
# ---------------------------------------------------------------------------
@app.route("/data")
def view_data():
    """Show all loaded data in simple tables."""
    if not db.data_loaded:
        flash("No data loaded yet. Please upload an Excel file first.", "error")
        return redirect(url_for("upload"))

    return render_template(
        "data.html",
        faculty_list  = db.faculty_list,
        room_list     = db.room_list,
        subject_list  = db.subject_list,
        section_list  = db.section_list,
    )


# ---------------------------------------------------------------------------
# FACULTY CODES
# ---------------------------------------------------------------------------
@app.route("/faculty_codes")
def faculty_codes():
    """Show the full name → short code mapping for all faculty."""
    if not db.data_loaded:
        flash("No data loaded yet. Please upload an Excel file first.", "error")
        return redirect(url_for("upload"))

    return render_template("faculty_codes.html", faculty_list=db.faculty_list)


# ---------------------------------------------------------------------------
# GENERATE TIMETABLE
# ---------------------------------------------------------------------------
@app.route("/generate", methods=["GET", "POST"])
def generate():
    """
    GET  → Show the generate page.
    POST → Run the scheduler and show the timetable.
    """
    if not db.data_loaded:
        flash("No data loaded yet. Please upload an Excel file first.", "error")
        return redirect(url_for("upload"))

    if request.method == "POST":
        success, message = scheduler.generate_timetable()

        if not success:
            flash(f"Error: {message}", "error")
            return render_template("timetable.html", timetable=[], message=message, success=False)

        flash(message, "success")
        return render_template(
            "timetable.html",
            timetable=db.timetable,
            faculty_list=db.faculty_list,
            message=message,
            success=True
        )

    return render_template("timetable.html", timetable=[], message=None, success=None)


# ---------------------------------------------------------------------------
# START THE SERVER
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 55)
    print("  ClashFree – Timetable Scheduling System")
    print("=" * 55)
    print("  Open this address in Chrome:")
    print("  http://127.0.0.1:5000")
    print("=" * 55)
    app.run(debug=True)
