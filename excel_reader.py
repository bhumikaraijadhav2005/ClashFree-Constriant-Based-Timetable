# excel_reader.py
# Root delegator for ClashFree excel_reader
# Forwards all imports directly to backend.excel_reader

import os
import sys
import importlib.util

backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "excel_reader.py")
spec = importlib.util.spec_from_file_location("backend_excel_reader", backend_path)
_backend_excel_reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_backend_excel_reader)

read_excel = _backend_excel_reader.read_excel
validate_excel_data = _backend_excel_reader.validate_excel_data
format_time_12h = _backend_excel_reader.format_time_12h
format_period_label = _backend_excel_reader.format_period_label
time_str_to_minutes = _backend_excel_reader.time_str_to_minutes
parse_availability_string = _backend_excel_reader.parse_availability_string
generate_faculty_codes = _backend_excel_reader.generate_faculty_codes
