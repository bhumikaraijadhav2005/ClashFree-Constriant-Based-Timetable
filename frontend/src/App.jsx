// frontend/src/App.jsx
// ClashFree: Constraint-Based Timetable & Academic Resource Management System
// Full-Featured Academic ERP Portal for HOD, Coordinators, and Faculty

import React, { useState, useEffect } from "react";
import * as api from "./api";

const ROLES = [
  { id: "ADMIN", label: "Admin (Full Access)", class: "role-admin" },
  { id: "HOD", label: "HOD (Academic & Resources)", class: "role-hod" },
  { id: "TIMETABLE_COORDINATOR", label: "Timetable Coordinator", class: "role-timetable" },
  { id: "DEPARTMENT_COORDINATOR", label: "Dept Coordinator", class: "role-coordinator" },
];

export function formatTime12Hour(val) {
  if (!val) return "";
  const s = String(val).trim();
  if (s.includes("-") && !s.includes("AM") && !s.includes("PM")) {
    const parts = s.split("-");
    if (parts.length === 2) {
      return `${formatTime12Hour(parts[0])} - ${formatTime12Hour(parts[1])}`;
    }
  }
  const ampmMatch = s.match(/^(\d{1,2})(?::(\d{2}))?\s*(AM|PM|am|pm)$/);
  if (ampmMatch) {
    const h = parseInt(ampmMatch[1], 10);
    const m = ampmMatch[2] ? ampmMatch[2] : "00";
    const mer = ampmMatch[3].toUpperCase();
    return `${h}:${m} ${mer}`;
  }
  const m24 = s.match(/^(\d{1,2}):(\d{2})/);
  if (m24) {
    let hour = parseInt(m24[1], 10);
    const min = m24[2];
    const mer = (hour >= 12 || (hour >= 1 && hour <= 7)) ? "PM" : "AM";
    hour = hour % 12;
    if (hour === 0) hour = 12;
    return `${hour}:${min} ${mer}`;
  }
  return s;
}

const PAGES = [
  { id: "dashboard", label: "Dashboard", icon: "📊" },
  { id: "timetable", label: "Timetable", icon: "📅" },
  { id: "faculty", label: "Faculty", icon: "👨‍🏫" },
  { id: "rooms", label: "Rooms", icon: "🏫" },
  { id: "subjects", label: "Subjects", icon: "📚" },
  { id: "sections", label: "Sections", icon: "👥" },
  { id: "structure", label: "Structure & Bells", icon: "🏛️" },
  { id: "reports", label: "Reports & Exports", icon: "📄" },
  { id: "preferences", label: "Preferences", icon: "⭐" },
  { id: "conflicts", label: "Conflicts", icon: "⚠️" },
  { id: "occupancy", label: "Occupancy", icon: "🏢" },
  { id: "import", label: "Import Data", icon: "📥" },
  { id: "generate", label: "Generate Timetable", icon: "⚡" },
];


export default function App() {
  const [activePage, setActivePage] = useState("dashboard");
  const [selectedDept, setSelectedDept] = useState("CSE");
  const [currentRole, setCurrentRole] = useState("HOD");
  const [departments, setDepartments] = useState([]);
  const [status, setStatus] = useState({ online: false, supabase: false });
  const [dashboardData, setDashboardData] = useState(null);
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    checkStatus();
    loadDepartments();
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [selectedDept]);

  const notify = (msg, type = "success") => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 4500);
  };

  const checkStatus = async () => {
    try {
      const res = await api.fetchStatus();
      setStatus({ online: true, supabase: res.supabase_configured });
    } catch {
      setStatus({ online: false, supabase: false });
    }
  };

  const loadDepartments = async () => {
    try {
      const data = await api.fetchDepartments();
      setDepartments(data || []);
    } catch (e) {
      console.error(e);
    }
  };

  const loadDashboard = async () => {
    try {
      const res = await api.fetchDashboard(selectedDept);
      setDashboardData(res);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <span>⏰</span>
          <div>
            <div style={{ fontSize: "1.1rem", fontWeight: "700", color: "#60a5fa" }}>CLASHFREE</div>
            <div style={{ fontSize: "0.7rem", color: "#94a3b8", fontWeight: "400" }}>Resource & Timetable ERP</div>
          </div>
        </div>

        <ul className="nav-links">
          {PAGES.map((page) => (
            <li
              key={page.id}
              className={`nav-item ${activePage === page.id ? "active" : ""}`}
              onClick={() => setActivePage(page.id)}
            >
              <span style={{ fontSize: "1.1rem" }}>{page.icon}</span>
              <span>{page.label}</span>
            </li>
          ))}
        </ul>

        <div style={{ marginTop: "auto", paddingTop: "20px", borderTop: "1px solid #1e293b", fontSize: "0.8rem", color: "#64748b" }}>
          <div>CSP + MRV Engine Active</div>
          <div style={{ marginTop: "4px" }}>B.Tech CSE Mini-Project</div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        <header className="header">
          <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
            <div className="header-title">
              {PAGES.find((p) => p.id === activePage)?.label}
            </div>

            {/* Department Context Pill */}
            <div style={{ display: "flex", alignItems: "center", gap: "6px", background: "#f8fafc", padding: "4px 8px", borderRadius: "8px", border: "1px solid #cbd5e1" }}>
              <span style={{ fontSize: "0.8rem", color: "#64748b", fontWeight: "500" }}>Dept:</span>
              <select
                value={selectedDept}
                onChange={(e) => setSelectedDept(e.target.value)}
                style={{ border: "none", background: "transparent", fontWeight: "700", color: "#1e40af", outline: "none", cursor: "pointer" }}
              >
                {departments.map((d) => (
                  <option key={d.code} value={d.code}>{d.code} - {d.name}</option>
                ))}
                {departments.length === 0 && <option value="CSE">CSE</option>}
              </select>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
            {/* Active User Role Switcher */}
            <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
              <span style={{ fontSize: "0.8rem", color: "#64748b" }}>Role:</span>
              <select
                value={currentRole}
                onChange={(e) => {
                  setCurrentRole(e.target.value);
                  notify(`Switched active view role to ${e.target.value}`);
                }}
                style={{ padding: "4px 8px", borderRadius: "6px", border: "1px solid #cbd5e1", fontSize: "0.85rem", fontWeight: "600" }}
              >
                {ROLES.map((r) => (
                  <option key={r.id} value={r.id}>{r.label}</option>
                ))}
              </select>
            </div>

            <span className={`role-pill ${ROLES.find((r) => r.id === currentRole)?.class}`}>
              {currentRole}
            </span>

            {status.supabase ? (
              <span className="badge badge-success">✓ Supabase PostgreSQL</span>
            ) : (
              <span className="badge badge-warning">⚡ Resilient Store Active</span>
            )}
          </div>
        </header>

        {notification && (
          <div
            style={{
              padding: "12px 28px",
              background: notification.type === "error" ? "#fef2f2" : "#f0fdf4",
              color: notification.type === "error" ? "#b91c1c" : "#15803d",
              borderBottom: "1px solid #e2e8f0",
              fontWeight: "500",
              fontSize: "0.9rem"
            }}
          >
            {notification.type === "error" ? "❌ " : "✅ "} {notification.msg}
          </div>
        )}

        <div className="content-body">
          {activePage === "dashboard" && (
            <DashboardView
              data={dashboardData}
              department={selectedDept}
              setPage={setActivePage}
              onRefresh={loadDashboard}
            />
          )}

          {activePage === "timetable" && (
            <TimetableView department={selectedDept} currentRole={currentRole} notify={notify} />
          )}

          {activePage === "faculty" && (
            <FacultyView department={selectedDept} notify={notify} />
          )}

          {activePage === "rooms" && (
            <RoomsView department={selectedDept} currentRole={currentRole} notify={notify} />
          )}

          {activePage === "subjects" && (
            <SubjectsView department={selectedDept} notify={notify} />
          )}

          {activePage === "sections" && (
            <AcademicStructureView department={selectedDept} notify={notify} />
          )}

          {activePage === "preferences" && (
            <PreferencesView department={selectedDept} notify={notify} />
          )}

          {activePage === "conflicts" && (
            <ConflictsView department={selectedDept} />
          )}

          {activePage === "occupancy" && (
            <OccupancyView department={selectedDept} />
          )}

          {activePage === "import" && (
            <ImportView
              notify={notify}
              onSuccess={() => {
                loadDashboard();
                setActivePage("dashboard");
              }}
            />
          )}

          {activePage === "structure" && (
            <SettingsView notify={notify} />
          )}

          {activePage === "reports" && (
            <ReportsView department={selectedDept} />
          )}

          {activePage === "generate" && (
            <GenerateTimetableView
              department={selectedDept}
              notify={notify}
              onSuccess={() => {
                loadDashboard();
                setActivePage("timetable");
              }}
            />
          )}
        </div>
      </main>
    </div>
  );
}

// =============================================================
// 1. DASHBOARD VIEW (Full ERP Metrics)
// =============================================================
function DashboardView({ data, department, setPage, onRefresh }) {
  const c = data?.counts || {};
  const [dashDivs, setDashDivs] = useState([]);
  const [selectedDivExport, setSelectedDivExport] = useState("ALL");

  useEffect(() => {
    api.fetchDivisions(department).then(divs => setDashDivs(divs || []));
  }, [department]);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <div>
          <h2>Academic Resource Management Dashboard</h2>
          <p style={{ color: "#64748b", marginTop: "4px" }}>
            Real-time status of {department} academic sections, faculty workload, resources, and scheduling feasibility.
          </p>
        </div>
        <button className="btn btn-secondary" onClick={onRefresh}>
          🔄 Refresh Metrics
        </button>
      </div>

      {/* 10 Required KPI Cards */}
      <div className="grid-cards" style={{ gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "16px" }}>
        <div className="card" style={{ borderTop: "3px solid #2563eb" }}>
          <div className="card-title">Total Sections</div>
          <div className="card-value">{c.sections || c.divisions || 0}</div>
          <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "4px" }}>Academic Divisions</div>
        </div>

        <div className="card" style={{ borderTop: "3px solid #0f766e" }}>
          <div className="card-title">Total Faculty</div>
          <div className="card-value">{c.faculty || 0}</div>
          <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "4px" }}>Qualified Instructors</div>
        </div>

        <div className="card" style={{ borderTop: "3px solid #6366f1" }}>
          <div className="card-title">Total Subjects</div>
          <div className="card-value">{c.subjects || 0}</div>
          <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "4px" }}>Theory & Lab Courses</div>
        </div>

        <div className="card" style={{ borderTop: "3px solid #0284c7" }}>
          <div className="card-title">Total Classrooms</div>
          <div className="card-value">{c.classrooms_total || 0}</div>
          <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "4px" }}>Capacity Matched</div>
        </div>

        <div className="card" style={{ borderTop: "3px solid #8b5cf6" }}>
          <div className="card-title">Total Labs</div>
          <div className="card-value">{c.labs_total || 0}</div>
          <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "4px" }}>Specialized Facilities</div>
        </div>

        <div className="card" style={{ borderTop: "3px solid #10b981" }}>
          <div className="card-title">Scheduled Sessions</div>
          <div className="card-value">{c.scheduled || 0}</div>
          <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "4px" }}>Active Timetable Slots</div>
        </div>

        <div className="card" style={{ borderTop: "3px solid #3b82f6" }}>
          <div className="card-title">Detected Clashes</div>
          <div className="card-value">{c.detected_clashes || 0}</div>
          <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "4px" }}>Identified by CSP</div>
        </div>

        <div className="card" style={{ borderTop: "3px solid #10b981" }}>
          <div className="card-title">Resolved Clashes</div>
          <div className="card-value" style={{ color: "#10b981" }}>{c.resolved_clashes || 0}</div>
          <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "4px" }}>Backtracking Solutions</div>
        </div>

        <div className="card" style={{ borderTop: "3px solid #14b8a6" }}>
          <div className="card-title">Available Classrooms</div>
          <div className="card-value" style={{ color: "#0f766e" }}>{c.classrooms_available || 0}</div>
          <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "4px" }}>{c.classrooms_occupied || 0} Occupied</div>
        </div>

        <div className="card" style={{ borderTop: "3px solid #a855f7" }}>
          <div className="card-title">Available Labs</div>
          <div className="card-value" style={{ color: "#7c3aed" }}>{c.labs_available || 0}</div>
          <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "4px" }}>{c.labs_occupied || 0} Occupied</div>
        </div>
      </div>

      {/* Timetable & Workload Excel Exports */}
      <div className="card" style={{ marginTop: "24px", border: "1px solid #cbd5e1", background: "#f8fafc" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
          <div>
            <h3 style={{ margin: 0, color: "#1e3a8a" }}>📥 Timetable & Workload Excel Downloads</h3>
            <p style={{ color: "#64748b", margin: "4px 0 0", fontSize: "0.85rem" }}>
              Collegiate matrix layout with courses, faculty codes, rooms, and signature fields.
            </p>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
            <label style={{ fontSize: "0.85rem", fontWeight: 700 }}>Choose Division:</label>
            <select
              value={selectedDivExport}
              onChange={(e) => setSelectedDivExport(e.target.value)}
              style={{ padding: "6px 12px", borderRadius: "6px", border: "1px solid #cbd5e1", fontWeight: 600 }}
            >
              <option value="ALL">All Divisions (Master Multi-Tab Workbook)</option>
              {dashDivs.map((d) => (
                <option key={d.name} value={d.name}>
                  {d.name} ({d.year || "Second Year"})
                </option>
              ))}
            </select>
            <a
              href={api.getExportTimetableUrl(department, selectedDivExport === "ALL" ? "" : selectedDivExport)}
              className="btn"
              style={{ background: "#1e40af", color: "#fff" }}
              target="_blank"
              rel="noreferrer"
            >
              {selectedDivExport === "ALL" ? "📥 Download Master Timetable (.xlsx)" : `📥 Download ${selectedDivExport} (.xlsx)`}
            </a>
            <a
              href={api.getExportWorkloadUrl(department)}
              className="btn btn-secondary"
              target="_blank"
              rel="noreferrer"
            >
              📊 Workload Report (.xlsx)
            </a>
          </div>
        </div>
      </div>

      {/* Quick Operational Actions (Section 22 requirement) */}
      <div className="card" style={{ marginTop: "24px" }}>
        <h3 style={{ marginBottom: "16px" }}>⚡ Quick Operational Actions</h3>
        <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
          <button className="btn" onClick={() => setPage("import")}>
            📥 Import Excel
          </button>
          <button className="btn btn-secondary" onClick={() => setPage("import")}>
            🔍 Validate Data
          </button>
          <button className="btn btn-secondary" style={{ background: "#2563eb", color: "#fff" }} onClick={() => setPage("generate")}>
            ⚡ Generate Timetable
          </button>
          <button className="btn btn-secondary" onClick={() => setPage("timetable")}>
            📅 View Timetable
          </button>
          <button className="btn btn-secondary" onClick={() => setPage("conflicts")}>
            ⚠️ View Conflicts
          </button>
          <button className="btn btn-secondary" onClick={() => setPage("occupancy")}>
            🏢 View Occupancy
          </button>
        </div>
      </div>
    </div>
  );
}

