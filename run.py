import os
import sys
import subprocess
import time
import webbrowser

def main():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)

    print("=" * 60)
    print("Starting ClashFree Timetable System...")
    print("=" * 60)

    backend_script = os.path.join(project_dir, "backend", "app.py")
    frontend_dir = os.path.join(project_dir, "frontend")

    # Ensure node_modules exists
    node_modules = os.path.join(frontend_dir, "node_modules")
    if not os.path.exists(node_modules):
        print("[Setup] Installing frontend dependencies (npm install)...")
        npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        subprocess.run([npm_cmd, "install"], cwd=frontend_dir, check=True)

    # 1. Start Flask backend server
    print("[1/3] Starting Flask Backend Server (http://127.0.0.1:5000)...")
    backend_proc = subprocess.Popen(
        [sys.executable, backend_script],
        cwd=project_dir,
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
    )

    # 2. Start React Vite frontend server
    print("[2/3] Starting React Vite Frontend Server (http://localhost:5173)...")
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=frontend_dir,
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
    )

    # 3. Wait for servers to spin up
    time.sleep(3)

    # 4. Open default web browser safely
    print("[3/3] Opening browser at http://localhost:5173...")
    try:
        webbrowser.open("http://localhost:5173")
    except Exception as e:
        print(f"Could not open browser automatically: {e}")
        print("Please open http://localhost:5173 manually in your browser.")

    print("\n" + "=" * 60)
    print("ClashFree is running!")
    print("Backend API:  http://127.0.0.1:5000")
    print("Frontend UI:  http://localhost:5173")
    print("Keep this window open. Press Ctrl+C to stop both servers.")
    print("=" * 60 + "\n")

    try:
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None and frontend_proc.poll() is not None:
                break
    except KeyboardInterrupt:
        print("\nShutting down ClashFree servers...")
        try:
            backend_proc.terminate()
        except Exception:
            pass
        try:
            frontend_proc.terminate()
        except Exception:
            pass
        print("Servers stopped cleanly.")

if __name__ == "__main__":
    main()

