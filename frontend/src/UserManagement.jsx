// frontend/src/UserManagement.jsx
// Super Admin User & Access Control Management
// Enables Super Admin to add faculty/dean/HOD accounts, assign role & department scope,
// set initial passwords, and copy/dispatch credentials to users.

import React, { useState, useEffect } from "react";
import * as api from "./api";

const ROLES = [
  { value: "SUPER_ADMIN", label: "Super Admin (Platform Owner)", scope: "global", badgeClass: "role-superadmin" },
  { value: "INSTITUTIONAL_VIEWER", label: "Institutional Viewer (Dean / Principal / Director)", scope: "college", badgeClass: "role-viewer" },
  { value: "HOD", label: "HOD (Head of Department)", scope: "dept", badgeClass: "role-hod" },
  { value: "TIMETABLE_CREATOR", label: "Timetable Creator (Authorized Faculty Scheduler)", scope: "dept", badgeClass: "role-creator" },
  { value: "FACULTY", label: "Faculty (Department Timetable Viewer)", scope: "dept", badgeClass: "role-faculty" },
];

function generateSecurePassword() {
  const chars = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ23456789!@#$%&*";
  let pass = "";
  for (let i = 0; i < 10; i++) {
    pass += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return `Clash#${pass}`;
}

export default function UserManagement({ departments, currentUser, onNotify }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [roleFilter, setRoleFilter] = useState("ALL");

  // Create Form State
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [designation, setDesignation] = useState("Assistant Professor");
  const [selectedRole, setSelectedRole] = useState("FACULTY");
  const [selectedDept, setSelectedDept] = useState("CSE");
  const [password, setPassword] = useState(generateSecurePassword());
  const [showPassword, setShowPassword] = useState(false);
  const [creating, setCreating] = useState(false);

  // Recent Provisioned Credentials Banner
  const [recentProvision, setRecentProvision] = useState(null);
  const [copied, setCopied] = useState(false);

  // Modals
  const [resetModalUser, setResetModalUser] = useState(null);
  const [resetPasswordVal, setResetPasswordVal] = useState("");
  const [resetting, setResetting] = useState(false);

  const [editModalUser, setEditModalUser] = useState(null);
  const [editFullName, setEditFullName] = useState("");
  const [editDesignation, setEditDesignation] = useState("");
  const [editRole, setEditRole] = useState("FACULTY");
  const [editDept, setEditDept] = useState("CSE");
  const [editStatus, setEditStatus] = useState("ACTIVE");
  const [savingEdit, setSavingEdit] = useState(false);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const res = await api.fetchUsers();
      if (res && res.users) {
        setUsers(res.users);
      }
    } catch (err) {
      if (onNotify) onNotify("Failed to load user directory", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    if (!email.trim() || !fullName.trim() || !password.trim()) {
      if (onNotify) onNotify("Email, Full Name, and Password are required.", "error");
      return;
    }

    const roleObj = ROLES.find((r) => r.value === selectedRole);
    const requiresDept = roleObj?.scope === "dept";
    if (requiresDept && !selectedDept) {
      if (onNotify) onNotify("Please select a department for this role.", "error");
      return;
    }

    setCreating(true);
    try {
      const payload = {
        email: email.trim().toLowerCase(),
        full_name: fullName.trim(),
        designation: designation.trim(),
        role: selectedRole,
        department: requiresDept ? selectedDept : null,
        password: password.trim(),
      };

      const res = await api.createUser(payload);
      if (res.success) {
        if (onNotify) onNotify(`User account created for ${fullName}!`, "success");
        setRecentProvision({
          email: payload.email,
          password: payload.password,
          fullName: payload.full_name,
          role: payload.role,
          department: requiresDept ? selectedDept : "College-Wide / All",
          designation: payload.designation,
        });

        // Reset inputs
        setEmail("");
        setFullName("");
        setDesignation("Assistant Professor");
        setPassword(generateSecurePassword());
        loadUsers();
      } else {
        if (onNotify) onNotify(res.error || "Failed to create user", "error");
      }
    } catch (err) {
      if (onNotify) onNotify("Network error while creating user", "error");
    } finally {
      setCreating(false);
    }
  };

  const copyCredentials = (cred) => {
    const text = `ClashFree Timetable Portal - User Credentials
------------------------------------------------
Full Name: ${cred.fullName || cred.full_name || ""}
Email: ${cred.email}
Password: ${cred.password}
Role: ${cred.role}
Scope: ${cred.department || "All Departments"}
Login URL: ${window.location.origin}`;

    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 3000);
      if (onNotify) onNotify("Credentials copied to clipboard!", "success");
    });
  };

  const handleOpenResetModal = (user) => {
    setResetModalUser(user);
    setResetPasswordVal(generateSecurePassword());
  };

  const handleConfirmResetPassword = async () => {
    if (!resetModalUser || !resetPasswordVal.trim()) return;
    setResetting(true);
    try {
      const res = await api.adminResetPassword(resetModalUser.id, resetPasswordVal.trim());
      if (res.success) {
        if (onNotify) onNotify(`Password reset for ${resetModalUser.full_name}`, "success");
        setRecentProvision({
          email: resetModalUser.email,
          password: resetPasswordVal.trim(),
          fullName: resetModalUser.full_name,
          role: resetModalUser.primary_role,
          department: resetModalUser.primary_department || "College-Wide",
          designation: resetModalUser.designation,
        });
        setResetModalUser(null);
      } else {
        if (onNotify) onNotify(res.error || "Failed to reset password", "error");
      }
    } catch {
      if (onNotify) onNotify("Error resetting password", "error");
    } finally {
      setResetting(false);
    }
  };

  const handleOpenEditModal = (user) => {
    setEditModalUser(user);
    setEditFullName(user.full_name || "");
    setEditDesignation(user.designation || "");
    setEditRole(user.primary_role || "FACULTY");
    setEditDept(user.primary_department || (departments[0]?.code || "CSE"));
    setEditStatus(user.account_status || "ACTIVE");
  };

  const handleSaveEdit = async () => {
    if (!editModalUser) return;
    setSavingEdit(true);
    try {
      const roleObj = ROLES.find((r) => r.value === editRole);
      const requiresDept = roleObj?.scope === "dept";
      const payload = {
        full_name: editFullName.trim(),
        designation: editDesignation.trim(),
        role: editRole,
        department: requiresDept ? editDept : null,
        account_status: editStatus,
      };
      const res = await api.updateUser(editModalUser.id, payload);
      if (res.success) {
        if (onNotify) onNotify("User access updated successfully", "success");
        setEditModalUser(null);
        loadUsers();
      } else {
        if (onNotify) onNotify(res.error || "Failed to update user", "error");
      }
    } catch {
      if (onNotify) onNotify("Error updating user", "error");
    } finally {
      setSavingEdit(false);
    }
  };

  const handleDeleteUser = async (user) => {
    if (String(user.id) === String(currentUser?.id)) {
      if (onNotify) onNotify("You cannot delete your own Super Admin account.", "error");
      return;
    }
    if (!window.confirm(`Are you sure you want to permanently delete account: ${user.full_name} (${user.email})?`)) {
      return;
    }
    try {
      const res = await api.deleteUser(user.id);
      if (res.success) {
        if (onNotify) onNotify(`Account ${user.email} removed`, "success");
        loadUsers();
      } else {
        if (onNotify) onNotify(res.error || "Failed to delete user", "error");
      }
    } catch {
      if (onNotify) onNotify("Error deleting user account", "error");
    }
  };

  // Filtered users
  const filteredUsers = users.filter((u) => {
    const term = searchTerm.toLowerCase();
    const matchesSearch =
      (u.full_name || "").toLowerCase().includes(term) ||
      (u.email || "").toLowerCase().includes(term) ||
      (u.designation || "").toLowerCase().includes(term) ||
      (u.primary_department || "").toLowerCase().includes(term);

    const matchesRole = roleFilter === "ALL" || u.primary_role === roleFilter;
    return matchesSearch && matchesRole;
  });

  const requiresDepartment = ROLES.find((r) => r.value === selectedRole)?.scope === "dept";

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* Page Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
        <div>
          <h2 style={{ margin: 0, fontSize: "1.4rem", fontWeight: 700, color: "#f8fafc" }}>
            🛡️ Super Admin User & Access Control Management
          </h2>
          <p style={{ margin: "4px 0 0", color: "#94a3b8", fontSize: "0.88rem" }}>
            Create faculty, dean, and HOD accounts, assign RBAC access scope, set initial credentials, and dispatch them securely.
          </p>
        </div>
        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          <span style={{ fontSize: "0.85rem", color: "#a855f7", background: "rgba(168, 85, 247, 0.12)", padding: "4px 12px", borderRadius: "16px", border: "1px solid rgba(168, 85, 247, 0.25)" }}>
            Total Users: <strong>{users.length}</strong>
          </span>
        </div>
      </div>

      {/* Recent Provision Banner (if user was created or password reset) */}
      {recentProvision && (
        <div
          style={{
            background: "linear-gradient(135deg, rgba(147, 51, 234, 0.18) 0%, rgba(79, 70, 229, 0.18) 100%)",
            border: "1px solid #9333ea",
            borderRadius: "12px",
            padding: "16px 20px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "16px",
          }}
        >
          <div>
            <div style={{ fontWeight: 700, color: "#e9d5ff", fontSize: "0.95rem", display: "flex", alignItems: "center", gap: "8px" }}>
              <span>✅ Credentials Ready to Share</span>
              <span style={{ fontSize: "0.78rem", background: "#7e22ce", color: "#fff", padding: "2px 8px", borderRadius: "10px" }}>
                {recentProvision.role}
              </span>
            </div>
            <div style={{ marginTop: "6px", fontSize: "0.85rem", color: "#cbd5e1" }}>
              User: <strong>{recentProvision.fullName}</strong> ({recentProvision.email}) | Password:{" "}
              <code style={{ background: "#0f172a", padding: "2px 6px", borderRadius: "4px", color: "#a78bfa" }}>
                {recentProvision.password}
              </code>{" "}
              | Scope: <strong>{recentProvision.department}</strong>
            </div>
          </div>
          <div style={{ display: "flex", gap: "10px" }}>
            <button
              onClick={() => copyCredentials(recentProvision)}
              style={{
                background: copied ? "#10b981" : "#9333ea",
                color: "#fff",
                border: "none",
                borderRadius: "8px",
                padding: "8px 16px",
                fontWeight: 600,
                fontSize: "0.85rem",
                cursor: "pointer",
                transition: "all 0.2s",
                display: "flex",
                alignItems: "center",
                gap: "6px",
              }}
            >
              {copied ? "✓ Copied!" : "📋 Copy Login Credentials"}
            </button>
            <button
              onClick={() => setRecentProvision(null)}
              style={{
                background: "transparent",
                color: "#94a3b8",
                border: "1px solid rgba(148, 163, 184, 0.3)",
                borderRadius: "8px",
                padding: "8px 12px",
                fontSize: "0.85rem",
                cursor: "pointer",
              }}
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Section 1: Add New User Form */}
      <div
        style={{
          background: "#1e1b4b1a",
          border: "1px solid rgba(168, 85, 247, 0.25)",
          borderRadius: "14px",
          padding: "24px",
          boxShadow: "0 4px 20px rgba(0, 0, 0, 0.2)",
        }}
      >
        <h3 style={{ margin: "0 0 8px 0", fontSize: "1.1rem", fontWeight: 700, color: "#e2e8f0" }}>
          ➕ Add New User & Provision Access
        </h3>
        <p style={{ margin: "0 0 20px 0", fontSize: "0.84rem", color: "#94a3b8" }}>
          Enter the person's email (faculty, dean, HOD, coordinator), assign their role and department, and specify their login password.
        </p>

        <form onSubmit={handleCreateUser}>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
              gap: "16px",
              marginBottom: "18px",
            }}
          >
            {/* Email */}
            <div>
              <label style={{ display: "block", fontSize: "0.78rem", fontWeight: 600, color: "#cbd5e1", marginBottom: "6px" }}>
                Email Address *
              </label>
              <input
                type="email"
                placeholder="e.g. dean.sharma@college.edu"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                style={{
                  width: "100%",
                  boxSizing: "border-box",
                  background: "#0f172a",
                  border: "1px solid #334155",
                  borderRadius: "8px",
                  padding: "10px 12px",
                  color: "#f8fafc",
                  fontSize: "0.88rem",
                }}
              />
            </div>

            {/* Full Name */}
            <div>
              <label style={{ display: "block", fontSize: "0.78rem", fontWeight: 600, color: "#cbd5e1", marginBottom: "6px" }}>
                Full Name *
              </label>
              <input
                type="text"
                placeholder="e.g. Dr. Rajesh Sharma"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
                style={{
                  width: "100%",
                  boxSizing: "border-box",
                  background: "#0f172a",
                  border: "1px solid #334155",
                  borderRadius: "8px",
                  padding: "10px 12px",
                  color: "#f8fafc",
                  fontSize: "0.88rem",
                }}
              />
            </div>

            {/* Designation */}
            <div>
              <label style={{ display: "block", fontSize: "0.78rem", fontWeight: 600, color: "#cbd5e1", marginBottom: "6px" }}>
                Designation
              </label>
              <input
                type="text"
                placeholder="e.g. Dean of Academics, Professor & HOD"
                value={designation}
                onChange={(e) => setDesignation(e.target.value)}
                style={{
                  width: "100%",
                  boxSizing: "border-box",
                  background: "#0f172a",
                  border: "1px solid #334155",
                  borderRadius: "8px",
                  padding: "10px 12px",
                  color: "#f8fafc",
                  fontSize: "0.88rem",
                }}
              />
            </div>

            {/* Role Assignment */}
            <div>
              <label style={{ display: "block", fontSize: "0.78rem", fontWeight: 600, color: "#cbd5e1", marginBottom: "6px" }}>
                Assigned Role *
              </label>
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                style={{
                  width: "100%",
                  boxSizing: "border-box",
                  background: "#0f172a",
                  border: "1px solid #334155",
                  borderRadius: "8px",
                  padding: "10px 12px",
                  color: "#f8fafc",
                  fontSize: "0.88rem",
                }}
              >
                {ROLES.map((r) => (
                  <option key={r.value} value={r.value}>
                    {r.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Department Scope */}
            <div>
              <label style={{ display: "block", fontSize: "0.78rem", fontWeight: 600, color: "#cbd5e1", marginBottom: "6px" }}>
                Department Scope {requiresDepartment ? "*" : "(Not Required for Global/College Role)"}
              </label>
              <select
                value={selectedDept}
                onChange={(e) => setSelectedDept(e.target.value)}
                disabled={!requiresDepartment}
                style={{
                  width: "100%",
                  boxSizing: "border-box",
                  background: requiresDepartment ? "#0f172a" : "#1e293b",
                  border: "1px solid #334155",
                  borderRadius: "8px",
                  padding: "10px 12px",
                  color: requiresDepartment ? "#f8fafc" : "#64748b",
                  fontSize: "0.88rem",
                }}
              >
                {!requiresDepartment && <option value="">College-Wide / All Departments</option>}
                {departments.map((d) => (
                  <option key={d.code} value={d.code}>
                    {d.code} - {d.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Initial Password */}
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                <label style={{ fontSize: "0.78rem", fontWeight: 600, color: "#cbd5e1" }}>
                  Set Initial Password *
                </label>
                <button
                  type="button"
                  onClick={() => setPassword(generateSecurePassword())}
                  style={{
                    background: "none",
                    border: "none",
                    color: "#a855f7",
                    fontSize: "0.75rem",
                    fontWeight: 600,
                    cursor: "pointer",
                    padding: 0,
                  }}
                >
                  ⚡ Generate
                </button>
              </div>
              <div style={{ position: "relative" }}>
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="Set initial password"
                  style={{
                    width: "100%",
                    boxSizing: "border-box",
                    background: "#0f172a",
                    border: "1px solid #334155",
                    borderRadius: "8px",
                    padding: "10px 40px 10px 12px",
                    color: "#f8fafc",
                    fontSize: "0.88rem",
                    fontFamily: showPassword ? "inherit" : "monospace",
                  }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: "absolute",
                    right: "10px",
                    top: "50%",
                    transform: "translateY(-50%)",
                    background: "none",
                    border: "none",
                    color: "#94a3b8",
                    fontSize: "0.85rem",
                    cursor: "pointer",
                  }}
                  title={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? "🙈" : "👁️"}
                </button>
              </div>
            </div>
          </div>

          <div style={{ display: "flex", justifyContent: "flex-end" }}>
            <button
              type="submit"
              disabled={creating}
              style={{
                background: "linear-gradient(135deg, #7e22ce 0%, #6366f1 100%)",
                color: "#ffffff",
                border: "none",
                borderRadius: "8px",
                padding: "10px 24px",
                fontWeight: 600,
                fontSize: "0.9rem",
                cursor: creating ? "not-allowed" : "pointer",
                boxShadow: "0 4px 12px rgba(126, 34, 206, 0.35)",
              }}
            >
              {creating ? "Creating Account..." : "✨ Create Account & Assign Scope"}
            </button>
          </div>
        </form>
      </div>

      {/* Section 2: User Directory */}
      <div
        style={{
          background: "#0f172a",
          border: "1px solid #1e293b",
          borderRadius: "14px",
          overflow: "hidden",
        }}
      >
        {/* Filter Bar */}
        <div
          style={{
            padding: "16px 20px",
            borderBottom: "1px solid #1e293b",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "12px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px", flex: 1, minWidth: "240px" }}>
            <span style={{ color: "#64748b" }}>🔍</span>
            <input
              type="text"
              placeholder="Search by name, email, designation, or department..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: "100%",
                background: "transparent",
                border: "none",
                color: "#f8fafc",
                fontSize: "0.88rem",
                outline: "none",
              }}
            />
          </div>

          <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
            <span style={{ fontSize: "0.8rem", color: "#64748b" }}>Filter Role:</span>
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              style={{
                background: "#1e293b",
                border: "1px solid #334155",
                borderRadius: "6px",
                padding: "6px 12px",
                color: "#e2e8f0",
                fontSize: "0.82rem",
              }}
            >
              <option value="ALL">All Roles</option>
              {ROLES.map((r) => (
                <option key={r.value} value={r.value}>
                  {r.value}
                </option>
              ))}
            </select>

            <button
              onClick={loadUsers}
              style={{
                background: "#1e293b",
                border: "1px solid #334155",
                borderRadius: "6px",
                padding: "6px 12px",
                color: "#94a3b8",
                fontSize: "0.82rem",
                cursor: "pointer",
              }}
            >
              🔄 Refresh
            </button>
          </div>
        </div>

        {/* Directory Table */}
        {loading ? (
          <div style={{ padding: "40px", textAlign: "center", color: "#94a3b8" }}>
            <div className="spinner-circle" style={{ margin: "0 auto 12px" }} />
            Loading user access directory...
          </div>
        ) : filteredUsers.length === 0 ? (
          <div style={{ padding: "40px", textAlign: "center", color: "#64748b" }}>
            No user accounts found matching your filter criteria.
          </div>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left", fontSize: "0.88rem" }}>
              <thead>
                <tr style={{ background: "#1e293b", color: "#94a3b8", fontSize: "0.78rem", textTransform: "uppercase" }}>
                  <th style={{ padding: "12px 16px" }}>User</th>
                  <th style={{ padding: "12px 16px" }}>Designation</th>
                  <th style={{ padding: "12px 16px" }}>Role</th>
                  <th style={{ padding: "12px 16px" }}>Scope</th>
                  <th style={{ padding: "12px 16px" }}>Status</th>
                  <th style={{ padding: "12px 16px", textAlign: "right" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map((u, idx) => {
                  const roleObj = ROLES.find((r) => r.value === u.primary_role);
                  const isSelf = String(u.id) === String(currentUser?.id);

                  return (
                    <tr
                      key={u.id || idx}
                      style={{
                        borderBottom: "1px solid #1e293b",
                        background: idx % 2 === 0 ? "transparent" : "rgba(30, 41, 59, 0.4)",
                      }}
                    >
                      <td style={{ padding: "12px 16px" }}>
                        <div style={{ fontWeight: 600, color: "#f8fafc" }}>
                          {u.full_name} {isSelf && <span style={{ fontSize: "0.7rem", color: "#a855f7" }}>(You)</span>}
                        </div>
                        <div style={{ fontSize: "0.78rem", color: "#64748b" }}>{u.email}</div>
                      </td>

                      <td style={{ padding: "12px 16px", color: "#cbd5e1" }}>
                        {u.designation || "—"}
                      </td>

                      <td style={{ padding: "12px 16px" }}>
                        <span className={`user-role-pill ${roleObj?.badgeClass || "role-faculty"}`}>
                          {u.primary_role}
                        </span>
                      </td>

                      <td style={{ padding: "12px 16px", color: "#cbd5e1" }}>
                        {u.primary_department ? (
                          <span style={{ background: "rgba(59, 130, 246, 0.15)", color: "#60a5fa", padding: "2px 8px", borderRadius: "4px", fontSize: "0.78rem" }}>
                            Dept: {u.primary_department}
                          </span>
                        ) : (
                          <span style={{ color: "#94a3b8", fontSize: "0.78rem" }}>College-Wide</span>
                        )}
                      </td>

                      <td style={{ padding: "12px 16px" }}>
                        <span
                          style={{
                            fontSize: "0.72rem",
                            fontWeight: 700,
                            padding: "2px 8px",
                            borderRadius: "10px",
                            background: u.account_status === "ACTIVE" ? "rgba(16, 185, 129, 0.15)" : "rgba(239, 68, 68, 0.15)",
                            color: u.account_status === "ACTIVE" ? "#34d399" : "#f87171",
                          }}
                        >
                          {u.account_status || "ACTIVE"}
                        </span>
                      </td>

                      <td style={{ padding: "12px 16px", textAlign: "right" }}>
                        <div style={{ display: "flex", gap: "8px", justifyContent: "flex-end" }}>
                          <button
                            onClick={() => handleOpenResetModal(u)}
                            title="Reset password and copy new credentials"
                            style={{
                              background: "#334155",
                              color: "#f8fafc",
                              border: "none",
                              borderRadius: "6px",
                              padding: "4px 10px",
                              fontSize: "0.78rem",
                              cursor: "pointer",
                            }}
                          >
                            🔑 Password
                          </button>

                          <button
                            onClick={() => handleOpenEditModal(u)}
                            title="Edit Role & Scope"
                            style={{
                              background: "#1e293b",
                              color: "#93c5fd",
                              border: "1px solid #3b82f6",
                              borderRadius: "6px",
                              padding: "4px 10px",
                              fontSize: "0.78rem",
                              cursor: "pointer",
                            }}
                          >
                            ✏️ Edit
                          </button>

                          {!isSelf && (
                            <button
                              onClick={() => handleDeleteUser(u)}
                              title="Delete Account"
                              style={{
                                background: "#450a0a",
                                color: "#fca5a5",
                                border: "1px solid #7f1d1d",
                                borderRadius: "6px",
                                padding: "4px 10px",
                                fontSize: "0.78rem",
                                cursor: "pointer",
                              }}
                            >
                              🗑️
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Reset Password Modal */}
      {resetModalUser && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0, 0, 0, 0.75)",
            backdropFilter: "blur(4px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 9999,
          }}
        >
          <div
            style={{
              background: "#0f172a",
              border: "1px solid #9333ea",
              borderRadius: "14px",
              padding: "24px",
              width: "100%",
              maxWidth: "460px",
              boxShadow: "0 10px 30px rgba(0, 0, 0, 0.5)",
            }}
          >
            <h3 style={{ margin: "0 0 8px 0", color: "#f8fafc", fontSize: "1.1rem" }}>
              🔑 Reset Password for {resetModalUser.full_name}
            </h3>
            <p style={{ margin: "0 0 16px 0", fontSize: "0.85rem", color: "#94a3b8" }}>
              Enter or generate a new password for <strong>{resetModalUser.email}</strong>. Once set, you can copy the updated credentials to share with them.
            </p>

            <div style={{ marginBottom: "20px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                <label style={{ fontSize: "0.78rem", fontWeight: 600, color: "#cbd5e1" }}>New Password</label>
                <button
                  type="button"
                  onClick={() => setResetPasswordVal(generateSecurePassword())}
                  style={{
                    background: "none",
                    border: "none",
                    color: "#a855f7",
                    fontSize: "0.75rem",
                    cursor: "pointer",
                  }}
                >
                  ⚡ Generate
                </button>
              </div>
              <input
                type="text"
                value={resetPasswordVal}
                onChange={(e) => setResetPasswordVal(e.target.value)}
                style={{
                  width: "100%",
                  boxSizing: "border-box",
                  background: "#1e293b",
                  border: "1px solid #334155",
                  borderRadius: "8px",
                  padding: "10px 12px",
                  color: "#f8fafc",
                  fontSize: "0.9rem",
                  fontFamily: "monospace",
                }}
              />
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px" }}>
              <button
                type="button"
                onClick={() => setResetModalUser(null)}
                style={{
                  background: "#1e293b",
                  color: "#94a3b8",
                  border: "none",
                  borderRadius: "8px",
                  padding: "8px 16px",
                  cursor: "pointer",
                }}
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={resetting || !resetPasswordVal.trim()}
                onClick={handleConfirmResetPassword}
                style={{
                  background: "linear-gradient(135deg, #7e22ce 0%, #6366f1 100%)",
                  color: "#ffffff",
                  border: "none",
                  borderRadius: "8px",
                  padding: "8px 18px",
                  fontWeight: 600,
                  cursor: resetting ? "not-allowed" : "pointer",
                }}
              >
                {resetting ? "Resetting..." : "Save & Generate Credentials"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit User Modal */}
      {editModalUser && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0, 0, 0, 0.75)",
            backdropFilter: "blur(4px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 9999,
          }}
        >
          <div
            style={{
              background: "#0f172a",
              border: "1px solid #3b82f6",
              borderRadius: "14px",
              padding: "24px",
              width: "100%",
              maxWidth: "520px",
              boxShadow: "0 10px 30px rgba(0, 0, 0, 0.5)",
            }}
          >
            <h3 style={{ margin: "0 0 8px 0", color: "#f8fafc", fontSize: "1.1rem" }}>
              ✏️ Edit Access & Role: {editModalUser.email}
            </h3>
            <p style={{ margin: "0 0 16px 0", fontSize: "0.85rem", color: "#94a3b8" }}>
              Update designations, role permissions, department scope, and account active status.
            </p>

            <div style={{ display: "grid", gap: "14px", marginBottom: "20px" }}>
              <div>
                <label style={{ display: "block", fontSize: "0.78rem", fontWeight: 600, color: "#cbd5e1", marginBottom: "6px" }}>
                  Full Name
                </label>
                <input
                  type="text"
                  value={editFullName}
                  onChange={(e) => setEditFullName(e.target.value)}
                  style={{
                    width: "100%",
                    boxSizing: "border-box",
                    background: "#1e293b",
                    border: "1px solid #334155",
                    borderRadius: "8px",
                    padding: "8px 12px",
                    color: "#f8fafc",
                    fontSize: "0.88rem",
                  }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "0.78rem", fontWeight: 600, color: "#cbd5e1", marginBottom: "6px" }}>
                  Designation
                </label>
                <input
                  type="text"
                  value={editDesignation}
                  onChange={(e) => setEditDesignation(e.target.value)}
                  style={{
                    width: "100%",
                    boxSizing: "border-box",
                    background: "#1e293b",
                    border: "1px solid #334155",
                    borderRadius: "8px",
                    padding: "8px 12px",
                    color: "#f8fafc",
                    fontSize: "0.88rem",
                  }}
                />
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                <div>
                  <label style={{ display: "block", fontSize: "0.78rem", fontWeight: 600, color: "#cbd5e1", marginBottom: "6px" }}>
                    Role
                  </label>
                  <select
                    value={editRole}
                    onChange={(e) => setEditRole(e.target.value)}
                    style={{
                      width: "100%",
                      boxSizing: "border-box",
                      background: "#1e293b",
                      border: "1px solid #334155",
                      borderRadius: "8px",
                      padding: "8px 12px",
                      color: "#f8fafc",
                      fontSize: "0.88rem",
                    }}
                  >
                    {ROLES.map((r) => (
                      <option key={r.value} value={r.value}>
                        {r.value}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label style={{ display: "block", fontSize: "0.78rem", fontWeight: 600, color: "#cbd5e1", marginBottom: "6px" }}>
                    Department Scope
                  </label>
                  <select
                    value={editDept}
                    onChange={(e) => setEditDept(e.target.value)}
                    disabled={ROLES.find((r) => r.value === editRole)?.scope !== "dept"}
                    style={{
                      width: "100%",
                      boxSizing: "border-box",
                      background: "#1e293b",
                      border: "1px solid #334155",
                      borderRadius: "8px",
                      padding: "8px 12px",
                      color: "#f8fafc",
                      fontSize: "0.88rem",
                    }}
                  >
                    {departments.map((d) => (
                      <option key={d.code} value={d.code}>
                        {d.code}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label style={{ display: "block", fontSize: "0.78rem", fontWeight: 600, color: "#cbd5e1", marginBottom: "6px" }}>
                  Account Status
                </label>
                <select
                  value={editStatus}
                  onChange={(e) => setEditStatus(e.target.value)}
                  style={{
                    width: "100%",
                    boxSizing: "border-box",
                    background: "#1e293b",
                    border: "1px solid #334155",
                    borderRadius: "8px",
                    padding: "8px 12px",
                    color: "#f8fafc",
                    fontSize: "0.88rem",
                  }}
                >
                  <option value="ACTIVE">ACTIVE (Can log in)</option>
                  <option value="SUSPENDED">SUSPENDED (Access blocked)</option>
                </select>
              </div>
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px" }}>
              <button
                type="button"
                onClick={() => setEditModalUser(null)}
                style={{
                  background: "#1e293b",
                  color: "#94a3b8",
                  border: "none",
                  borderRadius: "8px",
                  padding: "8px 16px",
                  cursor: "pointer",
                }}
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={savingEdit}
                onClick={handleSaveEdit}
                style={{
                  background: "#2563eb",
                  color: "#ffffff",
                  border: "none",
                  borderRadius: "8px",
                  padding: "8px 18px",
                  fontWeight: 600,
                  cursor: savingEdit ? "not-allowed" : "pointer",
                }}
              >
                {savingEdit ? "Saving..." : "Save Changes"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
