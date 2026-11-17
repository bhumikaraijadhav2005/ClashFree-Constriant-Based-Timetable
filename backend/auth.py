# backend/auth.py
# ClashFree Role-Based Access Control & Authentication Engine
# Handles Supabase Auth integration, dual-mode fallback, password hashing,
# signed session tokens, permission scopes, and audit logging.

import os
import json
import time
import hmac
import base64
import hashlib
import secrets
from datetime import datetime
from functools import wraps
from flask import request, jsonify

# ---------------------------------------------------------------------------
# CONFIGURATION & SECRETS
# ---------------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "clashfree-secret-salt-key-2026-secure-token-engine")
TOKEN_EXPIRY_DEFAULT = 24 * 3600  # 1 day
TOKEN_EXPIRY_REMEMBER = 30 * 24 * 3600  # 30 days

# Role Constants
ROLE_SUPER_ADMIN = "SUPER_ADMIN"
ROLE_INSTITUTIONAL_VIEWER = "INSTITUTIONAL_VIEWER"
ROLE_HOD = "HOD"
ROLE_TIMETABLE_CREATOR = "TIMETABLE_CREATOR"
ROLE_FACULTY = "FACULTY"

ALL_ROLES = [
    ROLE_SUPER_ADMIN,
    ROLE_INSTITUTIONAL_VIEWER,
    ROLE_HOD,
    ROLE_TIMETABLE_CREATOR,
    ROLE_FACULTY,
]

