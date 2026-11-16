// frontend/src/DepartmentAccess.jsx
// HOD Department Access Management: Delegate & Revoke Timetable Creator Role
// View eligible faculty, assign creator privileges, view who assigned and when.

import React, { useState, useEffect } from "react";
import * as api from "./api";

export default function DepartmentAccess({ department, currentUser, onNotify }) {
  const [creators, setCreators] = useState([]);
  const [eligibleFaculty, setEligibleFaculty] = useState([]);
  const [selectedFacultyId, setSelectedFacultyId] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const isHodOrAdmin = currentUser?.primary_role === "HOD" || currentUser?.primary_role === "SUPER_ADMIN";

  useEffect(() => {
    loadAccessData();
  }, [department]);

  const loadAccessData = async () => {
    setLoading(true);
    try {
      const [creatorsRes, facultyRes] = await Promise.all([
        api.fetchDepartmentCreators(department),
        api.fetchEligibleFaculty(department)
      ]);
      setCreators(creatorsRes.creators || []);
      setEligibleFaculty(facultyRes.faculty || []);
      setSelectedFacultyId("");
    } catch (err) {
      if (onNotify) onNotify("Could not load department access list", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleAssign = async (e) => {
    e.preventDefault();
    if (!selectedFacultyId) {
      if (onNotify) onNotify("Please select an eligible faculty member", "error");
      return;
    }
    setSubmitting(true);
    try {
      const res = await api.assignDepartmentCreator(selectedFacultyId, department);
      if (res.success) {
        if (onNotify) onNotify("Timetable Creator access assigned successfully", "success");
        loadAccessData();
      } else {
        if (onNotify) onNotify(res.error || "Failed to assign access", "error");
      }
    } catch {
      if (onNotify) onNotify("Server error while assigning role", "error");
    } finally {
      setSubmitting(false);
    }
  };

  const handleRevoke = async (userId, facultyName) => {
    if (!window.confirm(`Are you sure you want to revoke Timetable Creator access from ${facultyName}?`)) {
      return;
    }
    setSubmitting(true);
    try {
      const res = await api.revokeDepartmentCreator(userId, department);
      if (res.success) {
        if (onNotify) onNotify(`Revoked Timetable Creator access from ${facultyName}`, "success");
        loadAccessData();
      } else {
        if (onNotify) onNotify(res.error || "Failed to revoke access", "error");
      }
    } catch {
      if (onNotify) onNotify("Server error while revoking role", "error");
    } finally {
      setSubmitting(false);
    }
  };

  const creatorUserIds = new Set(creators.map((c) => c.user_id));
  const unassignedFaculty = eligibleFaculty.filter((f) => !creatorUserIds.has(f.id));

  return (
    <div className="card" style={{ marginTop: "16px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px", flexWrap: "wrap", gap: "10px" }}>
        <div>
          <h3 style={{ fontSize: "1.15rem", fontWeight: "700", color: "#1e293b", margin: 0 }}>
            🔑 Department Access & Timetable Creators
          </h3>
          <p style={{ fontSize: "0.85rem", color: "#64748b", margin: "4px 0 0 0" }}>
            Delegate timetable preparation and generation authority to faculty in <strong>{department}</strong>.
          </p>
        </div>
        <button className="btn btn-secondary" onClick={loadAccessData} disabled={loading} style={{ fontSize: "0.82rem" }}>
          🔄 Refresh
        </button>
      </div>

      {/* Assignment Control Box (HOD / Admin only) */}
      {isHodOrAdmin ? (
        <form onSubmit={handleAssign} style={{ background: "#f8fafc", padding: "16px", borderRadius: "10px", border: "1px solid #e2e8f0", marginBottom: "24px" }}>
          <div style={{ fontWeight: "600", fontSize: "0.9rem", color: "#334155", marginBottom: "8px" }}>
            Authorize New Timetable Creator
          </div>
          <div style={{ display: "flex", gap: "12px", alignItems: "center", flexWrap: "wrap" }}>
            <select
              className="select-filter"
              value={selectedFacultyId}
              onChange={(e) => setSelectedFacultyId(e.target.value)}
              style={{ flex: "1", minWidth: "250px", height: "40px" }}
              disabled={submitting || loading || unassignedFaculty.length === 0}
            >
              <option value="">
                {unassignedFaculty.length > 0 ? "-- Select Eligible Faculty Member --" : "-- All faculty are already creators or none found --"}
              </option>
              {unassignedFaculty.map((f) => (
                <option key={f.id} value={f.id}>
                  {f.full_name} ({f.designation || "Faculty"}) — {f.email}
                </option>
              ))}
            </select>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={submitting || !selectedFacultyId}
              style={{ height: "40px", padding: "0 18px", whiteSpace: "nowrap" }}
            >
              {submitting ? "Assigning..." : "+ Authorize Creator"}
            </button>
          </div>
          <div style={{ fontSize: "0.76rem", color: "#64748b", marginTop: "6px" }}>
            Note: Timetable Creators gain permission to edit scheduling inputs, import workbooks, and generate timetables for <strong>{department}</strong>. Only the HOD can restore versions or revoke access.
          </div>
        </form>
      ) : (
        <div style={{ padding: "10px 14px", background: "#f1f5f9", borderRadius: "8px", fontSize: "0.82rem", color: "#475569", marginBottom: "16px" }}>
          ℹ️ Only the HOD or Platform Admin can authorize or revoke Timetable Creators for this department.
        </div>
      )}

      {/* Active Creators Table */}
      <h4 style={{ fontSize: "0.95rem", fontWeight: "700", color: "#334155", marginBottom: "10px" }}>
        Active Timetable Creators ({creators.length})
      </h4>

      {loading ? (
        <div style={{ padding: "24px", textAlign: "center", color: "#64748b" }}>Loading creators list...</div>
      ) : creators.length === 0 ? (
        <div style={{ padding: "24px", textAlign: "center", background: "#faf5ff", borderRadius: "8px", border: "1px dashed #d8b4fe", color: "#6b21a8" }}>
          No additional Timetable Creators currently assigned for {department}. Only the HOD can generate schedules.
        </div>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table className="college-table" style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: "#f8fafc", textAlign: "left" }}>
                <th style={{ padding: "10px 12px", border: "1px solid #e2e8f0" }}>Faculty Name</th>
                <th style={{ padding: "10px 12px", border: "1px solid #e2e8f0" }}>Designation</th>
                <th style={{ padding: "10px 12px", border: "1px solid #e2e8f0" }}>Email</th>
                <th style={{ padding: "10px 12px", border: "1px solid #e2e8f0" }}>Assigned By</th>
                <th style={{ padding: "10px 12px", border: "1px solid #e2e8f0" }}>Date Assigned</th>
                {isHodOrAdmin && <th style={{ padding: "10px 12px", border: "1px solid #e2e8f0", textAlign: "center" }}>Actions</th>}
              </tr>
            </thead>
            <tbody>
              {creators.map((c) => (
                <tr key={c.role_id || c.user_id}>
                  <td style={{ padding: "10px 12px", border: "1px solid #e2e8f0", fontWeight: "600", color: "#1e293b" }}>
                    👨‍🏫 {c.full_name}
                  </td>
                  <td style={{ padding: "10px 12px", border: "1px solid #e2e8f0", color: "#475569" }}>
                    {c.designation || "Faculty"}
                  </td>
                  <td style={{ padding: "10px 12px", border: "1px solid #e2e8f0", color: "#64748b", fontFamily: "monospace", fontSize: "0.82rem" }}>
                    {c.email}
                  </td>
                  <td style={{ padding: "10px 12px", border: "1px solid #e2e8f0", color: "#334155" }}>
                    <span style={{ background: "#f3e8ff", color: "#6b21a8", padding: "2px 8px", borderRadius: "10px", fontSize: "0.75rem", fontWeight: "600" }}>
                      {c.assigned_by || "HOD"}
                    </span>
                  </td>
                  <td style={{ padding: "10px 12px", border: "1px solid #e2e8f0", color: "#64748b", fontSize: "0.8rem" }}>
                    {c.created_at ? new Date(c.created_at).toLocaleDateString() : "Active"}
                  </td>
                  {isHodOrAdmin && (
                    <td style={{ padding: "10px 12px", border: "1px solid #e2e8f0", textAlign: "center" }}>
                      <button
                        className="btn btn-danger"
                        onClick={() => handleRevoke(c.user_id, c.full_name)}
                        disabled={submitting}
                        style={{ padding: "4px 10px", fontSize: "0.78rem" }}
                      >
                        Revoke Access
                      </button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
