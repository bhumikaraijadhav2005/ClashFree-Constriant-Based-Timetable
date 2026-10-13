# scheduler.py
# Root delegator for ClashFree scheduler
# Forwards all imports directly to backend.scheduler

import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import scheduler as _backend_scheduler

# Forward all public attributes and functions
for _attr in dir(_backend_scheduler):
    if not _attr.startswith("__"):
        globals()[_attr] = getattr(_backend_scheduler, _attr)

generate_timetable = _backend_scheduler.generate_timetable
filter_and_reserve_resources = _backend_scheduler.filter_and_reserve_resources
diagnose_infeasibility = _backend_scheduler.diagnose_infeasibility
DEFAULT_SCHEDULE = _backend_scheduler.DEFAULT_SCHEDULE
DAYS = _backend_scheduler.DAYS
DAY_ORDER = _backend_scheduler.DAY_ORDER
