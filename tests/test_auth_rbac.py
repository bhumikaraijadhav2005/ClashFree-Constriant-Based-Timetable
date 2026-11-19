"""Comprehensive tests for ClashFree Authentication & Role-Based Access Control (RBAC)."""

import os
import sys
import json
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

import app
import db
import auth

# ---------------------------------------------------------------------------
# FIXTURES & HELPERS
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def setup_strict_tests(monkeypatch):
    monkeypatch.setenv("STRICT_AUTH_TESTS", "1")
    # Ensure memory store has default users seeded
    auth.ensure_seed_auth_data(db._memory_store)

def get_auth_token(email, password="ClashFree@2026", department=None):
    user_data, err = auth.authenticate_user(email, password, db._memory_store)
    assert err is None, f"Auth failed for {email}: {err}"
    session_data = auth.get_user_session_payload(user_data, active_department=department)
    return auth.create_auth_token({
        "sub": user_data["id"],
        "email": user_data["email"],
        "role": session_data["primary_role"],
        "college_id": session_data["college_id"],
        "department_code": session_data["active_department"]
    })

# ---------------------------------------------------------------------------
# 1. CRYPTOGRAPHIC PRIMITIVES & TOKEN SECURITY
# ---------------------------------------------------------------------------
def test_password_hashing_and_verification():
    raw = "SecurePassword@123"
    hashed = auth.hash_password(raw)
    assert hashed.startswith("pbkdf2:sha256:100000$")
    assert auth.verify_password(raw, hashed) is True
    assert auth.verify_password("WrongPassword", hashed) is False
    assert auth.verify_password("", hashed) is False
    assert auth.verify_password(raw, "") is False

def test_auth_token_signature_and_expiration():
    payload = {"sub": "usr-test-1", "email": "test@clashfree.edu"}
    token = auth.create_auth_token(payload, expires_in=3600)
    verified = auth.verify_auth_token(token)
    assert verified is not None
    assert verified["sub"] == "usr-test-1"
    assert verified["email"] == "test@clashfree.edu"

    # Tampered token
    tampered = token[:-4] + "abcd"
    assert auth.verify_auth_token(tampered) is None

    # Expired token
    expired_token = auth.create_auth_token(payload, expires_in=-10)
    assert auth.verify_auth_token(expired_token) is None