# ---------------------------------------------------------------------------
# PASSWORD HASHING (PBKDF2-HMAC-SHA256)
# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    """Generate secure salted PBKDF2-HMAC-SHA256 hash."""
    if not password:
        raise ValueError("Password cannot be empty")
    salt = secrets.token_hex(16)
    iterations = 100000
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations
    )
    return f"pbkdf2:sha256:{iterations}${salt}${derived.hex()}"


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against stored PBKDF2 hash."""
    if not password or not hashed_password:
        return False
    try:
        parts = hashed_password.split("$")
        if len(parts) != 3:
            return False
        header, salt, original_hash = parts
        iterations = int(header.split(":")[-1])
        derived = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations
        )
        return hmac.compare_digest(derived.hex(), original_hash)
    except Exception:
        return False

# ---------------------------------------------------------------------------
# SESSION TOKEN GENERATION & VERIFICATION (HMAC-SHA256)
# ---------------------------------------------------------------------------
def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

def _base64url_decode(data: str) -> bytes:
    padding = 4 - (len(data) % 4)
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data)

def create_auth_token(payload: dict, expires_in: int = TOKEN_EXPIRY_DEFAULT) -> str:
    """Create a signed tamper-proof HMAC-SHA256 token."""
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload_copy = dict(payload)
    payload_copy["iat"] = now
    payload_copy["exp"] = now + expires_in

    header_bytes = json.dumps(header, separators=(",", ":")).encode("utf-8")
    payload_bytes = json.dumps(payload_copy, separators=(",", ":")).encode("utf-8")

    encoded_header = _base64url_encode(header_bytes)
    encoded_payload = _base64url_encode(payload_bytes)

    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
    signature = hmac.new(SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
    encoded_signature = _base64url_encode(signature)

    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"

def verify_auth_token(token: str) -> dict | None:
    """Verify cryptographic signature and expiration of token."""
    if not token or not isinstance(token, str):
        return None
    parts = token.strip().split(".")
    if len(parts) != 3:
        return None
    encoded_header, encoded_payload, encoded_signature = parts
    try:
        signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
        expected_sig = hmac.new(SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
        actual_sig = _base64url_decode(encoded_signature)
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None

        payload_bytes = _base64url_decode(encoded_payload)
        payload = json.loads(payload_bytes.decode("utf-8"))

        # Check expiration
        now = int(time.time())
        if payload.get("exp", 0) < now:
            return None
        return payload
    except Exception:
        return None

# ---------------------------------------------------------------------------
# SEED ACCOUNTS & INITIALIZATION
# ---------------------------------------------------------------------------
SEED_COLLEGE = {
    "id": 1,
    "code": "ABC_ENGG",
    "name": "ABC College of Engineering & Technology",
    "address": "Campus Vidyanagari, Pune, India"
}

SEED_USERS = [
    {
        "id": "usr-superadmin-01",
        "email": "superadmin@clashfree.edu",
        "full_name": "Platform Administrator",
        "designation": "System Architect",
        "college_id": 1,
        "account_status": "ACTIVE",
        "roles": [
            {
                "role": ROLE_SUPER_ADMIN,
                "college_id": None,
                "department_code": None,
                "assigned_by": "SYSTEM"
            }
        ]
    },
    {
        "id": "usr-principal-01",
        "email": "principal@clashfree.edu",
        "full_name": "Dr. Rameshwar Patil",
        "designation": "Principal & Campus Director",
        "college_id": 1,
        "account_status": "ACTIVE",
        "roles": [
            {
                "role": ROLE_INSTITUTIONAL_VIEWER,
                "college_id": 1,
                "department_code": None,
                "assigned_by": "usr-superadmin-01"
            }
        ]
    },
    {
        "id": "usr-dean-01",
        "email": "dean@clashfree.edu",
        "full_name": "Dr. Shalini Deshmukh",
        "designation": "Dean of Academic Affairs",
        "college_id": 1,
        "account_status": "ACTIVE",
        "roles": [
            {
                "role": ROLE_INSTITUTIONAL_VIEWER,
                "college_id": 1,
                "department_code": None,
                "assigned_by": "usr-superadmin-01"
            }
        ]
    },
    {
        "id": "usr-hod-cse-01",
        "email": "hod.cse@clashfree.edu",
        "full_name": "Dr. Amit R. Sharma",
        "designation": "Professor & HOD CSE",
        "college_id": 1,
        "account_status": "ACTIVE",
        "roles": [
            {
                "role": ROLE_HOD,
                "college_id": 1,
                "department_code": "CSE",
                "assigned_by": "usr-superadmin-01"
            }
        ]
    },
    {
        "id": "usr-hod-etc-01",
        "email": "hod.etc@clashfree.edu",
        "full_name": "Dr. Sunita Kulkarni",
        "designation": "Professor & HOD E&TC",
        "college_id": 1,
        "account_status": "ACTIVE",
        "roles": [
            {
                "role": ROLE_HOD,
                "college_id": 1,
                "department_code": "E&TC",
                "assigned_by": "usr-superadmin-01"
            }
        ]
    },
    {
        "id": "usr-creator-cse-01",
        "email": "creator.cse@clashfree.edu",
        "full_name": "Mr. Vishal H. Pundikar",
        "designation": "Assistant Professor & Timetable Coordinator",
        "college_id": 1,
        "account_status": "ACTIVE",
        "roles": [
            {
                "role": ROLE_TIMETABLE_CREATOR,
                "college_id": 1,
                "department_code": "CSE",
                "assigned_by": "usr-hod-cse-01"
            },
            {
                "role": ROLE_FACULTY,
                "college_id": 1,
                "department_code": "CSE",
                "assigned_by": "usr-hod-cse-01"
            }
        ]
    },
    {
        "id": "usr-faculty-cse-01",
        "email": "faculty.cse@clashfree.edu",
        "full_name": "Mrs. Sneha P. Desai",
        "designation": "Assistant Professor",
        "college_id": 1,
        "account_status": "ACTIVE",
        "roles": [
            {
                "role": ROLE_FACULTY,
                "college_id": 1,
                "department_code": "CSE",
                "assigned_by": "usr-hod-cse-01"
            }
        ]
    }
]

# Standard seeded default password for dev/test accounts
DEFAULT_SEED_PASSWORD = "ClashFree@2026"
DEFAULT_PASSWORD_HASH = hash_password(DEFAULT_SEED_PASSWORD)

def ensure_seed_auth_data(store: dict) -> None:
    """Ensure colleges, user_profiles, user_roles, audit_logs exist in store."""
    if "colleges" not in store or not store["colleges"]:
        store["colleges"] = [dict(SEED_COLLEGE)]

    if "user_profiles" not in store:
        store["user_profiles"] = []
    if "user_roles" not in store:
        store["user_roles"] = []
    if "audit_logs" not in store:
        store["audit_logs"] = []

    existing_emails = {u.get("email"): u for u in store["user_profiles"]}
    next_role_id = max([r.get("id", 0) for r in store["user_roles"]] or [0]) + 1

    for seed_u in SEED_USERS:
        email = seed_u["email"]
        if email not in existing_emails:
            profile = {
                "id": seed_u["id"],
                "email": email,
                "full_name": seed_u["full_name"],
                "designation": seed_u["designation"],
                "college_id": seed_u["college_id"],
                "account_status": seed_u["account_status"],
                "password_hash": DEFAULT_PASSWORD_HASH,
                "created_at": datetime.now().isoformat()
            }
            store["user_profiles"].append(profile)
            for r in seed_u.get("roles", []):
                role_entry = {
                    "id": next_role_id,
                    "user_id": seed_u["id"],
                    "role": r["role"],
                    "college_id": r.get("college_id"),
                    "department_code": r.get("department_code"),
                    "assigned_by": r.get("assigned_by", "SYSTEM"),
                    "created_at": datetime.now().isoformat()
                }
                store["user_roles"].append(role_entry)
                next_role_id += 1

# ---------------------------------------------------------------------------
# USER LOOKUP & AUTHENTICATION
# ---------------------------------------------------------------------------
def authenticate_user(email: str, password: str, store: dict) -> tuple[dict | None, str | None]:
    """
    Validate credentials against user store (or Supabase Auth if online).
    Returns (user_profile_with_roles, error_message).
    """
    if not email or not password:
        return None, "Email and password are required"
    clean_email = email.strip().lower()

    # First check memory / local store
    profiles = store.get("user_profiles", [])
    user = next((u for u in profiles if u.get("email", "").strip().lower() == clean_email), None)

    if not user:
        return None, "Invalid email or password"

    if user.get("account_status") != "ACTIVE":
        return None, "This account is inactive or suspended. Please contact your administrator."

    # Verify password hash
    stored_hash = user.get("password_hash")
    if not stored_hash or not verify_password(password, stored_hash):
        return None, "Invalid email or password"

    # Assemble roles and scopes
    all_roles = store.get("user_roles", [])
    user_roles = [r for r in all_roles if str(r.get("user_id")) == str(user["id"])]

    user_data = {
        "id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "designation": user.get("designation", "Faculty"),
        "college_id": user.get("college_id", 1),
        "account_status": user.get("account_status", "ACTIVE"),
        "roles": user_roles
    }
    return user_data, None


def get_user_session_payload(user: dict, active_department: str = None) -> dict:
    """Format user data into standard session representation."""
    roles = user.get("roles", [])
    role_names = [r.get("role") for r in roles]

    # Determine highest priority role
    primary_role = ROLE_FACULTY
    for r in [ROLE_SUPER_ADMIN, ROLE_INSTITUTIONAL_VIEWER, ROLE_HOD, ROLE_TIMETABLE_CREATOR, ROLE_FACULTY]:
        if r in role_names:
            primary_role = r
            break

    # Determine accessible departments
    accessible_depts = []
    if primary_role == ROLE_SUPER_ADMIN:
        accessible_depts = ["ALL"]
    elif primary_role == ROLE_INSTITUTIONAL_VIEWER:
        accessible_depts = ["ALL_COLLEGE"]
    else:
        dept_set = set()
        for r in roles:
            if r.get("department_code"):
                dept_set.add(r.get("department_code"))
        accessible_depts = sorted(list(dept_set))

    default_dept = active_department
    if not default_dept and accessible_depts and accessible_depts[0] not in ("ALL", "ALL_COLLEGE"):
        default_dept = accessible_depts[0]
    elif not default_dept:
        default_dept = "CSE"

    return {
        "id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "designation": user.get("designation", "Faculty"),
        "college_id": user.get("college_id", 1),
        "primary_role": primary_role,
        "roles": roles,
        "accessible_departments": accessible_depts,
        "active_department": default_dept
    }

# ---------------------------------------------------------------------------
# PERMISSION & SCOPE CHECKERS
# ---------------------------------------------------------------------------
def check_scope_permission(
    user_session: dict,
    department: str = None,
    action: str = "read"
) -> tuple[bool, str | None]:
    """
    Enforce strict role and scope access rules.
    action: 'read', 'write', 'generate', 'restore', 'manage_creators', 'manage_users'
    """
    if not user_session:
        return False, "Authentication required"

    primary_role = user_session.get("primary_role")
    roles = user_session.get("roles", [])
    dept = (department or user_session.get("active_department") or "").strip().upper()

    # SUPER_ADMIN: platform-wide access to all actions and scopes
    if primary_role == ROLE_SUPER_ADMIN:
        return True, None

    # INSTITUTIONAL_VIEWER: college-scoped read-only
    if primary_role == ROLE_INSTITUTIONAL_VIEWER:
        if action in ("read", "view"):
            return True, None
        return False, f"Institutional Viewers have strictly read-only access. Cannot perform action: '{action}'."

    # HOD: full control for their assigned department
    hod_depts = [r.get("department_code") for r in roles if r.get("role") == ROLE_HOD]
    if primary_role == ROLE_HOD or any(r.get("role") == ROLE_HOD for r in roles):
        if not dept or dept in hod_depts:
            if action == "manage_users":
                return False, "Only Super Admin can manage platform users."
            return True, None
        return False, f"HOD permission denied: not authorized for department '{dept}'."

    # TIMETABLE_CREATOR: can manage scheduling inputs and generate in assigned department
    creator_depts = [r.get("department_code") for r in roles if r.get("role") == ROLE_TIMETABLE_CREATOR]
    if primary_role == ROLE_TIMETABLE_CREATOR or any(r.get("role") == ROLE_TIMETABLE_CREATOR for r in roles):
        if not dept or dept in creator_depts:
            if action in ("restore", "manage_creators", "manage_users"):
                return False, f"Timetable Creators cannot perform '{action}'. Restricted to HOD / Admin."
            return True, None
        return False, f"Timetable Creator permission denied: not authorized for department '{dept}'."

    # FACULTY: read-only access to their department
    faculty_depts = [r.get("department_code") for r in roles if r.get("role") == ROLE_FACULTY]
    if not dept or dept in faculty_depts or not faculty_depts:
        if action in ("read", "view"):
            return True, None
        return False, f"Faculty role is read-only. Cannot perform write action: '{action}'."

    return False, f"Access denied for department '{dept}'."

# ---------------------------------------------------------------------------
# AUDIT LOGGING
# ---------------------------------------------------------------------------
def record_audit_log(
    store: dict,
    actor_id: str,
    actor_email: str,
    actor_role: str,
    action: str,
    target_type: str = None,
    target_id: str = None,
    details: dict | str = None,
    college_id: int = 1,
    department_code: str = None
) -> dict:
    """Record a persistent audit log entry."""
    logs = store.setdefault("audit_logs", [])
    next_id = max([l.get("id", 0) for l in logs] or [0]) + 1
    entry = {
        "id": next_id,
        "actor_id": actor_id,
        "actor_email": actor_email,
        "actor_role": actor_role,
        "action": action,
        "target_type": target_type or "GENERAL",
        "target_id": str(target_id) if target_id else None,
        "details": details if isinstance(details, (dict, list, str)) else str(details),
        "college_id": college_id,
        "department_code": department_code,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "created_at": datetime.now().isoformat()
    }
    logs.insert(0, entry)  # newest first
    # Keep last 1000 logs in local storage
    if len(logs) > 1000:
        store["audit_logs"] = logs[:1000]
    return entry