// =============================================================
// 2. ACADEMIC STRUCTURE VIEW (Departments, Divisions, Batches)
// =============================================================
function AcademicStructureView({ department, notify }) {
  const [tab, setTab] = useState("divisions");
  const [departments, setDepartments] = useState([]);
  const [divisions, setDivisions] = useState([]);
  const [batches, setBatches] = useState([]);

  // Forms
  const [divName, setDivName] = useState("");
  const [divStrength, setDivStrength] = useState(75);
  const [batchDiv, setBatchDiv] = useState("");
  const [batchName, setBatchName] = useState("");
  const [batchStrength, setBatchStrength] = useState(38);
  const [deptCode, setDeptCode] = useState("");
  const [deptName, setDeptName] = useState("");

  useEffect(() => {
    loadAll();
  }, [department]);

  const loadAll = async () => {
    const depts = await api.fetchDepartments();
    const divs = await api.fetchDivisions(department);
    const bts = await api.fetchBatches();
    setDepartments(depts || []);
    setDivisions(divs || []);
    setBatches(bts || []);
    if (divs && divs.length > 0) setBatchDiv(divs[0].name);
  };

  const handleAddDivision = async (e) => {
    e.preventDefault();
    if (!divName) return;
    await api.saveDivision({
      name: divName,
      strength: Number(divStrength),
      department_code: department,
      degree: "B.Tech",
      year: "Second Year",
      semester: "Semester III"
    });
    setDivName("");
    notify("Division added with custom student strength");
    loadAll();
  };

  const handleAddBatch = async (e) => {
    e.preventDefault();
    if (!batchName || !batchDiv) return;
    await api.saveBatch({
      division_name: batchDiv,
      name: batchName,
      strength: Number(batchStrength)
    });
    setBatchName("");
    notify("Batch added to division");
    loadAll();
  };

  const handleAddDept = async (e) => {
    e.preventDefault();
    if (!deptCode || !deptName) return;
    await api.saveDepartment({ code: deptCode.toUpperCase(), name: deptName });
    setDeptCode("");
    setDeptName("");
    notify("Department registered");
    loadAll();
  };

  return (
    <div>
      <div className="subtabs">
        <button className={`subtab-btn ${tab === "divisions" ? "active" : ""}`} onClick={() => setTab("divisions")}>
          👥 Divisions & Strengths
        </button>
        <button className={`subtab-btn ${tab === "batches" ? "active" : ""}`} onClick={() => setTab("batches")}>
          🔬 Practical Batches
        </button>
        <button className={`subtab-btn ${tab === "departments" ? "active" : ""}`} onClick={() => setTab("departments")}>
          🏛️ Departments
        </button>
      </div>

      {tab === "divisions" && (
        <div>
          <form onSubmit={handleAddDivision} className="card" style={{ display: "flex", gap: "12px", alignItems: "center", marginBottom: "20px" }}>
            <input
              placeholder="Division Name (e.g. Division A, Division B)"
              value={divName}
              onChange={(e) => setDivName(e.target.value)}
              style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #ccc", flex: 1 }}
            />
            <label style={{ fontSize: "0.85rem", fontWeight: "600" }}>Student Strength:</label>
            <input
              type="number"
              value={divStrength}
              onChange={(e) => setDivStrength(e.target.value)}
              style={{ padding: "8px", borderRadius: "6px", border: "1px solid #ccc", width: "90px" }}
            />
            <button type="submit" className="btn">+ Add Division</button>
          </form>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Division Name</th>
                  <th>Department</th>
                  <th>Class / Semester</th>
                  <th>Student Strength</th>
                  <th>Capacity Constraint Rule</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {divisions.map((d) => (
                  <tr key={d.id || d.name}>
                    <td><strong>{d.name}</strong></td>
                    <td>{d.department_code || department}</td>
                    <td>{d.year || "Second Year"} ({d.semester || "Semester III"})</td>
                    <td><span className="badge badge-success">{d.strength} students</span></td>
                    <td style={{ color: "#64748b", fontSize: "0.85rem" }}>
                      Requires Classroom Capacity ≥ {d.strength}
                    </td>
                    <td>
                      <button className="btn btn-danger" style={{ padding: "4px 8px", fontSize: "0.8rem" }} onClick={async () => { await api.deleteDivision(d.id); loadAll(); }}>
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === "batches" && (
        <div>
          <form onSubmit={handleAddBatch} className="card" style={{ display: "flex", gap: "12px", alignItems: "center", marginBottom: "20px" }}>
            <label style={{ fontSize: "0.85rem" }}>Division:</label>
            <select
              value={batchDiv}
              onChange={(e) => setBatchDiv(e.target.value)}
              style={{ padding: "8px", borderRadius: "6px", border: "1px solid #ccc" }}
            >
              {divisions.map((d) => (
                <option key={d.name} value={d.name}>{d.name}</option>
              ))}
            </select>
            <input
              placeholder="Batch Name (e.g. A1, A2, B1, B2)"
              value={batchName}
              onChange={(e) => setBatchName(e.target.value)}
              style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #ccc", flex: 1 }}
            />
            <label style={{ fontSize: "0.85rem" }}>Batch Strength:</label>
            <input
              type="number"
              value={batchStrength}
              onChange={(e) => setBatchStrength(e.target.value)}
              style={{ padding: "8px", borderRadius: "6px", border: "1px solid #ccc", width: "90px" }}
            />
            <button type="submit" className="btn">+ Add Batch</button>
          </form>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Batch</th>
                  <th>Parent Division</th>
                  <th>Students Count</th>
                  <th>Lab Scheduling Rule</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {batches.map((b) => (
                  <tr key={b.id || b.name}>
                    <td><strong>{b.name}</strong></td>
                    <td>{b.division_name}</td>
                    <td>{b.strength} students</td>
                    <td style={{ color: "#64748b", fontSize: "0.85rem" }}>
                      Lab Capacity ≥ {b.strength} & PCs ≥ {b.strength}
                    </td>
                    <td>
                      <button className="btn btn-danger" style={{ padding: "4px 8px", fontSize: "0.8rem" }} onClick={async () => { await api.deleteBatch(b.id); loadAll(); }}>
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === "departments" && (
        <div>
          <form onSubmit={handleAddDept} className="card" style={{ display: "flex", gap: "12px", alignItems: "center", marginBottom: "20px" }}>
            <input
              placeholder="Code (e.g. CSE, E&TC, MECH)"
              value={deptCode}
              onChange={(e) => setDeptCode(e.target.value)}
              style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #ccc", width: "160px" }}
            />
            <input
              placeholder="Full Department Name"
              value={deptName}
              onChange={(e) => setDeptName(e.target.value)}
              style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #ccc", flex: 1 }}
            />
            <button type="submit" className="btn">+ Register Department</button>
          </form>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Code</th>
                  <th>Department Name</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {departments.map((dep) => (
                  <tr key={dep.id || dep.code}>
                    <td><strong>{dep.code}</strong></td>
                    <td>{dep.name}</td>
                    <td>
                      <button className="btn btn-danger" style={{ padding: "4px 8px", fontSize: "0.8rem" }} onClick={async () => { await api.deleteDepartment(dep.id); loadAll(); }}>
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================
// 3. FACULTY & WORKLOAD VIEW (Auto Short Codes, Workload & Load Report)
// =============================================================
function FacultyView({ department, notify }) {
  const [tab, setTab] = useState("list");
  const [faculty, setFaculty] = useState([]);
  const [workload, setWorkload] = useState([]);
  const [loadReport, setLoadReport] = useState([]);

  // Add Faculty Form
  const [name, setName] = useState("");
  const [designation, setDesignation] = useState("Assistant Professor");
  const [subjects, setSubjects] = useState("");
  const [pref, setPref] = useState("Morning");
  const [availFrom, setAvailFrom] = useState("09:00");
  const [availTo, setAvailTo] = useState("17:00");
  const [maxLoad, setMaxLoad] = useState(18);

  useEffect(() => {
    loadAll();
  }, [department]);

  const loadAll = async () => {
    const fList = await api.fetchFaculty(department);
    const wList = await api.fetchFacultyWorkload(department);
    const rList = await api.fetchAcademicLoadReport(department);
    setFaculty(fList || []);
    setWorkload(wList || []);
    setLoadReport(rList || []);
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!name) return;
    const subjArr = subjects.split(",").map((s) => s.trim()).filter(Boolean);
    await api.saveFaculty({
      name,
      designation,
      department,
      subjects: subjArr,
      preferred_time: pref,
      available_from: availFrom,
      available_to: availTo,
      max_load: Number(maxLoad)
    });
    setName("");
    setSubjects("");
    notify("Faculty registered with automatic short-code generation!");
    loadAll();
  };

  return (
    <div>
      <div className="subtabs">
        <button className={`subtab-btn ${tab === "list" ? "active" : ""}`} onClick={() => setTab("list")}>
          👨‍🏫 Faculty Directory & Short Codes
        </button>
        <button className={`subtab-btn ${tab === "workload" ? "active" : ""}`} onClick={() => setTab("workload")}>
          ⚖️ Weekly Workload Distribution
        </button>
        <button className={`subtab-btn ${tab === "report" ? "active" : ""}`} onClick={() => setTab("report")}>
          📋 Academic Load Report (College Format)
        </button>
      </div>

      {tab === "list" && (
        <div>
          <form onSubmit={handleAdd} className="card" style={{ marginBottom: "20px" }}>
            <h4 style={{ marginBottom: "12px" }}>Register Faculty Member</h4>
            <div style={{ display: "grid", gridTemplateColumns: "2fr 1.5fr 2fr", gap: "12px", marginBottom: "12px" }}>
              <input
                placeholder="Full Name (e.g. Mr. Vishal H. Pundikar)"
                value={name}
                onChange={(e) => setName(e.target.value)}
                style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #ccc" }}
              />
              <select
                value={designation}
                onChange={(e) => setDesignation(e.target.value)}
                style={{ padding: "8px", borderRadius: "6px", border: "1px solid #ccc" }}
              >
                <option value="Assistant Professor">Assistant Professor</option>
                <option value="Associate Professor">Associate Professor</option>
                <option value="Professor">Professor</option>
                <option value="Professor & HOD">Professor & HOD</option>
              </select>
              <input
                placeholder="Subjects (e.g. DSA, DS Lab, OS)"
                value={subjects}
                onChange={(e) => setSubjects(e.target.value)}
                style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #ccc" }}
              />
            </div>
            <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
              <label style={{ fontSize: "0.85rem" }}>Preference:</label>
              <select value={pref} onChange={(e) => setPref(e.target.value)} style={{ padding: "8px", borderRadius: "6px", border: "1px solid #ccc" }}>
                <option value="Morning">Morning Preference</option>
                <option value="Afternoon">Afternoon Preference</option>
                <option value="Any">Any Time Slot</option>
              </select>
              <label style={{ fontSize: "0.85rem" }}>Available From:</label>
              <input type="text" value={availFrom} onChange={(e) => setAvailFrom(e.target.value)} style={{ width: "75px", padding: "6px", borderRadius: "6px", border: "1px solid #ccc" }} />
              <label style={{ fontSize: "0.85rem" }}>To:</label>
              <input type="text" value={availTo} onChange={(e) => setAvailTo(e.target.value)} style={{ width: "75px", padding: "6px", borderRadius: "6px", border: "1px solid #ccc" }} />
              <label style={{ fontSize: "0.85rem" }}>Max Load:</label>
              <input type="number" value={maxLoad} onChange={(e) => setMaxLoad(e.target.value)} style={{ width: "70px", padding: "6px", borderRadius: "6px", border: "1px solid #ccc" }} />
              <button type="submit" className="btn" style={{ marginLeft: "auto" }}>+ Register Faculty</button>
            </div>
          </form>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Short Code</th>
                  <th>Full Name</th>
                  <th>Designation</th>
                  <th>Qualified Subjects</th>
                  <th>Hard Availability</th>
                  <th>Preference</th>
                  <th>Max Load</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {faculty.map((f) => (
                  <tr key={f.id || f.code}>
                    <td><strong style={{ color: "#2563eb", fontSize: "1.05rem" }}>{f.code}</strong></td>
                    <td>{f.name}</td>
                    <td><span className="badge" style={{ background: "#f1f5f9" }}>{f.designation || "Faculty"}</span></td>
                    <td>{Array.isArray(f.subjects) ? f.subjects.join(", ") : f.subjects}</td>
                    <td>{f.available_from} - {f.available_to}</td>
                    <td>{f.preferred_time}</td>
                    <td>{f.max_load} hrs/wk</td>
                    <td>
                      <button className="btn btn-danger" style={{ padding: "4px 8px", fontSize: "0.8rem" }} onClick={async () => { await api.deleteFaculty(f.id); loadAll(); }}>
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === "workload" && (
        <div>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Faculty</th>
                  <th>Short Code</th>
                  <th>Designation</th>
                  <th>Lecture Hrs</th>
                  <th>Lab Hrs</th>
                  <th>Total Weekly Load</th>
                  <th>Max Allowed</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {workload.map((w) => (
                  <tr key={w.short_code}>
                    <td><strong>{w.faculty_name}</strong></td>
                    <td><span className="badge" style={{ background: "#e0e7ff", color: "#3730a3" }}>{w.short_code}</span></td>
                    <td>{w.designation}</td>
                    <td>{w.lecture_hours} hrs</td>
                    <td>{w.lab_hours} hrs</td>
                    <td><strong>{w.total_hours} hrs/week</strong></td>
                    <td>{w.max_load} hrs</td>
                    <td>
                      <span className={`status-badge status-${w.status.toLowerCase()}`}>
                        {w.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === "report" && (
        <div>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <h4>Department Academic Load Report (Direct & Indirect Contact Hours)</h4>
            <a href={api.getExportWorkloadUrl(department)} className="btn btn-secondary" target="_blank" rel="noreferrer">
              📥 Export Load Report (Excel)
            </a>
          </div>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Faculty Name</th>
                  <th>Code</th>
                  <th>Designation</th>
                  <th>Class / Year</th>
                  <th>Div / Batch</th>
                  <th>Course</th>
                  <th>Lec</th>
                  <th>Lab</th>
                  <th>Direct Contact</th>
                  <th>Project</th>
                  <th>Seminar</th>
                  <th>Grand Total</th>
                </tr>
              </thead>
              <tbody>
                {loadReport.map((r, i) => (
                  <tr key={i}>
                    <td><strong>{r.faculty_name}</strong></td>
                    <td>{r.short_code}</td>
                    <td>{r.designation}</td>
                    <td>{r.class_year}</td>
                    <td>{r.division_batch}</td>
                    <td><strong>{r.course_name}</strong></td>
                    <td>{r.lecture_hours}</td>
                    <td>{r.lab_hours}</td>
                    <td><strong>{r.direct_contact_hours}</strong></td>
                    <td>{r.project_hours}</td>
                    <td>{r.seminar_hours}</td>
                    <td style={{ fontWeight: "700", color: "#1e40af" }}>{r.grand_total} hrs</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================
// 4. SUBJECTS VIEW (Lectures, Batch Labs & Session Generator)
// =============================================================
function SubjectsView({ department, notify }) {
  const [subjects, setSubjects] = useState([]);
  const [name, setName] = useState("");
  const [lec, setLec] = useState(4);
  const [lab, setLab] = useState(0);
  const [labType, setLabType] = useState("Computer Lab");

  useEffect(() => { load(); }, [department]);

  const load = async () => {
    const data = await api.fetchSubjects(department);
    setSubjects(data || []);
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!name) return;
    await api.saveSubject({
      name,
      department,
      lectures_per_week: Number(lec),
      labs_per_week: Number(lab),
      requires_lab: Number(lab) > 0,
      lab_type: Number(lab) > 0 ? labType : "",
      student_pc_ratio: 1.0
    });
    setName("");
    notify("Subject created with automatic weekly session breakdown");
    load();
  };

  return (
    <div>
      <form onSubmit={handleAdd} className="card" style={{ display: "flex", gap: "12px", alignItems: "center", marginBottom: "20px" }}>
        <input
          placeholder="Subject Name (e.g. DSA, DS Lab, DBMS)"
          value={name}
          onChange={(e) => setName(e.target.value)}
          style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #ccc", flex: 1 }}
        />
        <label style={{ fontSize: "0.85rem" }}>Lec/wk:</label>
        <input type="number" value={lec} onChange={(e) => setLec(e.target.value)} style={{ padding: "8px", borderRadius: "6px", border: "1px solid #ccc", width: "65px" }} />
        <label style={{ fontSize: "0.85rem" }}>Lab/wk:</label>
        <input type="number" value={lab} onChange={(e) => setLab(e.target.value)} style={{ padding: "8px", borderRadius: "6px", border: "1px solid #ccc", width: "65px" }} />
        {Number(lab) > 0 && (
          <select value={labType} onChange={(e) => setLabType(e.target.value)} style={{ padding: "8px", borderRadius: "6px", border: "1px solid #ccc" }}>
            <option value="Computer Lab">Computer Lab (1:1 PC)</option>
            <option value="Hardware Lab">Hardware Lab</option>
            <option value="Network Lab">Network Lab</option>
          </select>
        )}
        <button type="submit" className="btn">+ Add Subject</button>
      </form>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Subject</th>
              <th>Lectures / Wk</th>
              <th>Labs / Wk</th>
              <th>Requires Lab</th>
              <th>Internally Generated Sessions (CSP Variables)</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {subjects.map((s) => (
              <tr key={s.id || s.name}>
                <td><strong>{s.name}</strong></td>
                <td>{s.lectures_per_week} hrs</td>
                <td>{s.labs_per_week} hrs</td>
                <td>{s.requires_lab ? "🔬 Yes" : "📚 No"}</td>
                <td>
                  <span style={{ fontSize: "0.85rem", color: "#475569" }}>
                    {s.lectures_per_week > 0 && `Lecture: ${Array.from({ length: s.lectures_per_week }, (_, i) => `S${i + 1}`).join(", ")}`}
                    {s.labs_per_week > 0 && ` | Labs: ${Array.from({ length: s.labs_per_week }, (_, i) => `Batch Lab ${i + 1}`).join(", ")}`}
                  </span>
                </td>
                <td>
                  <button className="btn btn-danger" style={{ padding: "4px 8px", fontSize: "0.8rem" }} onClick={async () => { await api.deleteSubject(s.id); load(); }}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// =============================================================
// 5. RESOURCES & LABS VIEW (Inventory, Reservation Config, Slot Occupancy, Sharing)
// =============================================================
function ResourcesView({ department, currentRole, notify }) {
  const [tab, setTab] = useState("occupancy");
  const [rooms, setRooms] = useState([]);
  const [resourceConfig, setResourceConfig] = useState(null);
  const [sharingRequests, setSharingRequests] = useState([]);

  // Slot Occupancy filter state
  const [occDay, setOccDay] = useState("Monday");
  const [occPeriod, setOccPeriod] = useState("09:00-10:00");
  const [occType, setOccType] = useState("ALL");
  const [occupancyData, setOccupancyData] = useState(null);

  // Add room form
  const [rName, setRName] = useState("");
  const [rType, setRType] = useState("Classroom");
  const [rCap, setRCap] = useState(80);
  const [rPcs, setRPcs] = useState(0);
  const [rReserved, setRReserved] = useState(false);
  const [rReason, setRReason] = useState("");

  // Resource sharing request form
  const [reqResource, setReqResource] = useState("");
  const [reqDay, setReqDay] = useState("Monday");
  const [reqPeriod, setReqPeriod] = useState("14:00-15:00");
  const [reqReason, setReqReason] = useState("");

  useEffect(() => {
    loadAll();
  }, [department]);

  useEffect(() => {
    loadOccupancy();
  }, [occDay, occPeriod, occType, department]);

  const loadAll = async () => {
    const rList = await api.fetchRooms(department);
    const cfg = await api.fetchResourceConfig(department);
    const reqs = await api.fetchResourceSharing();
    setRooms(rList || []);
    setResourceConfig(cfg);
    setSharingRequests(reqs || []);
    if (rList && rList.length > 0) setReqResource(rList[0].name);
  };

  const loadOccupancy = async () => {
    try {
      const data = await api.fetchOccupancy(occDay, occPeriod, department, occType);
      setOccupancyData(data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleAddRoom = async (e) => {
    e.preventDefault();
    if (!rName) return;
    await api.saveRoom({
      name: rName,
      type: rType,
      capacity: Number(rCap),
      department,
      num_pcs: rType === "Lab" ? Number(rPcs) : 0,
      lab_type: rType === "Lab" ? "Computer Lab" : "",
      equipment: rType === "Lab" ? `${rPcs} PCs, Gigabit LAN` : "Projector",
      is_reserved: rReserved,
      reservation_reason: rReason
    });
    setRName("");
    setRReason("");
    notify("Resource added successfully");
    loadAll();
  };

  const handleSaveConfig = async (e) => {
    e.preventDefault();
    await api.saveResourceConfig(resourceConfig);
    notify("HOD Resource Reservation configuration updated!");
    loadAll();
    loadOccupancy();
  };

  const handleRequestSharing = async (e) => {
    e.preventDefault();
    if (!reqResource || !reqReason) return;
    const res = await api.createResourceSharingRequest({
      resource_name: reqResource,
      day: reqDay,
      period: reqPeriod,
      requesting_department: department,
      reason: reqReason,
      requested_by: `${currentRole} (${department})`
    });
    if (res.error) {
      notify(res.error, "error");
    } else {
      notify("Resource sharing request submitted!");
      loadAll();
      setReqReason("");
    }
  };

  const handleUpdateSharingStatus = async (id, status) => {
    await api.updateResourceSharingStatus(id, status, `${currentRole} (${department})`);
    notify(`Sharing request marked as ${status}`);
    loadAll();
    loadOccupancy();
  };

  const PERIODS = [
    "09:00-10:00",
    "10:00-11:00",
    "11:15-12:15",
    "13:00-14:00",
    "14:00-15:00",
    "15:15-16:15",
  ];

  const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];

  return (
    <div>
      <div className="subtabs">
        <button className={`subtab-btn ${tab === "occupancy" ? "active" : ""}`} onClick={() => setTab("occupancy")}>
          📍 Slot-Wise Occupancy Matrix
        </button>
        <button className={`subtab-btn ${tab === "inventory" ? "active" : ""}`} onClick={() => setTab("inventory")}>
          🏫 Classrooms & Labs Inventory
        </button>
        <button className={`subtab-btn ${tab === "reservation" ? "active" : ""}`} onClick={() => setTab("reservation")}>
          🔒 HOD Resource Reservation Config
        </button>
        <button className={`subtab-btn ${tab === "sharing" ? "active" : ""}`} onClick={() => setTab("sharing")}>
          🤝 Inter-Department Resource Sharing
        </button>
      </div>

      {/* TAB 1: SLOT-WISE OCCUPANCY (HOD Requirement 6 & 7) */}
      {tab === "occupancy" && (
        <div>
          <div className="filter-bar">
            <div>
              <label style={{ fontSize: "0.85rem", fontWeight: "600", marginRight: "8px" }}>Select Day:</label>
              <select value={occDay} onChange={(e) => setOccDay(e.target.value)} style={{ padding: "6px 10px", borderRadius: "6px", border: "1px solid #ccc" }}>
                {DAYS.map((d) => <option key={d} value={d}>{d}</option>)}
              </select>
            </div>

            <div>
              <label style={{ fontSize: "0.85rem", fontWeight: "600", marginRight: "8px" }}>Time Slot:</label>
              <select value={occPeriod} onChange={(e) => setOccPeriod(e.target.value)} style={{ padding: "6px 10px", borderRadius: "6px", border: "1px solid #ccc" }}>
                {PERIODS.map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>

            <div>
              <label style={{ fontSize: "0.85rem", fontWeight: "600", marginRight: "8px" }}>Type:</label>
              <select value={occType} onChange={(e) => setOccType(e.target.value)} style={{ padding: "6px 10px", borderRadius: "6px", border: "1px solid #ccc" }}>
                <option value="ALL">All Resources</option>
                <option value="Classroom">Classrooms Only</option>
                <option value="Lab">Laboratories Only</option>
              </select>
            </div>

            <div style={{ marginLeft: "auto", fontSize: "0.85rem", color: "#64748b" }}>
              Viewing slot: <strong>{occDay} {occPeriod}</strong>
            </div>
          </div>

          {/* Occupancy Summary Counters */}
          {occupancyData?.summary && (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "20px" }}>
              <div className="card" style={{ padding: "14px", borderLeft: "4px solid #2563eb" }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <strong>{department} Classrooms (This Slot)</strong>
                  <span className="badge badge-success">{occupancyData.summary.classrooms.occupancy_pct}% Occupancy</span>
                </div>
                <div style={{ display: "flex", gap: "16px", marginTop: "10px", fontSize: "0.9rem" }}>
                  <div>Total: <strong>{occupancyData.summary.classrooms.total}</strong></div>
                  <div style={{ color: "#dc2626" }}>Occupied: <strong>{occupancyData.summary.classrooms.occupied}</strong></div>
                  <div style={{ color: "#16a34a" }}>Available: <strong>{occupancyData.summary.classrooms.available}</strong></div>
                  <div style={{ color: "#d97706" }}>Reserved: <strong>{occupancyData.summary.classrooms.reserved}</strong></div>
                </div>
              </div>

              <div className="card" style={{ padding: "14px", borderLeft: "4px solid #8b5cf6" }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <strong>{department} Labs (This Slot)</strong>
                  <span className="badge badge-success">{occupancyData.summary.labs.occupancy_pct}% Occupancy</span>
                </div>
                <div style={{ display: "flex", gap: "16px", marginTop: "10px", fontSize: "0.9rem" }}>
                  <div>Total: <strong>{occupancyData.summary.labs.total}</strong></div>
                  <div style={{ color: "#dc2626" }}>Occupied: <strong>{occupancyData.summary.labs.occupied}</strong></div>
                  <div style={{ color: "#16a34a" }}>Available: <strong>{occupancyData.summary.labs.available}</strong></div>
                  <div style={{ color: "#d97706" }}>Reserved: <strong>{occupancyData.summary.labs.reserved}</strong></div>
                </div>
              </div>
            </div>
          )}

          {/* Slot-wise Resources Table */}
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Resource</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Current Allocation</th>
                  <th>Division / Batch</th>
                  <th>Faculty</th>
                  <th>Subject</th>
                  <th>Notes / Reservation</th>
                </tr>
              </thead>
              <tbody>
                {occupancyData?.resources?.map((r) => (
                  <tr key={r.resource}>
                    <td><strong>{r.resource}</strong></td>
                    <td>{r.type === "Lab" ? "🔬 Lab" : "📚 Classroom"}</td>
                    <td>
                      <span className={`status-badge status-${r.status.toLowerCase().split(" ")[0]}`}>
                        {r.status}
                      </span>
                    </td>
                    <td>{r.allocation.notes}</td>
                    <td>{r.allocation.division} {r.allocation.batch !== "-" ? `(${r.allocation.batch})` : ""}</td>
                    <td>{r.allocation.faculty}</td>
                    <td><strong>{r.allocation.subject}</strong></td>
                    <td style={{ color: "#64748b", fontSize: "0.85rem" }}>
                      Cap: {r.capacity} {r.type === "Lab" && `| PCs: ${r.num_pcs}`}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 2: INVENTORY */}
      {tab === "inventory" && (
        <div>
          <form onSubmit={handleAddRoom} className="card" style={{ marginBottom: "20px" }}>
            <h4 style={{ marginBottom: "12px" }}>Add Physical Classroom or Lab</h4>
            <div style={{ display: "grid", gridTemplateColumns: "1.5fr 1fr 1fr 1fr 1fr", gap: "12px", marginBottom: "12px" }}>
              <input
                placeholder="Resource Name (e.g. CR-01, LAB-01)"
                value={rName}
                onChange={(e) => setRName(e.target.value)}
                style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #ccc" }}
              />
              <select value={rType} onChange={(e) => setRType(e.target.value)} style={{ padding: "8px", borderRadius: "6px", border: "1px solid #ccc" }}>
                <option value="Classroom">Classroom</option>
                <option value="Lab">Laboratory</option>
              </select>
              <input
                type="number"
                placeholder="Capacity"
                value={rCap}
                onChange={(e) => setRCap(e.target.value)}
                style={{ padding: "8px", borderRadius: "6px", border: "1px solid #ccc" }}
              />
              <input
                type="number"
                placeholder="PCs (if Lab)"
                value={rPcs}
                onChange={(e) => setRPcs(e.target.value)}
                style={{ padding: "8px", borderRadius: "6px", border: "1px solid #ccc" }}
              />
              <label style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.85rem" }}>
                <input type="checkbox" checked={rReserved} onChange={(e) => setRReserved(e.target.checked)} />
                Reserve Resource
              </label>
            </div>
            {rReserved && (
              <div style={{ marginBottom: "12px" }}>
                <input
                  placeholder="Reason for reservation (e.g. HOD Electives, Project Work)"
                  value={rReason}
                  onChange={(e) => setRReason(e.target.value)}
                  style={{ width: "100%", padding: "8px 12px", borderRadius: "6px", border: "1px solid #ccc" }}
                />
              </div>
            )}
            <button type="submit" className="btn">+ Add Resource</button>
          </form>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Resource Name</th>
                  <th>Type</th>
                  <th>Capacity</th>
                  <th>PCs</th>
                  <th>Department</th>
                  <th>HOD Reservation Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {rooms.map((r) => (
                  <tr key={r.id || r.name}>
                    <td><strong>{r.name}</strong></td>
                    <td>{r.type === "Lab" ? "🔬 Lab" : "📚 Classroom"}</td>
                    <td>{r.capacity} seats</td>
                    <td>{r.type === "Lab" ? `${r.num_pcs || 0} PCs` : "-"}</td>
                    <td>{r.department || department}</td>
                    <td>
                      {r.is_reserved ? (
                        <span className="status-badge status-reserved">
                          🔒 RESERVED: {r.reservation_reason || "HOD Reserve"}
                        </span>
                      ) : (
                        <span className="status-badge status-available">✓ Scheduling Active</span>
                      )}
                    </td>
                    <td>
                      <button className="btn btn-danger" style={{ padding: "4px 8px", fontSize: "0.8rem" }} onClick={async () => { await api.deleteRoom(r.id); loadAll(); }}>
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 3: HOD RESOURCE RESERVATION CONFIGURATION (HOD Requirement 4) */}
      {tab === "reservation" && (
        <div className="card" style={{ maxWidth: "700px" }}>
          <h3>🔒 HOD Resource Reservation Policy</h3>
          <p style={{ color: "#64748b", margin: "8px 0 20px" }}>
            The HOD requires that the scheduler does NOT use every physical classroom and lab.
            Configure how many resources must remain reserved for seminar, electives, or ad-hoc purposes.
          </p>

          {resourceConfig && (
            <form onSubmit={handleSaveConfig} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              <div style={{ background: "#f8fafc", padding: "16px", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
                <label style={{ display: "block", fontWeight: "600", marginBottom: "6px" }}>
                  Reserved Classrooms Quota:
                </label>
                <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
                  <input
                    type="number"
                    min="0"
                    value={resourceConfig.reserved_classrooms_count}
                    onChange={(e) => setResourceConfig({ ...resourceConfig, reserved_classrooms_count: Number(e.target.value) })}
                    style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #ccc", width: "100px" }}
                  />
                  <span style={{ fontSize: "0.85rem", color: "#64748b" }}>
                    Example: If CSE has 10 classrooms and Reserved = 1, scheduler uses 10 - 1 = 9 classrooms.
                  </span>
                </div>
              </div>

              <div style={{ background: "#f8fafc", padding: "16px", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
                <label style={{ display: "block", fontWeight: "600", marginBottom: "6px" }}>
                  Reserved Labs Quota:
                </label>
                <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
                  <input
                    type="number"
                    min="0"
                    value={resourceConfig.reserved_labs_count}
                    onChange={(e) => setResourceConfig({ ...resourceConfig, reserved_labs_count: Number(e.target.value) })}
                    style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #ccc", width: "100px" }}
                  />
                  <span style={{ fontSize: "0.85rem", color: "#64748b" }}>
                    Example: If CSE has 6 labs and Reserved = 1, scheduler automatically uses 6 - 1 = 5 labs.
                  </span>
                </div>
              </div>

              <div style={{ background: "#f8fafc", padding: "16px", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
                <label style={{ display: "block", fontWeight: "600", marginBottom: "6px" }}>
                  Student-to-PC Ratio Constraint:
                </label>
                <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
                  <input
                    type="text"
                    value={resourceConfig.student_pc_ratio}
                    onChange={(e) => setResourceConfig({ ...resourceConfig, student_pc_ratio: e.target.value })}
                    style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #ccc", width: "100px" }}
                  />
                  <span style={{ fontSize: "0.85rem", color: "#64748b" }}>
                    Default 1:1 (30 students require at least 30 PCs in the allocated lab).
                  </span>
                </div>
              </div>

              <button type="submit" className="btn" style={{ alignSelf: "flex-start", marginTop: "8px" }}>
                💾 Save Reservation Policy
              </button>
            </form>
          )}
        </div>
      )}

      {/* TAB 4: INTER-DEPARTMENT RESOURCE SHARING (Requirement 8) */}
      {tab === "sharing" && (
        <div>
          <div className="card" style={{ marginBottom: "20px" }}>
            <h4>Request Available Resource (Cross-Department Sharing)</h4>
            <p style={{ color: "#64748b", margin: "6px 0 16px", fontSize: "0.875rem" }}>
              Identifiable free resources from other departments can be requested for extra classes or guest sessions.
            </p>
            <form onSubmit={handleRequestSharing} style={{ display: "flex", gap: "12px", flexWrap: "wrap", alignItems: "center" }}>
              <select value={reqResource} onChange={(e) => setReqResource(e.target.value)} style={{ padding: "8px", borderRadius: "6px", border: "1px solid #ccc" }}>
                {rooms.map((r) => <option key={r.name} value={r.name}>{r.name} ({r.type} - {r.department})</option>)}
              </select>
              <select value={reqDay} onChange={(e) => setReqDay(e.target.value)} style={{ padding: "8px", borderRadius: "6px", border: "1px solid #ccc" }}>
                {DAYS.map((d) => <option key={d} value={d}>{d}</option>)}
              </select>
              <select value={reqPeriod} onChange={(e) => setReqPeriod(e.target.value)} style={{ padding: "8px", borderRadius: "6px", border: "1px solid #ccc" }}>
                {PERIODS.map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
              <input
                placeholder="Reason (e.g. Extra Class, Guest Lecture)"
                value={reqReason}
                onChange={(e) => setReqReason(e.target.value)}
                style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #ccc", flex: 1, minWidth: "220px" }}
              />
              <button type="submit" className="btn">+ Submit Request</button>
            </form>
          </div>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Requested Resource</th>
                  <th>Day & Time Slot</th>
                  <th>Owner Dept</th>
                  <th>Requesting Dept</th>
                  <th>Reason</th>
                  <th>Status</th>
                  <th>Requested By</th>
                  <th>HOD Action</th>
                </tr>
              </thead>
              <tbody>
                {sharingRequests.map((req) => (
                  <tr key={req.id}>
                    <td><strong>{req.resource_name}</strong></td>
                    <td>{req.day} {req.period}</td>
                    <td>{req.owner_department}</td>
                    <td><strong>{req.requesting_department}</strong></td>
                    <td>{req.reason}</td>
                    <td>
                      <span className={`status-badge status-${req.status.toLowerCase()}`}>
                        {req.status}
                      </span>
                    </td>
                    <td>{req.requested_by}</td>
                    <td>
                      {req.status === "PENDING" && (currentRole === "HOD" || currentRole === "ADMIN") ? (
                        <div style={{ display: "flex", gap: "6px" }}>
                          <button
                            className="btn"
                            style={{ padding: "4px 8px", fontSize: "0.75rem", background: "#16a34a" }}
                            onClick={() => handleUpdateSharingStatus(req.id, "APPROVED")}
                          >
                            Approve
                          </button>
                          <button
                            className="btn btn-danger"
                            style={{ padding: "4px 8px", fontSize: "0.75rem" }}
                            onClick={() => handleUpdateSharingStatus(req.id, "REJECTED")}
                          >
                            Reject
                          </button>
                        </div>
                      ) : (
                        <span style={{ fontSize: "0.8rem", color: "#64748b" }}>{req.reviewed_by || "Reviewed"}</span>
                      )}
                    </td>
                  </tr>
                ))}
                {sharingRequests.length === 0 && (
                  <tr><td colSpan="8" style={{ textAlign: "center", color: "#64748b" }}>No resource sharing requests submitted.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================
// 6. MASTER TIMETABLE VIEW (Master + Multiple Filtered Views)
// =============================================================
// =============================================================
// 6. MASTER TIMETABLE VIEW (Matches Reference College Formats)
// =============================================================
function TimetableView({ department, currentRole, notify }) {
  const [timetable, setTimetable] = useState([]);
  const [timeSlots, setTimeSlots] = useState([]);
  const [timeSettings, setTimeSettings] = useState(null);
  const [divisions, setDivisions] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [faculty, setFaculty] = useState([]);
  const [rooms, setRooms] = useState([]);

  // View Modes: "MASTER", "DIVISION", "FACULTY", "CLASSROOM", "LAB", "BATCH"
  const [viewFilter, setViewFilter] = useState("MASTER");
  const [selectedDivision, setSelectedDivision] = useState("");
  const [selectedFaculty, setSelectedFaculty] = useState("");
  const [selectedRoom, setSelectedRoom] = useState("");
  const [selectedLab, setSelectedLab] = useState("");
  const [selectedBatch, setSelectedBatch] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadAll();
  }, [department]);

  const loadAll = async () => {
    try {
      const [ttData, slotsData, settingsData, divData, subData, facData, roomData] = await Promise.all([
        api.fetchTimetable(department),
        api.fetchTimeSlots(),
        api.fetchTimeSettings(),
        api.fetchDivisions(department),
        api.fetchSubjects(department),
        api.fetchFaculty(department),
        api.fetchRooms(department)
      ]);

      setTimetable(ttData || []);
      setTimeSlots(slotsData || []);
      setTimeSettings(settingsData);
      setDivisions(divData || []);
      setSubjects(subData || []);
      setFaculty(facData || []);
      setRooms(roomData || []);

      if (divData && divData.length > 0) {
        setSelectedDivision(divData[0].name);
      }
      if (facData && facData.length > 0) {
        setSelectedFaculty(facData[0].code);
      }
      const crs = (roomData || []).filter(r => (r.type || "").toLowerCase() !== "lab");
      const lbs = (roomData || []).filter(r => (r.type || "").toLowerCase() === "lab");
      if (crs.length > 0) setSelectedRoom(crs[0].name);
      else if (roomData && roomData.length > 0) setSelectedRoom(roomData[0].name);
      if (lbs.length > 0) setSelectedLab(lbs[0].name);

      const bts = Array.from(new Set((ttData || []).map(t => t.batch).filter(Boolean))).sort();
      if (bts.length > 0) setSelectedBatch(bts[0]);
    } catch (e) {
      console.error(e);
    }
  };

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const res = await api.generateTimetable({ department });
      if (res.success) {
        notify(res.message, "success");
        setTimetable(res.timetable);
        loadAll();
      } else {
        notify(res.message || "Scheduling dead-end reached.", "error");
      }
    } catch {
      notify("Scheduling execution failed", "error");
    } finally {
      setLoading(false);
    }
  };

  // Determine working days from settings or timetable or default
  const activeDays = (timeSettings && timeSettings.working_days && timeSettings.working_days.length > 0)
    ? timeSettings.working_days
    : ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

  // Sort slots by order_index and format labels to 12-hour AM/PM
  const orderedSlots = [...timeSlots]
    .sort((a, b) => (a.order_index || 0) - (b.order_index || 0))
    .map(s => ({
      ...s,
      displayPeriod: formatTime12Hour(s.period)
    }));

  // Build Course Legend for the currently viewed division
  const curDivObj = divisions.find(d => d.name === selectedDivision) || divisions[0];
  const divTimetableSessions = timetable.filter(t => t.section === (curDivObj?.name || selectedDivision));
  const distinctSubjectNames = Array.from(new Set(divTimetableSessions.map(t => t.subject)));

  const courseLegend = distinctSubjectNames.map((sName, idx) => {
    const subObj = subjects.find(s => s.name === sName);
    const subSessions = divTimetableSessions.filter(t => t.subject === sName);
    const facCodes = Array.from(new Set(subSessions.map(t => t.faculty_code)));
    const facNames = facCodes.map(fc => {
      const fObj = faculty.find(f => f.code === fc);
      return fObj ? `${fObj.name} (${fc})` : fc;
    }).join(", ");

    return {
      srNo: idx + 1,
      abbr: subObj?.code || sName.slice(0, 4).toUpperCase(),
      code: subObj?.code || `BTCSE03${idx + 1}`,
      title: sName,
      facultyName: facNames || "Department Faculty",
    };
  });

  const classrooms = rooms.filter(r => (r.type || "").toLowerCase() !== "lab");
  const labs = rooms.filter(r => (r.type || "").toLowerCase() === "lab");
  const allBatches = Array.from(new Set(timetable.map(t => t.batch).filter(Boolean))).sort();

  return (
    <div>
      {/* Top Filter and Action Bar */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px", flexWrap: "wrap", gap: "12px" }}>
        <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
          <button
            className={`filter-pill ${viewFilter === "MASTER" ? "active" : ""}`}
            onClick={() => setViewFilter("MASTER")}
          >
            🏛️ Master Timetable
          </button>
          <button
            className={`filter-pill ${viewFilter === "DIVISION" ? "active" : ""}`}
            onClick={() => setViewFilter("DIVISION")}
          >
            📋 Division-wise
          </button>
          <button
            className={`filter-pill ${viewFilter === "FACULTY" ? "active" : ""}`}
            onClick={() => setViewFilter("FACULTY")}
          >
            👨‍🏫 Faculty-wise
          </button>
          <button
            className={`filter-pill ${viewFilter === "CLASSROOM" ? "active" : ""}`}
            onClick={() => setViewFilter("CLASSROOM")}
          >
            🏫 Classroom-wise
          </button>
          <button
            className={`filter-pill ${viewFilter === "LAB" ? "active" : ""}`}
            onClick={() => setViewFilter("LAB")}
          >
            🔬 Lab-wise
          </button>
          <button
            className={`filter-pill ${viewFilter === "BATCH" ? "active" : ""}`}
            onClick={() => setViewFilter("BATCH")}
          >
            👥 Batch-wise
          </button>
        </div>

        <div style={{ display: "flex", gap: "10px", alignItems: "center", flexWrap: "wrap" }}>
          <button className="btn btn-secondary" onClick={() => window.print()}>
            🖨️ Print / Save PDF
          </button>
          {viewFilter === "DIVISION" && (
            <a
              href={api.getExportTimetableUrl(department, selectedDivision)}
              className="btn btn-secondary"
              target="_blank"
              rel="noreferrer"
              style={{ fontWeight: 600, background: "#1e40af", color: "#fff" }}
            >
              📥 Export {selectedDivision} (Excel)
            </a>
          )}
          <a
            href={api.getExportTimetableUrl(department)}
            className="btn btn-secondary"
            target="_blank"
            rel="noreferrer"
            title="Download complete multi-sheet workbook with all divisions"
          >
            📑 All Divisions Excel
          </a>
          <button className="btn" onClick={handleGenerate} disabled={loading}>
            {loading ? "⚙️ Running CSP + MRV..." : "🚀 Generate Timetable"}
          </button>
        </div>
      </div>

      {/* Sub-selector depending on view mode */}
      {viewFilter === "DIVISION" && (
        <div style={{ background: "#fff", padding: "10px 16px", borderRadius: "8px", border: "1px solid #e2e8f0", marginBottom: "16px", display: "flex", alignItems: "center", gap: "10px" }}>
          <label style={{ fontSize: "0.85rem", fontWeight: "700" }}>Select Division / Class:</label>
          <select
            value={selectedDivision}
            onChange={(e) => setSelectedDivision(e.target.value)}
            style={{ padding: "6px 12px", borderRadius: "6px", border: "1px solid #ccc", fontWeight: "600" }}
          >
            {divisions.map((d) => (
              <option key={d.name} value={d.name}>
                {d.name} ({d.year || "Second Year"} - {d.department_code || department})
              </option>
            ))}
          </select>
        </div>
      )}

      {viewFilter === "FACULTY" && (
        <div style={{ background: "#fff", padding: "10px 16px", borderRadius: "8px", border: "1px solid #e2e8f0", marginBottom: "16px", display: "flex", alignItems: "center", gap: "10px" }}>
          <label style={{ fontSize: "0.85rem", fontWeight: "700" }}>Select Faculty Member:</label>
          <select
            value={selectedFaculty}
            onChange={(e) => setSelectedFaculty(e.target.value)}
            style={{ padding: "6px 12px", borderRadius: "6px", border: "1px solid #ccc", fontWeight: "600" }}
          >
            {faculty.map((f) => (
              <option key={f.code} value={f.code}>
                {f.name} ({f.code}) - {f.designation}
              </option>
            ))}
          </select>
        </div>
      )}

      {viewFilter === "CLASSROOM" && (
        <div style={{ background: "#fff", padding: "10px 16px", borderRadius: "8px", border: "1px solid #e2e8f0", marginBottom: "16px", display: "flex", alignItems: "center", gap: "10px" }}>
          <label style={{ fontSize: "0.85rem", fontWeight: "700" }}>Select Classroom:</label>
          <select
            value={selectedRoom}
            onChange={(e) => setSelectedRoom(e.target.value)}
            style={{ padding: "6px 12px", borderRadius: "6px", border: "1px solid #ccc", fontWeight: "600" }}
          >
            {classrooms.map((r) => (
              <option key={r.name} value={r.name}>
                {r.name} (Cap: {r.capacity})
              </option>
            ))}
            {classrooms.length === 0 && rooms.map((r) => (
              <option key={r.name} value={r.name}>{r.name}</option>
            ))}
          </select>
        </div>
      )}

      {viewFilter === "LAB" && (
        <div style={{ background: "#fff", padding: "10px 16px", borderRadius: "8px", border: "1px solid #e2e8f0", marginBottom: "16px", display: "flex", alignItems: "center", gap: "10px" }}>
          <label style={{ fontSize: "0.85rem", fontWeight: "700" }}>Select Laboratory:</label>
          <select
            value={selectedLab}
            onChange={(e) => setSelectedLab(e.target.value)}
            style={{ padding: "6px 12px", borderRadius: "6px", border: "1px solid #ccc", fontWeight: "600" }}
          >
            {labs.map((r) => (
              <option key={r.name} value={r.name}>
                {r.name} (Cap: {r.capacity} | {r.equipment || "Equipment"})
              </option>
            ))}
            {labs.length === 0 && <option value="">No Labs Configured</option>}
          </select>
        </div>
      )}

      {viewFilter === "BATCH" && (
        <div style={{ background: "#fff", padding: "10px 16px", borderRadius: "8px", border: "1px solid #e2e8f0", marginBottom: "16px", display: "flex", alignItems: "center", gap: "10px" }}>
          <label style={{ fontSize: "0.85rem", fontWeight: "700" }}>Select Practical Batch:</label>
          <select
            value={selectedBatch}
            onChange={(e) => setSelectedBatch(e.target.value)}
            style={{ padding: "6px 12px", borderRadius: "6px", border: "1px solid #ccc", fontWeight: "600" }}
          >
            {allBatches.map((b) => (
              <option key={b} value={b}>Batch {b}</option>
            ))}
            {allBatches.length === 0 && <option value="">No Batches Scheduled Yet</option>}
          </select>
        </div>
      )}

      {/* VIEW 1: MASTER TIMETABLE (All Classes & Years) */}
      {viewFilter === "MASTER" && (
        <div className="college-container">
          <div className="college-header">
            <h2>MASTER TIME TABLE (ACADEMIC YEAR 2026 - 2027)</h2>
            <h3>Department of {department === "CSE" ? "Computer Science and Engineering" : department}</h3>
            <div className="academic-year-tag">All Academic Classes, Years & Divisions</div>
          </div>

          <div className="college-table-wrapper">
            <table className="college-table">
              <thead>
                <tr>
                  <th style={{ width: "65px" }}>Time / Day</th>
                  <th style={{ width: "110px" }}>Class / Div</th>
                  {orderedSlots.map((slot, idx) => (
                    <th key={idx} style={{ minWidth: slot.type === "TEACHING" ? "110px" : "42px" }}>
                      <div style={{ fontWeight: 700, fontSize: "0.85rem", whiteSpace: "nowrap" }}>
                        {slot.period}
                      </div>
                      <div style={{ fontSize: "0.75rem", opacity: 0.85, fontWeight: 500 }}>
                        {slot.displayPeriod}
                      </div>
                      <span className="th-period-time">
                        {slot.type === "LUNCH" ? "LUNCH" : slot.type === "SHORT_BREAK" ? "BREAK" : "LECTURE"}
                      </span>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {activeDays.map((day) => {
                  const dayDivisions = divisions.length > 0 ? divisions : [{ name: "Division A", year: "Second Year" }];

                  return dayDivisions.map((div, divIdx) => {
                    return (
                      <tr key={`${day}-${div.name}`}>
                        {divIdx === 0 && (
                          <td rowSpan={dayDivisions.length} className="cell-day">
                            {day.toUpperCase().slice(0, 3)}
                          </td>
                        )}
                        <td className="cell-class">
                          <strong>{div.year ? div.year.split(" ")[0].slice(0, 2).toUpperCase() : "SY"}</strong>
                          <div style={{ fontSize: "0.75rem", color: "#64748b" }}>{div.name}</div>
                        </td>

                        {orderedSlots.map((slot, slotIdx) => {
                          if (slot.type === "SHORT_BREAK" || slot.type === "LUNCH") {
                            if (divIdx === 0) {
                              return (
                                <td
                                  key={slotIdx}
                                  rowSpan={dayDivisions.length}
                                  className="break-col"
                                >
                                  {slot.type === "LUNCH" ? "L U N C H   B R E A K" : "S H O R T   B R E A K"}
                                </td>
                              );
                            }
                            return null;
                          }

                          // Teaching slot sessions for this day, slot, and division
                          const slotSessions = timetable.filter(
                            (t) => t.day === day && (t.period === slot.period || formatTime12Hour(t.period) === slot.displayPeriod) && t.section === div.name
                          );

                          if (!slotSessions || slotSessions.length === 0) {
                            return <td key={slotIdx} style={{ color: "#cbd5e1" }}>-</td>;
                          }

                          // If batch lab sessions
                          if (slotSessions[0].is_lab) {
                            return (
                              <td key={slotIdx} style={{ padding: 0 }}>
                                <div className="cell-lab-container">
                                  {slotSessions.map((ls, bIdx) => (
                                    <div key={bIdx} className="cell-lab-batch">
                                      <span className="batch-tag">{ls.batch || `B${bIdx + 1}`}</span>
                                      <span className="course-tag">{ls.subject}</span>
                                      <span className="fac-tag">{ls.faculty_code}</span>
                                      <span className="room-tag">{ls.room}</span>
                                    </div>
                                  ))}
                                </div>
                              </td>
                            );
                          }

                          // Regular theory lecture
                          const s = slotSessions[0];
                          return (
                            <td key={slotIdx}>
                              <div className="cell-lecture">
                                <div className="course-code">{s.subject}</div>
                                <div className="fac-code">{s.faculty_code}</div>
                                <div className="room-tag">{s.room}</div>
                              </div>
                            </td>
                          );
                        })}
                      </tr>
                    );
                  });
                })}
              </tbody>
            </table>
          </div>

          <div className="college-signatures">
            <div className="sig-box"><div className="sig-line">HoD</div></div>
            <div className="sig-box"><div className="sig-line">Dean</div></div>
            <div className="sig-box"><div className="sig-line">Dean, Academics</div></div>
          </div>
        </div>
      )}

      {/* VIEW 2: DIVISION / CLASS TIMETABLE (Official Format with Legend) */}
      {viewFilter === "DIVISION" && (
        <div className="college-container">
          <div className="college-header">
            <h2>CLASS TIME TABLE (ACADEMIC YEAR 2026 - 2027)</h2>
            <h3>Department of {department === "CSE" ? "Computer Science and Engineering" : department}</h3>
            <div className="academic-year-tag">{curDivObj?.year || "Second Year"} - {selectedDivision} (Semester III)</div>
          </div>

          {/* Metadata Banner Box */}
          <div className="college-meta-grid">
            <div><strong>Department:</strong> {department === "CSE" ? "Computer Science & Engineering" : department}</div>
            <div><strong>Academic Year:</strong> 2026-27</div>
            <div><strong>Class / Div:</strong> {curDivObj?.year || "Second Year"} - {selectedDivision} (Sem III)</div>
            <div><strong>Semester:</strong> Semester III</div>
            <div><strong>HoD:</strong> Mr. Naresh A. Kamble</div>
            <div><strong>Status:</strong> Approved Official Schedule</div>
          </div>

          <div className="college-table-wrapper">
            <table className="college-table">
              <thead>
                <tr>
                  <th style={{ width: "80px" }}>Time/Day</th>
                  <th style={{ width: "60px" }}>Class</th>
                  {orderedSlots.map((slot, idx) => (
                    <th key={idx} style={{ minWidth: slot.type === "TEACHING" ? "105px" : "42px" }}>
                      <div style={{ fontWeight: 700, fontSize: "0.85rem", whiteSpace: "nowrap" }}>
                        {slot.period}
                      </div>
                      <div style={{ fontSize: "0.75rem", opacity: 0.85, fontWeight: 500 }}>
                        {slot.displayPeriod}
                      </div>
                      <span className="th-period-time">
                        {slot.type === "LUNCH" ? "LUNCH" : slot.type === "SHORT_BREAK" ? "BREAK" : ""}
                      </span>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {activeDays.map((day) => (
                  <tr key={day}>
                    <td className="cell-day">{day.toUpperCase().slice(0, 3)}</td>
                    <td className="cell-class">
                      {curDivObj?.year ? curDivObj.year.split(" ")[0].slice(0, 2).toUpperCase() : "SY"}
                    </td>

                    {orderedSlots.map((slot, slotIdx) => {
                      if (slot.type === "SHORT_BREAK" || slot.type === "LUNCH") {
                        return (
                          <td key={slotIdx} className="break-col">
                            {slot.type === "LUNCH" ? "LUNCH" : "BREAK"}
                          </td>
                        );
                      }

                      const slotSessions = timetable.filter(
                        (t) => t.day === day && (t.period === slot.period || formatTime12Hour(t.period) === slot.displayPeriod) && t.section === selectedDivision
                      );

                      if (!slotSessions || slotSessions.length === 0) {
                        return <td key={slotIdx} style={{ color: "#cbd5e1" }}>-</td>;
                      }

                      if (slotSessions[0].is_lab) {
                        return (
                          <td key={slotIdx} style={{ padding: 0 }}>
                            <div className="cell-lab-container">
                              {slotSessions.map((ls, bIdx) => (
                                <div key={bIdx} className="cell-lab-batch">
                                  <span className="batch-tag">{ls.batch || `B${bIdx + 1}`}</span>
                                  <span className="course-tag">{ls.subject}</span>
                                  <span className="fac-tag">{ls.faculty_code}</span>
                                  <span className="room-tag">{ls.room}</span>
                                </div>
                              ))}
                            </div>
                          </td>
                        );
                      }

                      const s = slotSessions[0];
                      return (
                        <td key={slotIdx}>
                          <div className="cell-lecture">
                            <div className="course-code">{s.subject}</div>
                            <div className="fac-code">{s.faculty_code}</div>
                            <div className="room-tag">{s.room}</div>
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Course Abbreviation & Faculty Legend Table */}
          <div style={{ marginTop: "24px" }}>
            <h4 style={{ marginBottom: "10px", fontSize: "0.9rem", color: "#1e293b" }}>
              📖 Course Abbreviations & Qualified Faculty Code Legend:
            </h4>
            <div className="table-container" style={{ margin: 0 }}>
              <table style={{ fontSize: "0.85rem" }}>
                <thead>
                  <tr style={{ background: "#f8fafc" }}>
                    <th style={{ width: "60px" }}>Sr. No</th>
                    <th style={{ width: "160px" }}>Course Abbreviation</th>
                    <th style={{ width: "140px" }}>Course Code</th>
                    <th>Course Title</th>
                    <th>Assigned Faculty Name & Code</th>
                  </tr>
                </thead>
                <tbody>
                  {courseLegend.map((c) => (
                    <tr key={c.srNo}>
                      <td>{c.srNo}</td>
                      <td><strong style={{ color: "#1e40af" }}>{c.abbr}</strong></td>
                      <td>{c.code}</td>
                      <td><strong>{c.title}</strong></td>
                      <td>{c.facultyName}</td>
                    </tr>
                  ))}
                  {courseLegend.length === 0 && (
                    <tr>
                      <td colSpan="5" style={{ textAlign: "center", color: "#64748b" }}>
                        No sessions scheduled yet. Click "Generate Timetable" to populate schedule.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            <div style={{ marginTop: "12px", fontSize: "0.82rem", color: "#475569" }}>
              <strong>Class Coordinator:</strong> Ms. Rutuja R. Dakare (Contact: 9156418849)
            </div>
          </div>

          <div className="college-signatures">
            <div className="sig-box"><div className="sig-line">HoD</div></div>
            <div className="sig-box"><div className="sig-line">Dean</div></div>
            <div className="sig-box"><div className="sig-line">Dean, Academics</div></div>
          </div>
        </div>
      )}

      {/* VIEW 3: FACULTY-WISE TIMETABLE */}
      {viewFilter === "FACULTY" && (
        <div className="college-container">
          <div className="college-header">
            <h2>Individual Faculty Teaching Schedule</h2>
            <h3>
              {faculty.find((f) => f.code === selectedFaculty)?.name || selectedFaculty} (Code: {selectedFaculty})
            </h3>
            <div className="academic-year-tag">Department of {department} | Academic Year 2026 - 2027</div>
          </div>

          <div className="college-table-wrapper">
            <table className="college-table">
              <thead>
                <tr>
                  <th style={{ width: "90px" }}>Day</th>
                  {orderedSlots.map((slot, idx) => (
                    <th key={idx} style={{ minWidth: slot.type === "TEACHING" ? "110px" : "36px" }}>
                      {slot.displayPeriod}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {activeDays.map((day) => (
                  <tr key={day}>
                    <td className="cell-day">{day}</td>
                    {orderedSlots.map((slot, sIdx) => {
                      if (slot.type !== "TEACHING") {
                        return <td key={sIdx} className="break-col">{slot.type === "LUNCH" ? "LUNCH" : "BREAK"}</td>;
                      }

                      const facSessions = timetable.filter(
                        (t) => t.day === day && (t.period === slot.period || formatTime12Hour(t.period) === slot.displayPeriod) && t.faculty_code === selectedFaculty
                      );

                      if (facSessions.length === 0) {
                        return <td key={sIdx} style={{ color: "#cbd5e1" }}>-</td>;
                      }

                      const s = facSessions[0];
                      return (
                        <td key={sIdx}>
                          <div className="cell-lecture">
                            <div className="course-code">{s.subject}</div>
                            <div className="fac-code">{s.section} {s.batch ? `(${s.batch})` : ""}</div>
                            <div className="room-tag">📍 {s.room}</div>
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* VIEW 4: CLASSROOM-WISE TIMETABLE */}
      {viewFilter === "CLASSROOM" && (
        <div className="college-container">
          <div className="college-header">
            <h2>Classroom Occupancy Schedule: {selectedRoom}</h2>
            <h3>
              Classroom Capacity: {rooms.find((r) => r.name === selectedRoom)?.capacity || 60} seats
            </h3>
            <div className="academic-year-tag">Department of {department} | Academic Year 2026 - 2027</div>
          </div>

          <div className="college-table-wrapper">
            <table className="college-table">
              <thead>
                <tr>
                  <th style={{ width: "90px" }}>Day</th>
                  {orderedSlots.map((slot, idx) => (
                    <th key={idx} style={{ minWidth: slot.type === "TEACHING" ? "110px" : "36px" }}>
                      {slot.displayPeriod}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {activeDays.map((day) => (
                  <tr key={day}>
                    <td className="cell-day">{day}</td>
                    {orderedSlots.map((slot, sIdx) => {
                      if (slot.type !== "TEACHING") {
                        return <td key={sIdx} className="break-col">{slot.type === "LUNCH" ? "LUNCH" : "BREAK"}</td>;
                      }

                      const roomSessions = timetable.filter(
                        (t) => t.day === day && (t.period === slot.period || formatTime12Hour(t.period) === slot.displayPeriod) && t.room === selectedRoom
                      );

                      if (roomSessions.length === 0) {
                        return <td key={sIdx} style={{ color: "#10b981", fontWeight: "600" }}>✓ Free</td>;
                      }

                      const s = roomSessions[0];
                      return (
                        <td key={sIdx} style={{ background: "#eff6ff" }}>
                          <div className="cell-lecture">
                            <div className="course-code">{s.subject}</div>
                            <div className="fac-code">{s.section}</div>
                            <div className="room-tag">👨‍🏫 {s.faculty_code}</div>
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* VIEW 5: LAB-WISE TIMETABLE */}
      {viewFilter === "LAB" && (
        <div className="college-container">
          <div className="college-header">
            <h2>Laboratory Occupancy Schedule: {selectedLab}</h2>
            <h3>
              Lab Capacity: {rooms.find((r) => r.name === selectedLab)?.capacity || 30} | {rooms.find((r) => r.name === selectedLab)?.equipment || "Computer Lab"}
            </h3>
            <div className="academic-year-tag">Department of {department} | Academic Year 2026 - 2027</div>
          </div>

          <div className="college-table-wrapper">
            <table className="college-table">
              <thead>
                <tr>
                  <th style={{ width: "90px" }}>Day</th>
                  {orderedSlots.map((slot, idx) => (
                    <th key={idx} style={{ minWidth: slot.type === "TEACHING" ? "110px" : "36px" }}>
                      {slot.displayPeriod}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {activeDays.map((day) => (
                  <tr key={day}>
                    <td className="cell-day">{day}</td>
                    {orderedSlots.map((slot, sIdx) => {
                      if (slot.type !== "TEACHING") {
                        return <td key={sIdx} className="break-col">{slot.type === "LUNCH" ? "LUNCH" : "BREAK"}</td>;
                      }

                      const labSessions = timetable.filter(
                        (t) => t.day === day && (t.period === slot.period || formatTime12Hour(t.period) === slot.displayPeriod) && t.room === selectedLab
                      );

                      if (labSessions.length === 0) {
                        return <td key={sIdx} style={{ color: "#10b981", fontWeight: "600" }}>✓ Free</td>;
                      }

                      const s = labSessions[0];
                      return (
                        <td key={sIdx} style={{ background: "#f0fdf4" }}>
                          <div className="cell-lecture">
                            <div className="course-code">{s.subject}</div>
                            <div className="fac-code">{s.section} ({s.batch || "Lab"})</div>
                            <div className="room-tag">👨‍🏫 {s.faculty_code}</div>
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* VIEW 6: BATCH-WISE TIMETABLE */}
      {viewFilter === "BATCH" && (
        <div className="college-container">
          <div className="college-header">
            <h2>Practical Batch Timetable: Batch {selectedBatch}</h2>
            <h3>Department of {department === "CSE" ? "Computer Science and Engineering" : department}</h3>
            <div className="academic-year-tag">Academic Year 2026 - 2027</div>
          </div>

          <div className="college-table-wrapper">
            <table className="college-table">
              <thead>
                <tr>
                  <th style={{ width: "90px" }}>Day</th>
                  {orderedSlots.map((slot, idx) => (
                    <th key={idx} style={{ minWidth: slot.type === "TEACHING" ? "110px" : "36px" }}>
                      {slot.displayPeriod}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {activeDays.map((day) => (
                  <tr key={day}>
                    <td className="cell-day">{day}</td>
                    {orderedSlots.map((slot, sIdx) => {
                      if (slot.type !== "TEACHING") {
                        return <td key={sIdx} className="break-col">{slot.type === "LUNCH" ? "LUNCH" : "BREAK"}</td>;
                      }

                      const batchSessions = timetable.filter(
                        (t) => t.day === day && (t.period === slot.period || formatTime12Hour(t.period) === slot.displayPeriod) &&
                        (t.batch === selectedBatch || (!t.batch && selectedBatch && t.section === selectedDivision))
                      );

                      if (batchSessions.length === 0) {
                        return <td key={sIdx} style={{ color: "#cbd5e1" }}>-</td>;
                      }

                      const s = batchSessions[0];
                      return (
                        <td key={sIdx}>
                          <div className="cell-lecture">
                            <div className="course-code">{s.subject}</div>
                            <div className="fac-code">{s.faculty_code}</div>
                            <div className="room-tag">📍 {s.room}</div>
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================
// 7. CONFLICTS VIEW (Conflict Detection & Clash Resolution History)
// =============================================================
function ConflictsView({ department }) {
  const [conflicts, setConflicts] = useState([]);
  const [clashHistory, setClashHistory] = useState([]);
  const [counts, setCounts] = useState({ detected: 0, resolved: 0, unresolved: 0 });
  const [activeTab, setActiveTab] = useState("ALL");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadConflicts();
  }, [department]);

  const loadConflicts = async () => {
    setLoading(true);
    try {
      const res = await api.fetchConflicts(department);
      const history = res.clash_history || [];
      setConflicts(res.conflicts || []);
      setClashHistory(history);

      const det = res.detected_clashes || history.length;
      const resCount = res.resolved_clashes || history.filter((c) => c.status === "Resolved").length;
      const unres = res.unresolved_clashes || (res.conflicts ? res.conflicts.length : 0);
      setCounts({ detected: det, resolved: resCount, unresolved: unres });
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const filteredHistory = clashHistory.filter((c) => {
    if (activeTab === "RESOLVED") return c.status === "Resolved";
    if (activeTab === "DETECTED") return c.status === "Detected";
    if (activeTab === "UNRESOLVED") return c.status === "Unresolved";
    return true;
  });

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <div>
          <h2>Conflict Detection & Clash Resolution History</h2>
          <p style={{ color: "#64748b", marginTop: "4px" }}>
            Real-time audit log of scheduling clashes detected by CSP and automatically resolved during backtracking search.
          </p>
        </div>
        <button className="btn btn-secondary" onClick={loadConflicts} disabled={loading}>
          {loading ? "Refreshing..." : "🔄 Refresh Conflicts"}
        </button>
      </div>

      {/* 3 Metric Cards */}
      <div className="grid-cards" style={{ marginBottom: "20px" }}>
        <div className="card" style={{ borderTop: "3px solid #3b82f6" }}>
          <div className="card-title">Detected Clashes</div>
          <div className="card-value" style={{ color: "#2563eb" }}>{counts.detected}</div>
          <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "4px" }}>Total Constraint Collisions Encountered</div>
        </div>

        <div className="card" style={{ borderTop: "3px solid #10b981" }}>
          <div className="card-title">Resolved Clashes</div>
          <div className="card-value" style={{ color: "#10b981" }}>{counts.resolved}</div>
          <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "4px" }}>Resolved via CSP Backtracking & Alternate Slots</div>
        </div>

        <div className="card" style={{ borderTop: "3px solid #ef4444" }}>
          <div className="card-title">Unresolved Clashes</div>
          <div className="card-value" style={{ color: counts.unresolved > 0 ? "#ef4444" : "#10b981" }}>{counts.unresolved}</div>
          <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "4px" }}>
            {counts.unresolved === 0 ? "✓ Zero Clash-Free State" : "Bottlenecks Requiring Attention"}
          </div>
        </div>
      </div>

      {/* Infeasibility Diagnostics Warning Box (if any) */}
      {conflicts.length > 0 && (
        <div className="card" style={{ background: "#fef2f2", border: "1px solid #fecaca", marginBottom: "20px" }}>
          <h4 style={{ color: "#b91c1c", marginBottom: "8px" }}>⚠️ Active Constraint Diagnostics:</h4>
          <ul style={{ paddingLeft: "20px", color: "#991b1b", fontSize: "0.9rem", display: "flex", flexDirection: "column", gap: "6px" }}>
            {conflicts.map((c, i) => (
              <li key={i}>{c}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Clash Resolution History Section */}
      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px", flexWrap: "wrap", gap: "10px" }}>
          <div>
            <h3>Clash Resolution History Log</h3>
            <p style={{ color: "#64748b", fontSize: "0.85rem", marginTop: "2px" }}>
              Displays when a collision occurred (faculty clash, room clash, division clash) and how it was resolved.
            </p>
          </div>

          <div style={{ display: "flex", gap: "8px" }}>
            <button className={`subtab-btn ${activeTab === "ALL" ? "active" : ""}`} onClick={() => setActiveTab("ALL")}>
              All Clashes ({clashHistory.length})
            </button>
            <button className={`subtab-btn ${activeTab === "RESOLVED" ? "active" : ""}`} onClick={() => setActiveTab("RESOLVED")}>
              Resolved ({counts.resolved})
            </button>
            <button className={`subtab-btn ${activeTab === "DETECTED" ? "active" : ""}`} onClick={() => setActiveTab("DETECTED")}>
              Detected ({counts.detected - counts.resolved})
            </button>
            <button className={`subtab-btn ${activeTab === "UNRESOLVED" ? "active" : ""}`} onClick={() => setActiveTab("UNRESOLVED")}>
              Unresolved ({counts.unresolved})
            </button>
          </div>
        </div>

        {filteredHistory.length === 0 ? (
          <div style={{ padding: "32px", textAlign: "center", color: "#166534", background: "#f0fdf4", borderRadius: "8px" }}>
            <div style={{ fontSize: "1.1rem", fontWeight: "700" }}>✓ No Clashes in this Filter View</div>
            <div style={{ fontSize: "0.85rem", color: "#15803d", marginTop: "4px" }}>
              The scheduler found optimal clash-free assignments for all session requirements.
            </div>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th style={{ width: "70px" }}>Log ID</th>
                  <th>Clash Type</th>
                  <th>Time Slot</th>
                  <th>Affected Faculty</th>
                  <th>Division / Resource</th>
                  <th>Issue Details</th>
                  <th>Status</th>
                  <th>Resolution Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredHistory.slice(0, 100).map((item, idx) => (
                  <tr key={idx}>
                    <td><strong>{item.id || `#${101 + idx}`}</strong></td>
                    <td>
                      <span className="badge" style={{
                        background: item.type?.includes("Faculty") ? "#dbeafe" : item.type?.includes("Room") ? "#fef3c7" : "#e0e7ff",
                        color: item.type?.includes("Faculty") ? "#1e40af" : item.type?.includes("Room") ? "#92400e" : "#3730a3"
                      }}>
                        {item.type}
                      </span>
                    </td>
                    <td><strong>{formatTime12Hour(item.time)}</strong></td>
                    <td>{item.faculty || item.entity || "-"}</td>
                    <td>{item.division ? `Div ${item.division}` : ""} {item.resource ? `(${item.resource})` : ""}</td>
                    <td style={{ fontSize: "0.85rem", color: "#475569" }}>{item.issue}</td>
                    <td>
                      {item.status === "Resolved" ? (
                        <span className="badge badge-success">✓ Resolved</span>
                      ) : item.status === "Detected" ? (
                        <span className="badge" style={{ background: "#dbeafe", color: "#1e40af" }}>🔍 Detected</span>
                      ) : (
                        <span className="badge badge-danger">❌ Unresolved</span>
                      )}
                    </td>
                    <td style={{ fontSize: "0.85rem", fontWeight: "600", color: item.status === "Resolved" ? "#15803d" : "#b91c1c" }}>
                      {item.resolution}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

// =============================================================
// 8. IMPORT DATA VIEW (2-Step Validation & Single-Sheet Template)
// =============================================================
function ImportView({ notify, onSuccess }) {
  const [file, setFile] = useState(null);
  const [validating, setValidating] = useState(false);
  const [importing, setImporting] = useState(false);
  const [validationResult, setValidationResult] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0] || null);
    setValidationResult(null);
  };

  const handleValidate = async () => {
    if (!file) {
      notify("Please select an Excel (.xlsx) file first", "error");
      return;
    }
    setValidating(true);
    try {
      const res = await api.validateExcelFile(file);
      setValidationResult(res);
      if (res.valid) {
        notify("File validated successfully! Review summary below.", "success");
      } else {
        notify("Validation errors found. Please review the report.", "error");
      }
    } catch (err) {
      notify("Validation request failed: " + err.message, "error");
    } finally {
      setValidating(false);
    }
  };

  const handleImport = async () => {
    if (!file) {
      notify("Please select an Excel (.xlsx) file first", "error");
      return;
    }
    setImporting(true);
    try {
      const res = await api.uploadExcelFile(file);
      if (res.success) {
        notify("Excel data successfully imported and synced with database!", "success");
        onSuccess();
      } else {
        const errorList = res.errors || (res.error ? [res.error] : ["Import failed"]);
        notify(errorList[0] || "Import failed", "error");
      }
    } catch (err) {
      notify("Import error: " + err.message, "error");
    } finally {
      setImporting(false);
    }
  };

  const s = validationResult?.summary || {};

  return (
    <div style={{ maxWidth: "800px", margin: "0 auto" }}>
      {/* Top Header Card with Download Sample Button */}
      <div className="card" style={{ marginBottom: "20px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "14px" }}>
          <div>
            <h2>📥 Import Academic Data (Single-Sheet Template)</h2>
            <p style={{ color: "#64748b", marginTop: "4px", fontSize: "0.9rem" }}>
              Upload the human-friendly <code>CLASHFREE_INPUT</code> Excel template containing Teaching Requirements, Resource Configuration, and Time Configuration.
            </p>
          </div>
          <a
            href={api.getDownloadTemplateUrl()}
            download="CLASHFREE_Input_Template.xlsx"
            className="btn btn-secondary"
            style={{ textDecoration: "none", display: "inline-flex", alignItems: "center", gap: "8px", fontWeight: "600" }}
          >
            📥 Download Sample Excel Template
          </a>
        </div>
      </div>

      {/* 2-Step Import Workflow Card */}
      <div className="card" style={{ marginBottom: "20px", padding: "28px" }}>
        <h3 style={{ marginBottom: "16px" }}>Select Excel File</h3>

        <div style={{ border: "2px dashed #cbd5e1", borderRadius: "8px", padding: "24px", textAlign: "center", background: "#f8fafc" }}>
          <input
            type="file"
            accept=".xlsx"
            onChange={handleFileChange}
            id="excel-file-input"
            style={{ display: "none" }}
          />
          <label htmlFor="excel-file-input" className="btn btn-secondary" style={{ cursor: "pointer", display: "inline-block" }}>
            📂 Choose .xlsx File
          </label>
          <div style={{ marginTop: "10px", fontSize: "0.9rem", color: file ? "#0f172a" : "#94a3b8", fontWeight: file ? "600" : "400" }}>
            {file ? `Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)` : "No file chosen yet"}
          </div>
        </div>

        {/* 2 Step Buttons */}
        <div style={{ display: "flex", gap: "12px", marginTop: "24px", justifyContent: "center" }}>
          <button
            type="button"
            className="btn"
            onClick={handleValidate}
            disabled={!file || validating}
            style={{ background: "#0f766e", minWidth: "160px" }}
          >
            {validating ? "Validating..." : "🔍 Step 1: Validate"}
          </button>

          <button
            type="button"
            className="btn"
            onClick={handleImport}
            disabled={!file || !validationResult?.valid || importing}
            style={{
              background: validationResult?.valid ? "#2563eb" : "#94a3b8",
              cursor: validationResult?.valid ? "pointer" : "not-allowed",
              minWidth: "180px"
            }}
          >
            {importing ? "Importing to Database..." : "🚀 Step 2: Import to Database"}
          </button>
        </div>
      </div>

      {/* Validation Summary Card */}
      {validationResult && (
        <div className="card" style={{ borderLeft: validationResult.valid ? "4px solid #10b981" : "4px solid #ef4444" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
            <h4>
              {validationResult.valid ? (
                <span style={{ color: "#166534" }}>✅ File Validated Successfully</span>
              ) : (
                <span style={{ color: "#b91c1c" }}>❌ Validation Failed</span>
              )}
            </h4>
            <span className={`badge ${validationResult.valid ? "badge-success" : "badge-danger"}`}>
              {validationResult.valid ? "0 Errors Found" : `${validationResult.errors?.length || 0} Error(s)`}
            </span>
          </div>

          {/* Counts Checklist */}
          {validationResult.valid && (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", margin: "16px 0", fontSize: "0.9rem", color: "#334155" }}>
              <div>✓ <strong>{s.teaching_requirements_count || 0}</strong> teaching requirements found</div>
              <div>✓ <strong>{s.faculty_count || 0}</strong> faculty records found</div>
              <div>✓ <strong>{s.subjects_count || 0}</strong> subjects found</div>
              <div>✓ <strong>{s.divisions_count || 0}</strong> divisions found</div>
              <div>✓ <strong>{s.classrooms_count || 0}</strong> classrooms configured</div>
              <div>✓ <strong>{s.labs_count || 0}</strong> labs configured</div>
              <div>✓ <strong>{s.teaching_slots_count || 0}</strong> teaching slots per week</div>
              <div>✓ <strong>{s.total_slots_count || 0}</strong> total time slots found</div>
            </div>
          )}

          {/* Errors Box */}
          {validationResult.errors && validationResult.errors.length > 0 && (
            <div style={{ marginTop: "16px", background: "#fef2f2", padding: "14px", borderRadius: "6px", border: "1px solid #fecaca" }}>
              <div style={{ color: "#991b1b", fontWeight: "700", marginBottom: "6px" }}>Errors:</div>
              <ul style={{ paddingLeft: "20px", color: "#b91c1c", fontSize: "0.85rem", display: "flex", flexDirection: "column", gap: "4px" }}>
                {validationResult.errors.map((err, i) => (
                  <li key={i}>{err}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Warnings Box */}
          {validationResult.warnings && validationResult.warnings.length > 0 && (
            <div style={{ marginTop: "16px", background: "#fffbeb", padding: "14px", borderRadius: "6px", border: "1px solid #fde68a" }}>
              <div style={{ color: "#92400e", fontWeight: "700", marginBottom: "6px" }}>Warnings:</div>
              <ul style={{ paddingLeft: "20px", color: "#b45309", fontSize: "0.85rem", display: "flex", flexDirection: "column", gap: "4px" }}>
                {validationResult.warnings.map((w, i) => (
                  <li key={i}>{w}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// =============================================================
// 9. ROOMS VIEW (Separate Classrooms & Labs)
// =============================================================
function RoomsView({ department, notify }) {
  const [rooms, setRooms] = useState([]);
  const [tab, setTab] = useState("CLASSROOM"); // "CLASSROOM" or "LAB"
  const [timetable, setTimetable] = useState([]);

  useEffect(() => {
    loadRooms();
  }, [department]);

  const loadRooms = async () => {
    const [rData, tData] = await Promise.all([
      api.fetchRooms(department),
      api.fetchTimetable(department)
    ]);
    setRooms(rData || []);
    setTimetable(tData || []);
  };

  const activeRooms = rooms.filter((r) => r.is_active !== false);
  const displayedRooms = activeRooms.filter((r) =>
    tab === "CLASSROOM" ? r.type === "Classroom" : r.type === "Lab"
  );

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <div>
          <h2>Academic Resources & Facilities</h2>
          <p style={{ color: "#64748b", marginTop: "4px" }}>
            Separate management of Classrooms and Specialized Laboratories with dynamic capacity and equipment matching.
          </p>
        </div>
        <div style={{ display: "flex", gap: "10px" }}>
          <button className={`subtab-btn ${tab === "CLASSROOM" ? "active" : ""}`} onClick={() => setTab("CLASSROOM")}>
            🏫 Classrooms ({activeRooms.filter((r) => r.type === "Classroom").length})
          </button>
          <button className={`subtab-btn ${tab === "LAB" ? "active" : ""}`} onClick={() => setTab("LAB")}>
            🔬 Laboratories ({activeRooms.filter((r) => r.type === "Lab").length})
          </button>
        </div>
      </div>

      <div className="card">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Resource Name</th>
                <th>Type</th>
                <th>Capacity</th>
                <th>Equipment</th>
                <th>Status</th>
                <th>Scheduled Load</th>
              </tr>
            </thead>
            <tbody>
              {displayedRooms.map((r) => {
                const roomSessions = timetable.filter((t) => t.room === r.name);
                const isOccupied = roomSessions.length > 0;
                return (
                  <tr key={r.id || r.name}>
                    <td><strong>{r.name}</strong></td>
                    <td>{r.type}</td>
                    <td>{r.capacity} seats</td>
                    <td>{r.equipment || (r.type === "Lab" ? "Computer" : "-")}</td>
                    <td>
                      {isOccupied ? (
                        <span className="badge" style={{ background: "#fee2e2", color: "#991b1b" }}>Occupied ({roomSessions.length} sessions/wk)</span>
                      ) : (
                        <span className="badge badge-success">Available</span>
                      )}
                    </td>
                    <td style={{ fontSize: "0.85rem", color: "#64748b" }}>
                      {roomSessions.length} weekly periods scheduled
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// =============================================================
// 10. PREFERENCES VIEW (Faculty Preferences & Availability)
// =============================================================
function PreferencesView({ department, notify }) {
  const [faculty, setFaculty] = useState([]);
  const [timetable, setTimetable] = useState([]);

  useEffect(() => {
    loadData();
  }, [department]);

  const loadData = async () => {
    const [fData, tData] = await Promise.all([
      api.fetchFaculty(department),
      api.fetchTimetable(department)
    ]);
    setFaculty(fData || []);
    setTimetable(tData || []);
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <div>
          <h2>Faculty Preferences & Availability</h2>
          <p style={{ color: "#64748b", marginTop: "4px" }}>
            Faculty availability is a hard constraint (scheduling impossible outside window). Preference (Morning/Afternoon) is a soft constraint.
          </p>
        </div>
      </div>

      <div className="card">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Faculty Full Name</th>
                <th>Short Code</th>
                <th>Hard Availability Window</th>
                <th>Soft Preference</th>
                <th>Weekly Max Load</th>
                <th>Assigned Load</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {faculty.map((f) => {
                const facSessions = timetable.filter((t) => t.faculty_code === f.code);
                const assignedHours = facSessions.length;
                const maxLoad = f.max_load || 18;
                const isOver = assignedHours > maxLoad;
                return (
                  <tr key={f.id || f.code}>
                    <td><strong>{f.name}</strong></td>
                    <td><span className="badge" style={{ background: "#e0e7ff", color: "#3730a3" }}>{f.code}</span></td>
                    <td>{f.availability || "Mon-Fri 9:00 AM-5:00 PM"}</td>
                    <td>
                      <span className="badge" style={{
                        background: f.preferred_time === "Morning" ? "#fef3c7" : f.preferred_time === "Afternoon" ? "#ede9fe" : "#f1f5f9",
                        color: f.preferred_time === "Morning" ? "#92400e" : f.preferred_time === "Afternoon" ? "#5b21b6" : "#475569"
                      }}>
                        {f.preferred_time || f.preference || "Any"}
                      </span>
                    </td>
                    <td>{maxLoad} hrs/wk</td>
                    <td><strong>{assignedHours} hrs</strong></td>
                    <td>
                      {isOver ? (
                        <span className="badge badge-danger">Overloaded</span>
                      ) : (
                        <span className="badge badge-success">Optimal</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// =============================================================
// 11. OCCUPANCY VIEW (Slot-Wise Matrix)
// =============================================================
function OccupancyView({ department }) {
  const [occDay, setOccDay] = useState("Monday");
  const [occPeriod, setOccPeriod] = useState("9:00 AM - 10:00 AM");
  const [occData, setOccData] = useState(null);
  const [loading, setLoading] = useState(false);

  const PERIODS_12H = [
    "9:00 AM - 10:00 AM",
    "10:00 AM - 11:00 AM",
    "11:15 AM - 12:15 PM",
    "12:15 PM - 1:15 PM",
    "2:00 PM - 3:00 PM",
    "3:00 PM - 4:00 PM"
  ];

  const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];

  useEffect(() => {
    loadOccupancy();
  }, [occDay, occPeriod, department]);

  const loadOccupancy = async () => {
    setLoading(true);
    try {
      const data = await api.fetchOccupancy(occDay, occPeriod, department, "ALL");
      setOccData(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const sum = occData?.summary || {};
  const cr = sum.classrooms || {};
  const lab = sum.labs || {};

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <div>
          <h2>Resource Occupancy Module</h2>
          <p style={{ color: "#64748b", marginTop: "4px" }}>
            Inspect physical classroom and lab utilization in any specific time slot.
          </p>
        </div>
        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          <select value={occDay} onChange={(e) => setOccDay(e.target.value)} style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}>
            {DAYS.map((d) => <option key={d} value={d}>{d}</option>)}
          </select>
          <select value={occPeriod} onChange={(e) => setOccPeriod(e.target.value)} style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}>
            {PERIODS_12H.map((p) => <option key={p} value={p}>{p}</option>)}
          </select>
        </div>
      </div>

      {/* KPI Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "20px" }}>
        <div className="card" style={{ borderLeft: "4px solid #2563eb" }}>
          <h4>Classrooms ({department}) — {occDay} {occPeriod}</h4>
          <div style={{ display: "flex", gap: "24px", marginTop: "12px" }}>
            <div>
              <div style={{ fontSize: "0.8rem", color: "#64748b" }}>Total</div>
              <div style={{ fontSize: "1.5rem", fontWeight: "700" }}>{cr.total || 0}</div>
            </div>
            <div>
              <div style={{ fontSize: "0.8rem", color: "#64748b" }}>Occupied</div>
              <div style={{ fontSize: "1.5rem", fontWeight: "700", color: "#ef4444" }}>{cr.occupied || 0}</div>
            </div>
            <div>
              <div style={{ fontSize: "0.8rem", color: "#64748b" }}>Available</div>
              <div style={{ fontSize: "1.5rem", fontWeight: "700", color: "#10b981" }}>{cr.available || 0}</div>
            </div>
          </div>
        </div>

        <div className="card" style={{ borderLeft: "4px solid #8b5cf6" }}>
          <h4>Laboratories ({department}) — {occDay} {occPeriod}</h4>
          <div style={{ display: "flex", gap: "24px", marginTop: "12px" }}>
            <div>
              <div style={{ fontSize: "0.8rem", color: "#64748b" }}>Total</div>
              <div style={{ fontSize: "1.5rem", fontWeight: "700" }}>{lab.total || 0}</div>
            </div>
            <div>
              <div style={{ fontSize: "0.8rem", color: "#64748b" }}>Occupied</div>
              <div style={{ fontSize: "1.5rem", fontWeight: "700", color: "#ef4444" }}>{lab.occupied || 0}</div>
            </div>
            <div>
              <div style={{ fontSize: "0.8rem", color: "#64748b" }}>Available</div>
              <div style={{ fontSize: "1.5rem", fontWeight: "700", color: "#10b981" }}>{lab.available || 0}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Resources Status Table */}
      <div className="card">
        <h3 style={{ marginBottom: "16px" }}>Resource Utilization Table ({occDay} {occPeriod})</h3>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Resource Name</th>
                <th>Type</th>
                <th>Capacity</th>
                <th>Equipment</th>
                <th>Status</th>
                <th>Occupying Details</th>
              </tr>
            </thead>
            <tbody>
              {(occData?.resources || []).map((r, i) => (
                <tr key={i}>
                  <td><strong>{r.resource}</strong></td>
                  <td>{r.type}</td>
                  <td>{r.capacity} seats</td>
                  <td>{r.equipment || "-"}</td>
                  <td>
                    {r.status === "OCCUPIED" ? (
                      <span className="badge" style={{ background: "#fee2e2", color: "#991b1b" }}>Occupied</span>
                    ) : (
                      <span className="badge badge-success">Available</span>
                    )}
                  </td>
                  <td style={{ fontSize: "0.85rem" }}>
                    {r.status === "OCCUPIED" && r.allocation ? (
                      <span>
                        <strong>Div {r.allocation.division}</strong> {r.allocation.batch !== "-" ? `(${r.allocation.batch})` : ""} — {r.allocation.subject} [{r.allocation.faculty}]
                      </span>
                    ) : (
                      <span style={{ color: "#94a3b8" }}>Free for department / cross-dept sharing</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// =============================================================
// 12. GENERATE TIMETABLE VIEW (CSP + MRV + Backtracking)
// =============================================================
function GenerateTimetableView({ department, notify, onSuccess }) {
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);

  const handleGenerate = async () => {
    setRunning(true);
    setResult(null);
    try {
      const res = await api.generateTimetable({ department });
      if (res.success) {
        setResult(res);
        notify(res.message, "success");
      } else {
        notify("Generation could not find a clash-free schedule: " + (res.message || ""), "error");
        setResult(res);
      }
    } catch (err) {
      notify("Failed to generate: " + err.message, "error");
    } finally {
      setRunning(false);
    }
  };

  const meta = result?.metadata || {};

  return (
    <div style={{ maxWidth: "800px", margin: "0 auto" }}>
      <div className="card" style={{ marginBottom: "20px" }}>
        <h2>⚡ Constraint Satisfaction (CSP) Timetable Engine</h2>
        <p style={{ color: "#64748b", marginTop: "6px", fontSize: "0.95rem" }}>
          ClashFree utilizes <strong>Constraint Satisfaction Problem (CSP)</strong> formulation, <strong>MRV (Minimum Remaining Values)</strong> variable selection heuristic, and <strong>Backtracking Search</strong> with state restoration.
        </p>

        {/* Algorithm Viva Highlights */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "12px", marginTop: "16px" }}>
          <div style={{ background: "#f8fafc", padding: "12px", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
            <div style={{ fontWeight: "700", color: "#1e3a8a" }}>1. CSP Variables</div>
            <div style={{ fontSize: "0.8rem", color: "#475569", marginTop: "4px" }}>
              Every lecture and lab session to be scheduled across the academic week.
            </div>
          </div>
          <div style={{ background: "#f8fafc", padding: "12px", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
            <div style={{ fontWeight: "700", color: "#0f766e" }}>2. MRV Heuristic</div>
            <div style={{ fontSize: "0.8rem", color: "#475569", marginTop: "4px" }}>
              Picks unscheduled session with FEWEST valid remaining options to fail fast and prune search branches.
            </div>
          </div>
          <div style={{ background: "#f8fafc", padding: "12px", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
            <div style={{ fontWeight: "700", color: "#6d28d9" }}>3. Backtracking</div>
            <div style={{ fontSize: "0.8rem", color: "#475569", marginTop: "4px" }}>
              Recursively attempts assignments. Undoes dead ends and automatically records clash resolutions.
            </div>
          </div>
        </div>

        <div style={{ marginTop: "24px", textAlign: "center" }}>
          <button
            className="btn"
            onClick={handleGenerate}
            disabled={running}
            style={{ padding: "12px 28px", fontSize: "1rem", fontWeight: "700", background: "#2563eb" }}
          >
            {running ? "🔄 Running CSP + MRV Backtracking Engine..." : "⚡ Generate Clash-Free Timetable"}
          </button>
        </div>
      </div>

      {result && (
        <div className="card" style={{ borderLeft: result.success ? "4px solid #10b981" : "4px solid #ef4444" }}>
          <h3>{result.success ? "✅ Timetable Generated Successfully!" : "❌ Generation Failed"}</h3>
          <p style={{ marginTop: "6px", color: result.success ? "#15803d" : "#b91c1c" }}>
            {result.message}
          </p>

          {result.success && (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "12px", margin: "16px 0" }}>
              <div style={{ background: "#f0fdf4", padding: "12px", borderRadius: "6px" }}>
                <div style={{ fontSize: "0.8rem", color: "#166534" }}>Sessions Scheduled</div>
                <div style={{ fontSize: "1.4rem", fontWeight: "700", color: "#15803d" }}>{result.count || 0}</div>
              </div>
              <div style={{ background: "#eff6ff", padding: "12px", borderRadius: "6px" }}>
                <div style={{ fontSize: "0.8rem", color: "#1e40af" }}>Clashes Resolved</div>
                <div style={{ fontSize: "1.4rem", fontWeight: "700", color: "#2563eb" }}>{meta.resolved_clashes || 0}</div>
              </div>
              <div style={{ background: "#f5f3ff", padding: "12px", borderRadius: "6px" }}>
                <div style={{ fontSize: "0.8rem", color: "#5b21b6" }}>Backtrack Steps</div>
                <div style={{ fontSize: "1.4rem", fontWeight: "700", color: "#6d28d9" }}>{meta.backtrack_steps || 0}</div>
              </div>
            </div>
          )}

          <div style={{ marginTop: "16px" }}>
            <button className="btn" onClick={onSuccess}>
              📅 Open Master Timetable View
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================
// 10. REPORTS & EXPORT VIEW
// =============================================================
function ReportsView({ department }) {
  const [repDivs, setRepDivs] = useState([]);
  const [repSelectedDiv, setRepSelectedDiv] = useState("ALL");

  useEffect(() => {
    api.fetchDivisions(department).then(divs => setRepDivs(divs || []));
  }, [department]);

  return (
    <div className="card">
      <h3>📄 Academic Reports & Export Hub</h3>
      <p style={{ color: "#64748b", margin: "6px 0 24px" }}>
        Generate standardized collegiate reports for HOD review, board approvals, and accreditation documentation.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
        <div style={{ background: "#f8fafc", padding: "20px", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
          <h4>📅 Timetable Excel Export (Collegiate Grid)</h4>
          <p style={{ fontSize: "0.875rem", color: "#64748b", margin: "8px 0 16px" }}>
            Official collegiate matrix format with subjects, faculty codes, lab batches, course legend, and signatures.
          </p>

          <div style={{ marginBottom: "16px" }}>
            <label style={{ fontSize: "0.85rem", fontWeight: 700, display: "block", marginBottom: "6px" }}>
              Filter by Division / Class:
            </label>
            <select
              value={repSelectedDiv}
              onChange={(e) => setRepSelectedDiv(e.target.value)}
              style={{ width: "100%", padding: "8px 12px", borderRadius: "6px", border: "1px solid #cbd5e1", fontWeight: 600 }}
            >
              <option value="ALL">All Divisions (Master Multi-Tab Workbook)</option>
              {repDivs.map((d) => (
                <option key={d.name} value={d.name}>
                  {d.name} ({d.year || "Second Year"})
                </option>
              ))}
            </select>
          </div>

          <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
            <a
              href={api.getExportTimetableUrl(department, repSelectedDiv === "ALL" ? "" : repSelectedDiv)}
              className="btn"
              style={{ background: "#1e40af", color: "#fff" }}
              target="_blank"
              rel="noreferrer"
            >
              {repSelectedDiv === "ALL" ? "📥 Download Master Workbook (.xlsx)" : `📥 Download ${repSelectedDiv} (.xlsx)`}
            </a>
            {repSelectedDiv !== "ALL" && (
              <a
                href={api.getExportTimetableUrl(department)}
                className="btn btn-secondary"
                target="_blank"
                rel="noreferrer"
              >
                📑 Master All-Divisions
              </a>
            )}
          </div>
        </div>

        <div style={{ background: "#f8fafc", padding: "20px", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
          <h4>📊 Academic Load Report</h4>
          <p style={{ fontSize: "0.875rem", color: "#64748b", margin: "8px 0 16px" }}>
            College format showing Direct Contact Hours, Theory, Practical, Project, Seminar, and Grand Total.
          </p>
          <a href={api.getExportWorkloadUrl(department)} className="btn" target="_blank" rel="noreferrer">
            📥 Download Load Report (.xlsx)
          </a>
        </div>
      </div>
    </div>
  );
}

// =============================================================
// 11. TIME SLOTS & SETTINGS VIEW (Requirement 21 - Configurable Break/Class Times)
// =============================================================
function SettingsView({ notify }) {
  const [slots, setSlots] = useState([]);
  const [loading, setLoading] = useState(false);

  // Customization Form State
  const [startTime, setStartTime] = useState("09:00");
  const [periodDuration, setPeriodDuration] = useState(60);
  const [morningPeriods, setMorningPeriods] = useState(2);
  const [shortBreak1Duration, setShortBreak1Duration] = useState(10);
  const [preLunchPeriods, setPreLunchPeriods] = useState(2);
  const [lunchDuration, setLunchDuration] = useState(40);
  const [afternoonPeriods, setAfternoonPeriods] = useState(2);
  const [shortBreak2Duration, setShortBreak2Duration] = useState(10);
  const [finalPeriods, setFinalPeriods] = useState(1);
  const [workingDays, setWorkingDays] = useState([
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
  ]);

  const ALL_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

  useEffect(() => {
    load();
  }, []);

  const load = async () => {
    const data = await api.fetchTimeSlots();
    setSlots(data || []);
    const cfg = await api.fetchTimeSettings();
    if (cfg && cfg.start_time) {
      setStartTime(cfg.start_time || "09:00");
      setPeriodDuration(cfg.period_duration || 60);
      setMorningPeriods(cfg.morning_periods || 2);
      setShortBreak1Duration(cfg.short_break_1_duration || 10);
      setPreLunchPeriods(cfg.pre_lunch_periods || 2);
      setLunchDuration(cfg.lunch_duration || 40);
      setAfternoonPeriods(cfg.afternoon_periods || 2);
      setShortBreak2Duration(cfg.short_break_2_duration || 10);
      setFinalPeriods(cfg.final_periods || 1);
      if (cfg.working_days && cfg.working_days.length > 0) {
        setWorkingDays(cfg.working_days);
      }
    }
  };

  const toMinutes = (timeStr) => {
    const [h, m] = timeStr.split(":").map(Number);
    return h * 60 + m;
  };

  const toTimeString = (mins) => {
    const h = Math.floor(mins / 60) % 24;
    const m = mins % 60;
    return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
  };

  const handleGenerateSlots = () => {
    let currentMins = toMinutes(startTime);
    let order = 1;
    const newSlots = [];

    // Helper to add slot
    const addSlot = (duration, type, isMorning) => {
      const startStr = toTimeString(currentMins);
      currentMins += Number(duration);
      const endStr = toTimeString(currentMins);
      newSlots.push({
        order_index: order++,
        period: `${startStr}-${endStr}`,
        start_time: startStr,
        end_time: endStr,
        type: type,
        is_morning: isMorning,
      });
    };

    // 1. Morning Periods
    for (let i = 0; i < Number(morningPeriods); i++) {
      addSlot(periodDuration, "TEACHING", true);
    }

    // 2. Short Break 1
    if (Number(shortBreak1Duration) > 0) {
      addSlot(shortBreak1Duration, "SHORT_BREAK", true);
    }

    // 3. Pre-Lunch Periods
    for (let i = 0; i < Number(preLunchPeriods); i++) {
      addSlot(periodDuration, "TEACHING", true);
    }

    // 4. Lunch Break
    if (Number(lunchDuration) > 0) {
      addSlot(lunchDuration, "LUNCH", false);
    }

    // 5. Afternoon Periods
    for (let i = 0; i < Number(afternoonPeriods); i++) {
      addSlot(periodDuration, "TEACHING", false);
    }

    // 6. Short Break 2
    if (Number(shortBreak2Duration) > 0) {
      addSlot(shortBreak2Duration, "SHORT_BREAK", false);
    }

    // 7. Final Periods
    for (let i = 0; i < Number(finalPeriods); i++) {
      addSlot(periodDuration, "TEACHING", false);
    }

    setSlots(newSlots);
    notify(`Generated ${newSlots.length} schedule periods with configured break & lecture times!`);
  };

  const handleLoadCollegePreset = () => {
    setStartTime("09:00");
    setPeriodDuration(60);
    setMorningPeriods(2);
    setShortBreak1Duration(10);
    setPreLunchPeriods(2);
    setLunchDuration(40);
    setAfternoonPeriods(2);
    setShortBreak2Duration(10);
    setFinalPeriods(1);
    setWorkingDays(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]);

    // Directly build the matching array
    const dypSlots = [
      { order_index: 1, period: "9:00 AM - 10:00 AM", start_time: "09:00", end_time: "10:00", type: "TEACHING", is_morning: true },
      { order_index: 2, period: "10:00 AM - 11:00 AM", start_time: "10:00", end_time: "11:00", type: "TEACHING", is_morning: true },
      { order_index: 3, period: "11:00 AM - 11:10 AM", start_time: "11:00", end_time: "11:10", type: "SHORT_BREAK", is_morning: true },
      { order_index: 4, period: "11:10 AM - 12:10 PM", start_time: "11:10", end_time: "12:10", type: "TEACHING", is_morning: true },
      { order_index: 5, period: "12:10 PM - 1:10 PM", start_time: "12:10", end_time: "13:10", type: "TEACHING", is_morning: true },
      { order_index: 6, period: "1:10 PM - 1:50 PM", start_time: "13:10", end_time: "13:50", type: "LUNCH", is_morning: false },
      { order_index: 7, period: "1:50 PM - 2:50 PM", start_time: "13:50", end_time: "14:50", type: "TEACHING", is_morning: false },
      { order_index: 8, period: "2:50 PM - 3:50 PM", start_time: "14:50", end_time: "15:50", type: "TEACHING", is_morning: false },
      { order_index: 9, period: "3:50 PM - 4:00 PM", start_time: "15:50", end_time: "16:00", type: "SHORT_BREAK", is_morning: false },
      { order_index: 10, period: "4:00 PM - 5:00 PM", start_time: "16:00", end_time: "17:00", type: "TEACHING", is_morning: false },
    ];
    setSlots(dypSlots);
    notify("Loaded standard 6-Day college bell schedule!");
  };

  const handleLoadStandard5DayPreset = () => {
    setStartTime("09:00");
    setPeriodDuration(60);
    setMorningPeriods(2);
    setShortBreak1Duration(15);
    setPreLunchPeriods(1);
    setLunchDuration(45);
    setAfternoonPeriods(2);
    setShortBreak2Duration(15);
    setFinalPeriods(1);
    setWorkingDays(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]);

    const stdSlots = [
      { order_index: 1, period: "9:00 AM - 10:00 AM", start_time: "09:00", end_time: "10:00", type: "TEACHING", is_morning: true },
      { order_index: 2, period: "10:00 AM - 11:00 AM", start_time: "10:00", end_time: "11:00", type: "TEACHING", is_morning: true },
      { order_index: 3, period: "11:00 AM - 11:15 AM", start_time: "11:00", end_time: "11:15", type: "SHORT_BREAK", is_morning: true },
      { order_index: 4, period: "11:15 AM - 12:15 PM", start_time: "11:15", end_time: "12:15", type: "TEACHING", is_morning: true },
      { order_index: 5, period: "12:15 PM - 1:00 PM", start_time: "12:15", end_time: "13:00", type: "LUNCH", is_morning: false },
      { order_index: 6, period: "1:00 PM - 2:00 PM", start_time: "13:00", end_time: "14:00", type: "TEACHING", is_morning: false },
      { order_index: 7, period: "2:00 PM - 3:00 PM", start_time: "14:00", end_time: "15:00", type: "TEACHING", is_morning: false },
      { order_index: 8, period: "3:00 PM - 3:15 PM", start_time: "15:00", end_time: "15:15", type: "SHORT_BREAK", is_morning: false },
      { order_index: 9, period: "3:15 PM - 4:15 PM", start_time: "15:15", end_time: "16:15", type: "TEACHING", is_morning: false },
    ];
    setSlots(stdSlots);
    notify("Loaded standard 5-Day engineering schedule!");
  };

  const handleUpdateSlotField = (idx, field, value) => {
    const updated = [...slots];
    updated[idx][field] = value;
    if (field === "start_time" || field === "end_time") {
      updated[idx].period = `${updated[idx].start_time}-${updated[idx].end_time}`;
    }
    setSlots(updated);
  };

  const handleDeleteSlot = (idx) => {
    const updated = slots.filter((_, i) => i !== idx);
    updated.forEach((s, i) => (s.order_index = i + 1));
    setSlots(updated);
  };

  const handleAddCustomSlot = () => {
    const lastSlot = slots[slots.length - 1];
    const startStr = lastSlot ? lastSlot.end_time : "17:00";
    const endMins = toMinutes(startStr) + 60;
    const endStr = toTimeString(endMins);
    const newSlot = {
      order_index: slots.length + 1,
      period: `${startStr}-${endStr}`,
      start_time: startStr,
      end_time: endStr,
      type: "TEACHING",
      is_morning: false,
    };
    setSlots([...slots, newSlot]);
  };

  const toggleDay = (day) => {
    if (workingDays.includes(day)) {
      if (workingDays.length <= 1) {
        notify("At least 1 working day is required", "error");
        return;
      }
      setWorkingDays(workingDays.filter((d) => d !== day));
    } else {
      setWorkingDays([...workingDays, day]);
    }
  };

  const handleSaveAll = async () => {
    setLoading(true);
    try {
      const cfgPayload = {
        start_time: startTime,
        period_duration: Number(periodDuration),
        morning_periods: Number(morningPeriods),
        short_break_1_duration: Number(shortBreak1Duration),
        pre_lunch_periods: Number(preLunchPeriods),
        lunch_duration: Number(lunchDuration),
        afternoon_periods: Number(afternoonPeriods),
        short_break_2_duration: Number(shortBreak2Duration),
        final_periods: Number(finalPeriods),
        working_days: workingDays,
      };

      await api.saveTimeSettings(cfgPayload);
      await api.saveTimeSlots(slots);
      notify("Academic time schedule, break durations, and working days saved successfully!");
    } catch {
      notify("Failed to save schedule settings", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Institutional Structure Preset Banner with Zero Input Required */}
      <div className="card" style={{ marginBottom: "24px", border: "2px solid #2563eb", background: "linear-gradient(135deg, #eff6ff 0%, #ffffff 100%)" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "16px" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ fontSize: "1.5rem" }}>🏛️</span>
              <h3 style={{ margin: 0, color: "#1e3a8a" }}>Standard Engineering Academic Structure & Bell Schedule Preset</h3>
            </div>
            <p style={{ color: "#475569", margin: "8px 0 12px", fontSize: "0.9rem" }}>
              Zero manual input required! One-click structure configuration for CSE Department — sets up divisions, academic years, time slots, and working days automatically.
            </p>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "8px", fontSize: "0.82rem", color: "#334155" }}>
              <div>🏢 <strong>Department:</strong> Computer Science & Engineering</div>
              <div>📅 <strong>Academic Year:</strong> 2026-27 (Sem III)</div>
              <div>⏰ <strong>Working Days:</strong> Mon - Sat (6 Days, 10 Periods)</div>
              <div>🕘 <strong>Schedule:</strong> 9:00 AM – 5:00 PM</div>
              <div>☕ <strong>Short Break:</strong> 11:00 AM (10 mins)</div>
              <div>🍽️ <strong>Lunch Break:</strong> 1:10 PM – 1:50 PM</div>
            </div>
          </div>
          <button
            className="btn"
            style={{ background: "#1e40af", color: "#fff", padding: "12px 20px", fontSize: "0.95rem", fontWeight: 700, boxShadow: "0 4px 6px -1px rgba(30, 64, 175, 0.3)" }}
            onClick={async () => {
              setLoading(true);
              try {
                await api.applyStructurePreset();
                notify("✅ Standard CSE academic structure & 6-day bell schedule applied successfully with zero user input!");
                load();
              } catch (e) {
                notify("Failed to apply preset", "error");
              } finally {
                setLoading(false);
              }
            }}
            disabled={loading}
          >
            ⚡ Apply Standard Structure Preset (Zero Input)
          </button>
        </div>
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
        <div>
          <h3>⚙️ Academic Periods, Break & Lecture Time Customizer</h3>
          <p style={{ color: "#64748b", marginTop: "4px" }}>
            Configure college start time, class durations, short breaks, lunch duration, and active working days.
          </p>
        </div>
        <div style={{ display: "flex", gap: "8px" }}>
          <button className="btn btn-secondary" onClick={handleLoadCollegePreset}>
            🏫 Load College Reference Preset (Mon-Sat)
          </button>
          <button className="btn btn-secondary" onClick={handleLoadStandard5DayPreset}>
            ⚡ Load Standard 5-Day Preset (Mon-Fri)
          </button>
          <button className="btn" onClick={handleSaveAll} disabled={loading}>
            💾 Save & Apply Schedule
          </button>
        </div>
      </div>

      {/* Bell Schedule Interactive Configurator Form */}
      <div className="card" style={{ marginBottom: "20px" }}>
        <h4 style={{ marginBottom: "14px", color: "#1e40af" }}>
          ⏱️ Auto-Generate Time Slots from Bell Schedule Parameters
        </h4>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "16px", marginBottom: "16px" }}>
          <div>
            <label style={{ display: "block", fontSize: "0.85rem", fontWeight: "600", marginBottom: "4px" }}>
              Day Start Time:
            </label>
            <input
              type="time"
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
              style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: "0.85rem", fontWeight: "600", marginBottom: "4px" }}>
              Class Duration (mins):
            </label>
            <input
              type="number"
              min="30"
              max="90"
              value={periodDuration}
              onChange={(e) => setPeriodDuration(e.target.value)}
              style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: "0.85rem", fontWeight: "600", marginBottom: "4px" }}>
              Morning Lectures:
            </label>
            <input
              type="number"
              min="1"
              max="4"
              value={morningPeriods}
              onChange={(e) => setMorningPeriods(e.target.value)}
              style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: "0.85rem", fontWeight: "600", marginBottom: "4px" }}>
              1st Short Break (mins):
            </label>
            <input
              type="number"
              min="0"
              max="30"
              value={shortBreak1Duration}
              onChange={(e) => setShortBreak1Duration(e.target.value)}
              style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: "0.85rem", fontWeight: "600", marginBottom: "4px" }}>
              Pre-Lunch Lectures:
            </label>
            <input
              type="number"
              min="1"
              max="4"
              value={preLunchPeriods}
              onChange={(e) => setPreLunchPeriods(e.target.value)}
              style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: "0.85rem", fontWeight: "600", marginBottom: "4px" }}>
              Lunch Break (mins):
            </label>
            <input
              type="number"
              min="20"
              max="75"
              value={lunchDuration}
              onChange={(e) => setLunchDuration(e.target.value)}
              style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: "0.85rem", fontWeight: "600", marginBottom: "4px" }}>
              Afternoon Lectures:
            </label>
            <input
              type="number"
              min="1"
              max="4"
              value={afternoonPeriods}
              onChange={(e) => setAfternoonPeriods(e.target.value)}
              style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: "0.85rem", fontWeight: "600", marginBottom: "4px" }}>
              2nd Short Break (mins):
            </label>
            <input
              type="number"
              min="0"
              max="30"
              value={shortBreak2Duration}
              onChange={(e) => setShortBreak2Duration(e.target.value)}
              style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
            />
          </div>
        </div>

        {/* Working Days Selector */}
        <div style={{ marginBottom: "16px", padding: "12px", background: "#f8fafc", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
          <label style={{ display: "block", fontSize: "0.85rem", fontWeight: "700", marginBottom: "8px" }}>
            📅 Active Working Days (Included in Timetable Generation):
          </label>
          <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
            {ALL_DAYS.map((day) => {
              const active = workingDays.includes(day);
              return (
                <button
                  key={day}
                  type="button"
                  onClick={() => toggleDay(day)}
                  style={{
                    padding: "6px 14px",
                    borderRadius: "20px",
                    border: active ? "1px solid #2563eb" : "1px solid #cbd5e1",
                    background: active ? "#eff6ff" : "#fff",
                    color: active ? "#1e40af" : "#64748b",
                    fontWeight: active ? "700" : "500",
                    cursor: "pointer",
                    fontSize: "0.85rem",
                  }}
                >
                  {active ? "✓ " : ""}{day}
                </button>
              );
            })}
          </div>
        </div>

        <button className="btn" onClick={handleGenerateSlots}>
          ⚡ Compute & Generate Time Slots Sequence
        </button>
      </div>

      {/* Editable Table of Defined Periods */}
      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
          <h4>Active Periods List ({slots.length} Defined Periods)</h4>
          <button className="btn btn-secondary" onClick={handleAddCustomSlot} style={{ fontSize: "0.85rem" }}>
            + Add Custom Period (Zero Hour / Remedial)
          </button>
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th style={{ width: "60px" }}>#</th>
                <th>Period Label</th>
                <th>Start Time</th>
                <th>End Time</th>
                <th>Period Type</th>
                <th>Session</th>
                <th>Scheduler Action</th>
                <th style={{ width: "80px" }}>Remove</th>
              </tr>
            </thead>
            <tbody>
              {slots.map((s, idx) => (
                <tr key={idx}>
                  <td><strong>{s.order_index || idx + 1}</strong></td>
                  <td>
                    <input
                      type="text"
                      value={s.period}
                      onChange={(e) => handleUpdateSlotField(idx, "period", e.target.value)}
                      style={{ padding: "4px 8px", borderRadius: "4px", border: "1px solid #cbd5e1", fontWeight: "600", width: "130px" }}
                    />
                  </td>
                  <td>
                    <input
                      type="time"
                      value={s.start_time}
                      onChange={(e) => handleUpdateSlotField(idx, "start_time", e.target.value)}
                      style={{ padding: "4px 6px", borderRadius: "4px", border: "1px solid #cbd5e1" }}
                    />
                  </td>
                  <td>
                    <input
                      type="time"
                      value={s.end_time}
                      onChange={(e) => handleUpdateSlotField(idx, "end_time", e.target.value)}
                      style={{ padding: "4px 6px", borderRadius: "4px", border: "1px solid #cbd5e1" }}
                    />
                  </td>
                  <td>
                    <select
                      value={s.type}
                      onChange={(e) => handleUpdateSlotField(idx, "type", e.target.value)}
                      style={{ padding: "4px 8px", borderRadius: "4px", border: "1px solid #cbd5e1", fontWeight: "600" }}
                    >
                      <option value="TEACHING">TEACHING (Classes Scheduled)</option>
                      <option value="SHORT_BREAK">SHORT_BREAK (Recess)</option>
                      <option value="LUNCH">LUNCH (Mid-day Meal)</option>
                    </select>
                  </td>
                  <td>
                    <select
                      value={s.is_morning ? "morning" : "afternoon"}
                      onChange={(e) => handleUpdateSlotField(idx, "is_morning", e.target.value === "morning")}
                      style={{ padding: "4px 6px", borderRadius: "4px", border: "1px solid #cbd5e1" }}
                    >
                      <option value="morning">Morning</option>
                      <option value="afternoon">Afternoon</option>
                    </select>
                  </td>
                  <td>
                    {s.type === "TEACHING" ? (
                      <span style={{ color: "#16a34a", fontWeight: "700", fontSize: "0.85rem" }}>
                        ✓ CSP Schedulable
                      </span>
                    ) : (
                      <span style={{ color: "#b45309", fontWeight: "700", fontSize: "0.85rem" }}>
                        🔒 Blocked Break ({s.type === "LUNCH" ? "Lunch" : "Recess"})
                      </span>
                    )}
                  </td>
                  <td>
                    <button
                      className="btn btn-danger"
                      onClick={() => handleDeleteSlot(idx)}
                      style={{ padding: "2px 8px", fontSize: "0.75rem" }}
                    >
                      ✕
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