# ---------------------------------------------------------------------------
# 2. LOGIN & AUTHENTICATION ENDPOINTS
# ---------------------------------------------------------------------------
def test_login_valid_credentials():
    client = app.app.test_client()
    res = client.post("/api/auth/login", json={
        "email": "hod.cse@clashfree.edu",
        "password": "ClashFree@2026"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "token" in data
    assert data["user"]["email"] == "hod.cse@clashfree.edu"
    assert data["user"]["primary_role"] == "HOD"
    assert data["user"]["active_department"] == "CSE"

def test_login_invalid_password():
    client = app.app.test_client()
    res = client.post("/api/auth/login", json={
        "email": "hod.cse@clashfree.edu",
        "password": "WrongPassword@999"
    })
    assert res.status_code == 401
    assert res.get_json()["success"] is False

def test_login_unknown_email():
    client = app.app.test_client()
    res = client.post("/api/auth/login", json={
        "email": "nonexistent@clashfree.edu",
        "password": "ClashFree@2026"
    })
    assert res.status_code == 401
    assert res.get_json()["success"] is False

def test_login_empty_fields():
    client = app.app.test_client()
    res = client.post("/api/auth/login", json={"email": "", "password": ""})
    assert res.status_code == 401

def test_session_restoration_with_auth_me():
    client = app.app.test_client()
    token = get_auth_token("principal@clashfree.edu")
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["user"]["primary_role"] == "INSTITUTIONAL_VIEWER"
    assert data["user"]["designation"] == "Principal & Campus Director"

def test_forgot_password_flow():
    client = app.app.test_client()
    res = client.post("/api/auth/forgot-password", json={"email": "hod.cse@clashfree.edu"})
    assert res.status_code == 200
    assert res.get_json()["success"] is True
    assert "dispatched" in res.get_json()["message"]

# ---------------------------------------------------------------------------
# 3. ROLE SCOPE & PERMISSIONS MATRIX
# ---------------------------------------------------------------------------
def test_super_admin_has_platform_wide_access():
    user, _ = auth.authenticate_user("superadmin@clashfree.edu", "ClashFree@2026", db._memory_store)
    session = auth.get_user_session_payload(user)
    assert auth.check_scope_permission(session, "CSE", action="generate")[0] is True
    assert auth.check_scope_permission(session, "E&TC", action="generate")[0] is True
    assert auth.check_scope_permission(session, "CIVIL", action="restore")[0] is True
    assert auth.check_scope_permission(session, "ANY", action="manage_users")[0] is True

def test_institutional_viewer_is_strictly_read_only():
    user, _ = auth.authenticate_user("principal@clashfree.edu", "ClashFree@2026", db._memory_store)
    session = auth.get_user_session_payload(user)
    # Can view all departments in college
    assert auth.check_scope_permission(session, "CSE", action="read")[0] is True
    assert auth.check_scope_permission(session, "E&TC", action="read")[0] is True
    # Cannot write, generate, or restore
    assert auth.check_scope_permission(session, "CSE", action="write")[0] is False
    assert auth.check_scope_permission(session, "CSE", action="generate")[0] is False
    assert auth.check_scope_permission(session, "CSE", action="restore")[0] is False

def test_hod_is_isolated_to_assigned_department():
    user, _ = auth.authenticate_user("hod.cse@clashfree.edu", "ClashFree@2026", db._memory_store)
    session = auth.get_user_session_payload(user)
    # Full control in CSE
    assert auth.check_scope_permission(session, "CSE", action="read")[0] is True
    assert auth.check_scope_permission(session, "CSE", action="write")[0] is True
    assert auth.check_scope_permission(session, "CSE", action="generate")[0] is True
    assert auth.check_scope_permission(session, "CSE", action="restore")[0] is True
    assert auth.check_scope_permission(session, "CSE", action="manage_creators")[0] is True

    # Blocked from other departments
    assert auth.check_scope_permission(session, "E&TC", action="write")[0] is False
    assert auth.check_scope_permission(session, "E&TC", action="generate")[0] is False
    assert auth.check_scope_permission(session, "E&TC", action="manage_creators")[0] is False

def test_timetable_creator_permissions():
    user, _ = auth.authenticate_user("creator.cse@clashfree.edu", "ClashFree@2026", db._memory_store)
    session = auth.get_user_session_payload(user)
    # Can edit scheduling data and generate for CSE
    assert auth.check_scope_permission(session, "CSE", action="write")[0] is True
    assert auth.check_scope_permission(session, "CSE", action="generate")[0] is True
    # Cannot restore versions, cannot manage users/creators
    assert auth.check_scope_permission(session, "CSE", action="restore")[0] is False
    assert auth.check_scope_permission(session, "CSE", action="manage_creators")[0] is False
    # Cannot access other departments
    assert auth.check_scope_permission(session, "E&TC", action="generate")[0] is False

def test_faculty_is_read_only_department_scoped():
    user, _ = auth.authenticate_user("faculty.cse@clashfree.edu", "ClashFree@2026", db._memory_store)
    session = auth.get_user_session_payload(user)
    # Can view department timetables
    assert auth.check_scope_permission(session, "CSE", action="read")[0] is True
    # Cannot write, import, generate or restore
    assert auth.check_scope_permission(session, "CSE", action="write")[0] is False
    assert auth.check_scope_permission(session, "CSE", action="generate")[0] is False
    assert auth.check_scope_permission(session, "CSE", action="restore")[0] is False

# ---------------------------------------------------------------------------
# 4. API ENFORCEMENT & UNAUTHORIZED MUTATION BLOCKING
# ---------------------------------------------------------------------------
def test_faculty_cannot_generate_timetable_via_api():
    client = app.app.test_client()
    token = get_auth_token("faculty.cse@clashfree.edu")
    res = client.post("/api/generate-timetable", json={"department": "CSE"}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403
    assert res.get_json()["success"] is False

def test_institutional_viewer_cannot_restore_version_via_api():
    client = app.app.test_client()
    token = get_auth_token("principal@clashfree.edu")
    res = client.post("/api/timetable-versions/1/restore", json={"department": "CSE"}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403
    assert res.get_json()["success"] is False

def test_creator_cannot_restore_version_via_api():
    client = app.app.test_client()
    token = get_auth_token("creator.cse@clashfree.edu")
    res = client.post("/api/timetable-versions/1/restore", json={"department": "CSE"}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403
    assert "cannot perform 'restore'" in res.get_json()["error"]

def test_hod_cross_department_mutation_is_blocked():
    client = app.app.test_client()
    # HOD CSE trying to generate for E&TC
    token = get_auth_token("hod.cse@clashfree.edu")
    res = client.post("/api/generate-timetable", json={"department": "E&TC"}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403

# ---------------------------------------------------------------------------
# 5. HOD MANAGE TIMETABLE CREATOR DELEGATION
# ---------------------------------------------------------------------------
def test_hod_can_assign_and_revoke_creator_role():
    client = app.app.test_client()
    hod_token = get_auth_token("hod.cse@clashfree.edu")

    # 1. HOD lists eligible faculty in CSE
    res_list = client.get("/api/auth/eligible-faculty?department=CSE", headers={"Authorization": f"Bearer {hod_token}"})
    assert res_list.status_code == 200
    assert len(res_list.get_json()["faculty"]) > 0

    # 2. Assign Timetable Creator access to faculty.cse
    target_id = "usr-faculty-cse-01"
    res_assign = client.post("/api/auth/creators", json={
        "target_user_id": target_id,
        "department": "CSE"
    }, headers={"Authorization": f"Bearer {hod_token}"})
    assert res_assign.status_code == 200
    assert res_assign.get_json()["success"] is True

    # 3. Verify target is now in creators list
    res_creators = client.get("/api/auth/creators?department=CSE", headers={"Authorization": f"Bearer {hod_token}"})
    creators = res_creators.get_json()["creators"]
    assert any(c["user_id"] == target_id for c in creators)

    # 4. Revoke Timetable Creator access
    res_revoke = client.delete("/api/auth/creators", json={
        "target_user_id": target_id,
        "department": "CSE"
    }, headers={"Authorization": f"Bearer {hod_token}"})
    assert res_revoke.status_code == 200
    assert res_revoke.get_json()["success"] is True

def test_faculty_cannot_assign_themselves_or_others_as_creator():
    client = app.app.test_client()
    faculty_token = get_auth_token("faculty.cse@clashfree.edu")
    res = client.post("/api/auth/creators", json={
        "target_user_id": "usr-faculty-cse-01",
        "department": "CSE"
    }, headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 403

def test_creator_cannot_assign_roles():
    client = app.app.test_client()
    creator_token = get_auth_token("creator.cse@clashfree.edu")
    res = client.post("/api/auth/creators", json={
        "target_user_id": "usr-faculty-cse-01",
        "department": "CSE"
    }, headers={"Authorization": f"Bearer {creator_token}"})
    assert res.status_code == 403

# ---------------------------------------------------------------------------
# 6. AUDIT LOGGING INTEGRATION
# ---------------------------------------------------------------------------
def test_audit_logs_recorded_and_retrieved():
    client = app.app.test_client()
    admin_token = get_auth_token("superadmin@clashfree.edu")

    # Super admin checks audit logs
    res = client.get("/api/audit-logs", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    logs = res.get_json()["logs"]
    assert isinstance(logs, list)
    assert len(logs) > 0

# ---------------------------------------------------------------------------
# 7. SUPER ADMIN USER ACCESS MANAGEMENT & CREDENTIAL PROVISIONING
# ---------------------------------------------------------------------------
def test_super_admin_creates_user_and_user_can_login():
    import uuid
    client = app.app.test_client()
    admin_token = get_auth_token("superadmin@clashfree.edu")
    test_email = f"dr.kulkarni.{uuid.uuid4().hex[:6]}@college.edu"

    # 1. Super Admin creates new faculty user with custom password
    new_user_payload = {
        "email": test_email,
        "password": "InitialPass@2026",
        "full_name": "Dr. Pradeep Kulkarni",
        "designation": "Associate Professor",
        "role": "FACULTY",
        "department": "CSE"
    }
    res_create = client.post("/api/auth/users", json=new_user_payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert res_create.status_code == 201
    created_user = res_create.get_json()["user"]
    assert created_user["email"] == test_email

    # 2. Newly created faculty logs in immediately with provided password
    res_login = client.post("/api/auth/login", json={
        "email": test_email,
        "password": "InitialPass@2026"
    })
    assert res_login.status_code == 200
    login_data = res_login.get_json()
    assert login_data["success"] is True
    assert login_data["user"]["primary_role"] == "FACULTY"
    assert login_data["user"]["active_department"] == "CSE"

    # 3. Super Admin resets the password for this user
    user_id = created_user["id"]
    res_reset = client.post(f"/api/auth/users/{user_id}/reset-password", json={
        "password": "UpdatedPassword@2027"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert res_reset.status_code == 200

    # 4. Old password fails
    res_old_login = client.post("/api/auth/login", json={
        "email": test_email,
        "password": "InitialPass@2026"
    })
    assert res_old_login.status_code == 401

    # 5. New password succeeds
    res_new_login = client.post("/api/auth/login", json={
        "email": test_email,
        "password": "UpdatedPassword@2027"
    })
    assert res_new_login.status_code == 200

    # 6. Clean up created test user
    client.delete(f"/api/auth/users/{user_id}", headers={"Authorization": f"Bearer {admin_token}"})

def test_non_super_admin_cannot_manage_users():
    client = app.app.test_client()
    hod_token = get_auth_token("hod.cse@clashfree.edu")

    # HOD attempts to create user -> must be 403 Forbidden
    res = client.post("/api/auth/users", json={
        "email": "unauthorized.faculty@college.edu",
        "password": "Pass@123",
        "full_name": "Unauthorized Faculty",
        "role": "FACULTY",
        "department": "CSE"
    }, headers={"Authorization": f"Bearer {hod_token}"})
    assert res.status_code == 403
    assert "Super Admin" in res.get_json()["error"]


# ---------------------------------------------------------------------------
# 8. SELF-SERVICE PASSWORD RESET FLOW (OFFICIAL EMAIL & TOKEN VERIFICATION)
# ---------------------------------------------------------------------------
def test_forgot_password_and_token_reset_flow():
    client = app.app.test_client()
    email = "faculty.cse@clashfree.edu"
    initial_pass = "ClashFree@2026"
    new_reset_pass = "NewResetPassword@2026"

    # 1. Request password reset for official email
    res_forgot = client.post("/api/auth/forgot-password", json={"email": email})
    assert res_forgot.status_code == 200
    assert res_forgot.get_json()["success"] is True

    # 2. Verify token generation and verification
    user = app.db.get_user_by_email(email)
    assert user is not None
    token = app.auth.create_password_reset_token(user["id"], user["email"], expires_in=900)
    payload = app.auth.verify_password_reset_token(token)
    assert payload is not None
    assert payload["sub"] == user["id"]
    assert payload["email"] == email

    # 3. Test invalid token rejection
    res_bad = client.post("/api/auth/reset-password", json={"token": "invalid.fake.token", "password": new_reset_pass})
    assert res_bad.status_code == 400
    assert "invalid or has expired" in res_bad.get_json()["error"]

    # 4. Test short password rejection
    res_short = client.post("/api/auth/reset-password", json={"token": token, "password": "123"})
    assert res_short.status_code == 400
    assert "at least 6 characters" in res_short.get_json()["error"]

    # 5. Reset password with valid token
    res_reset = client.post("/api/auth/reset-password", json={"token": token, "password": new_reset_pass})
    assert res_reset.status_code == 200
    assert res_reset.get_json()["success"] is True

    # 6. Verify login with newly set password
    res_new_login = client.post("/api/auth/login", json={"email": email, "password": new_reset_pass})
    assert res_new_login.status_code == 200
    assert res_new_login.get_json()["success"] is True

    # 7. Old password no longer works
    res_old_login = client.post("/api/auth/login", json={"email": email, "password": initial_pass})
    assert res_old_login.status_code == 401

    # 8. Restore initial password so other tests are not affected
    app.db.set_user_password(user["id"], initial_pass)

