# app.py
# Root runner for ClashFree Backend API
# Delegates directly to backend/app.py

import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import app as backend_server

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print("=" * 60)
    print("  ClashFree – Constraint-Based Timetable & Academic Resource System")
    print(f"  Backend REST API running on http://127.0.0.1:{port}")
    print("=" * 60)
    backend_server.app.run(host="0.0.0.0", port=port, debug=True)
