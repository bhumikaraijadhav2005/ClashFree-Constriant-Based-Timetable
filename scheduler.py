# scheduler.py
# Root delegator for ClashFree scheduler
# Forwards all imports directly to backend.scheduler

import os
import sys
import importlib.util

backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "scheduler.py")
spec = importlib.util.spec_from_file_location("backend_scheduler", backend_path)
_backend_scheduler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_backend_scheduler)

generate_timetable = _backend_scheduler.generate_timetable
filter_and_reserve_resources = _backend_scheduler.filter_and_reserve_resources
diagnose_infeasibility = _backend_scheduler.diagnose_infeasibility
format_time_12h = _backend_scheduler.format_time_12h
time_to_minutes = _backend_scheduler.time_to_minutes
DEFAULT_SCHEDULE = _backend_scheduler.DEFAULT_SCHEDULE
DAYS = _backend_scheduler.DAYS
DAY_ORDER = _backend_scheduler.DAY_ORDER
