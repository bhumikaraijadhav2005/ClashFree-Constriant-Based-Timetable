"""Launch the Flask API and Vite UI for a one-click local development run."""

from pathlib import Path
import os
import shutil
import subprocess
import sys
import time
import webbrowser


def start_process(command, cwd, new_console=False):
    options = {"cwd": cwd}
    if new_console and os.name == "nt":
        options["creationflags"] = subprocess.CREATE_NEW_CONSOLE
    return subprocess.Popen(command, **options)


def main():
    project_root = Path(__file__).resolve().parent
    frontend_dir = project_root / "frontend"
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if not npm:
        print("Node.js and npm are required. Install Node.js, then run run.bat again.")
        return 1

    if not (frontend_dir / "node_modules").is_dir():
        print("Installing frontend packages for the first run...")
        install = subprocess.run([npm, "install"], cwd=frontend_dir)
        if install.returncode:
            print("Frontend setup failed. Check the npm output above, then run run.bat again.")
            return install.returncode

    if os.name == "nt":
        frontend_command = ["cmd.exe", "/c", npm, "run", "dev"]
    else:
        frontend_command = [npm, "run", "dev"]

    backend = None
    frontend = None
    try:
        backend = start_process(
            [sys.executable, str(project_root / "backend" / "app.py")],
            project_root,
            new_console=True,
        )
        frontend = start_process(frontend_command, frontend_dir, new_console=True)
        print("ClashFree is starting. API: http://127.0.0.1:5000")
        print("The browser will open at http://localhost:5173")
        time.sleep(3)
        webbrowser.open("http://localhost:5173")
        print("Keep this launcher window open. Press Ctrl+C here to stop both servers.")
        while backend.poll() is None and frontend.poll() is None:
            time.sleep(0.5)
        return backend.poll() or frontend.poll() or 0
    except KeyboardInterrupt:
        print("Stopping ClashFree development servers...")
        return 0
    except OSError as error:
        print(f"Could not start ClashFree: {error}")
        return 1
    finally:
        for process in (frontend, backend):
            if process is not None and process.poll() is None:
                process.terminate()
        for process in (frontend, backend):
            if process is not None:
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


if __name__ == "__main__":
    raise SystemExit(main())
