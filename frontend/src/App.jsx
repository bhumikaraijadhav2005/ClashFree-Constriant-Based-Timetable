// frontend/src/App.jsx
import React, { useState, useEffect } from "react";
import * as api from "./api";

const PAGES = [
  { id: "dashboard", label: "Dashboard", icon: "📊" },
  { id: "timetable", label: "Timetable", icon: "📅" },
  { id: "faculty", label: "Faculty", icon: "👨‍🏫" },
  { id: "rooms", label: "Rooms & Labs", icon: "🏫" },
  { id: "subjects", label: "Subjects", icon: "📚" },
  { id: "sections", label: "Sections", icon: "👥" },
  { id: "preferences", label: "Preferences", icon: "⚙️" },
  { id: "conflicts", label: "Conflicts", icon: "⚠️" },
  { id: "import", label: "Import Excel", icon: "📥" },
];

export default function App() {
  const [activePage, setActivePage] = useState("dashboard");
  const [status, setStatus] = useState({ online: false, supabase: false });
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    checkStatus();
    loadDashboard();
  }, []);

  const notify = (msg, type = "success") => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 4000);
  };

  const checkStatus = async () => {
    try {
      const res = await api.fetchStatus();
      setStatus({ online: true, supabase: res.supabase_configured });
    } catch {
      setStatus({ online: false, supabase: false });
    }
  };

  const loadDashboard = async () => {
    try {
      const res = await api.fetchDashboard();
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
          <span>⏰</span> ClashFree
        </div>
        <ul className="nav-links">
          {PAGES.map((page) => (
            <li
              key={page.id}
              className={`nav-item ${activePage === page.id ? "active" : ""}`}
              onClick={() => setActivePage(page.id)}
            >
              <span>{page.icon}</span>
              <span>{page.label}</span>
            </li>
          ))}
        </ul>
      </aside>

      {/* Main Area */}
      <main className="main-content">
        <header className="header">
          <div className="header-title">
            {PAGES.find((p) => p.id === activePage)?.label}
          </div>
          <div>
            {status.supabase ? (
              <span className="badge badge-success">✓ Supabase Connected</span>
            ) : (
              <span className="badge badge-warning">⚠ Supabase Not Configured</span>
            )}
          </div>
        </header>

        {notification && (
          <div
            style={{
              padding: "12px 24px",
              background: notification.type === "error" ? "#fef2f2" : "#f0fdf4",
              color: notification.type === "error" ? "#b91c1c" : "#15803d",
              borderBottom: "1px solid #e2e8f0",
            }}
          >
            {notification.msg}
          </div>
        )}

        <div className="content-body">
          {activePage === "dashboard" && (
            <DashboardView
              data={dashboardData}
              setPage={setActivePage}
              onRefresh={loadDashboard}
            />
          )}
          {activePage === "timetable" && <TimetableView notify={notify} />}
          {activePage === "faculty" && <FacultyView notify={notify} />}
          {activePage === "rooms" && <RoomsView notify={notify} />}
          {activePage === "subjects" && <SubjectsView notify={notify} />}
          {activePage === "sections" && <SectionsView notify={notify} />}
          {activePage === "preferences" && <PreferencesView notify={notify} />}
          {activePage === "conflicts" && <ConflictsView />}
          {activePage === "import" && (
            <ImportView
              notify={notify}
              onSuccess={() => {
                loadDashboard();
                setActivePage("dashboard");
              }}
            />
          )}
        </div>
      </main>
    </div>
  );
}

// -------------------------------------------------------------
// 1. DASHBOARD VIEW
// -------------------------------------------------------------
function DashboardView({ data, setPage, onRefresh }) {
  const counts = data?.counts || {};
  return (
    <div>
      <div className="grid-cards">
        <div className="card">
          <div className="card-title">Sections</div>
          <div className="card-value">{counts.sections || 0}</div>
        </div>
        <div className="card">
          <div className="card-title">Faculty Members</div>
          <div className="card-value">{counts.faculty || 0}</div>
        </div>
        <div className="card">
          <div className="card-title">Classrooms & Labs</div>
          <div className="card-value">{counts.rooms || 0}</div>
        </div>
        <div className="card">
          <div className="card-title">Subjects</div>
          <div className="card-value">{counts.subjects || 0}</div>
        </div>
        <div className="card">
          <div className="card-title">Scheduled Sessions</div>
          <div className="card-value">{counts.scheduled || 0}</div>
        </div>
      </div>

      <div className="card" style={{ marginTop: "20px" }}>
        <h3 style={{ marginBottom: "16px" }}>⚡ Quick Actions</h3>
        <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
          <button className="btn" onClick={() => setPage("timetable")}>
            📅 Open Timetable
          </button>
          <button className="btn btn-secondary" onClick={() => setPage("import")}>
            📥 Import Excel File
          </button>
          <button className="btn btn-secondary" onClick={() => setPage("faculty")}>
            👨‍🏫 Add Faculty
          </button>
          <button className="btn btn-secondary" onClick={() => setPage("rooms")}>
            🏫 Add Room
          </button>
        </div>
      </div>
    </div>
  );
}

// -------------------------------------------------------------
// 2. TIMETABLE VIEW
// -------------------------------------------------------------
function TimetableView({ notify }) {
  const [timetable, setTimetable] = useState([]);
  const [selectedSection, setSelectedSection] = useState("ALL");
  const [loading, setLoading] = useState(false);

  const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
  const PERIODS = [
    { label: "09:00-10:00", type: "TEACHING" },
    { label: "10:00-11:00", type: "TEACHING" },
    { label: "11:00-11:15", type: "SHORT_BREAK" },
    { label: "11:15-12:15", type: "TEACHING" },
    { label: "12:15-13:00", type: "LUNCH" },
    { label: "13:00-14:00", type: "TEACHING" },
    { label: "14:00-15:00", type: "TEACHING" },
    { label: "15:00-15:15", type: "SHORT_BREAK" },
    { label: "15:15-16:15", type: "TEACHING" },
  ];

  useEffect(() => {
    loadTimetable();
  }, []);

  const loadTimetable = async () => {
    try {
      const data = await api.fetchTimetable();
      setTimetable(data || []);
    } catch (e) {
      console.error(e);
    }
  };

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const res = await api.generateTimetable();
      if (res.success) {
        notify(res.message, "success");
        setTimetable(res.timetable);
      } else {
        notify(res.message || "Failed to generate timetable", "error");
      }
    } catch (e) {
      notify("Scheduling error occurred", "error");
    } finally {
      setLoading(false);
    }
  };

  const sectionsList = Array.from(new Set(timetable.map((t) => t.section)));

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          <label>Filter Section:</label>
          <select
            value={selectedSection}
            onChange={(e) => setSelectedSection(e.target.value)}
            style={{ padding: "8px", borderRadius: "6px", border: "1px solid #ccc" }}
          >
            <option value="ALL">All Sections</option>
            {sectionsList.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
        <button className="btn" onClick={handleGenerate} disabled={loading}>
          {loading ? "⚙️ Generating (CSP+MRV)..." : "🚀 Generate Timetable"}
        </button>
      </div>

      <div className="timetable-grid">
        <div className="grid-cell grid-header">Time / Day</div>
        {DAYS.map((d) => (
          <div key={d} className="grid-cell grid-header">{d}</div>
        ))}

        {PERIODS.map((p) => {
          if (p.type !== "TEACHING") {
            return (
              <React.Fragment key={p.label}>
                <div className="grid-cell" style={{ fontWeight: "600" }}>{p.label}</div>
                <div className="grid-cell grid-break" style={{ gridColumn: "span 5" }}>
                  {p.type === "LUNCH" ? "🥗 LUNCH BREAK (12:15 - 13:00)" : "☕ SHORT BREAK"}
                </div>
              </React.Fragment>
            );
          }

          return (
            <React.Fragment key={p.label}>
              <div className="grid-cell" style={{ fontWeight: "600" }}>{p.label}</div>
              {DAYS.map((day) => {
                const sessions = timetable.filter(
                  (t) =>
                    t.day === day &&
                    t.period === p.label &&
                    (selectedSection === "ALL" || t.section === selectedSection)
                );

                return (
                  <div key={day} className="grid-cell">
                    {sessions.map((s, idx) => (
                      <div key={idx} className="grid-session" style={{ padding: "6px", marginBottom: "4px", borderRadius: "4px" }}>
                        {s.is_lab && <div className="session-badge-lab">🔬 LAB</div>}
                        <div style={{ fontWeight: "700" }}>{s.subject} ({s.section})</div>
                        <div style={{ color: "#475569", fontSize: "0.8rem" }}>
                          📍 {s.room} | 👨‍🏫 {s.faculty_code}
                        </div>
                      </div>
                    ))}
                  </div>
                );
              })}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}

// -------------------------------------------------------------
// 3. FACULTY VIEW
// -------------------------------------------------------------
function FacultyView({ notify }) {
  const [faculty, setFaculty] = useState([]);
  const [name, setName] = useState("");
  const [subjects, setSubjects] = useState("");
  const [pref, setPref] = useState("Morning");

  useEffect(() => {
    load();
  }, []);

  const load = async () => {
    const data = await api.fetchFaculty();
    setFaculty(data || []);
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!name) return;
    const subjArray = subjects.split(",").map((s) => s.strip ? s.strip() : s.trim());
    await api.saveFaculty({
      name,
      subjects: subjArray,
      preferred_time: pref,
      available_from: "09:00",
      available_to: "17:00",
    });
    setName("");
    setSubjects("");
    notify("Faculty added successfully!");
    load();
  };

  const handleDelete = async (id) => {
    await api.deleteFaculty(id);
    notify("Faculty removed");
    load();
  };

  return (
    <div>
      <form onSubmit={handleAdd} className="card" style={{ display: "flex", gap: "12px", alignItems: "center", marginBottom: "20px" }}>
        <input
          placeholder="Faculty Name (e.g. Dr. Kunal Patil)"
          value={name}
          onChange={(e) => setName(e.target.value)}
          style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #ccc", flex: 1 }}
        />
        <input
          placeholder="Subjects (e.g. DSA, OS)"
          value={subjects}
          onChange={(e) => setSubjects(e.target.value)}
          style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #ccc", flex: 1 }}
        />
        <select value={pref} onChange={(e) => setPref(e.target.value)} style={{ padding: "8px", borderRadius: "6px", border: "1px solid #ccc" }}>
          <option value="Morning">Morning Preference</option>
          <option value="Afternoon">Afternoon Preference</option>
          <option value="Any">Any Time</option>
        </select>
        <button type="submit" className="btn">+ Add Faculty</button>
      </form>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Code</th>
              <th>Full Name</th>
              <th>Subjects</th>
              <th>Availability</th>
              <th>Preference</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {faculty.map((f) => (
              <tr key={f.id || f.name}>
                <td><strong>{f.code}</strong></td>
                <td>{f.name}</td>
                <td>{Array.isArray(f.subjects) ? f.subjects.join(", ") : f.subjects}</td>
                <td>{f.available_from} - {f.available_to}</td>
                <td>{f.preferred_time}</td>
                <td>
                  <button className="btn btn-danger" style={{ padding: "4px 8px", fontSize: "0.8rem" }} onClick={() => handleDelete(f.id)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
            {faculty.length === 0 && (
              <tr><td colSpan="6" style={{ textAlign: "center", color: "#64748b" }}>No faculty records found.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// -------------------------------------------------------------
// 4. ROOMS VIEW
// -------------------------------------------------------------
function RoomsView({ notify }) {
  const [rooms, setRooms] = useState([]);
  const [name, setName] = useState("");
  const [type, setType] = useState("Classroom");
  const [capacity, setCapacity] = useState(60);

  useEffect(() => { load(); }, []);

  const load = async () => {
    const data = await api.fetchRooms();
    setRooms(data || []);
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!name) return;
    await api.saveRoom({ name, type, capacity: Number(capacity) });
    setName("");
    notify("Room added successfully");
    load();
  };

  return (
    <div>
      <form onSubmit={handleAdd} className="card" style={{ display: "flex", gap: "12px", alignItems: "center", marginBottom: "20px" }}>
        <input
          placeholder="Room Name (e.g. Room 101, Lab 1)"
          value={name}
          onChange={(e) => setName(e.target.value)}
          style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #ccc", flex: 1 }}
        />
        <select value={type} onChange={(e) => setType(e.target.value)} style={{ padding: "8px", borderRadius: "6px", border: "1px solid #ccc" }}>
          <option value="Classroom">Classroom</option>
          <option value="Lab">Laboratory</option>
        </select>
        <input
          type="number"
          placeholder="Capacity"
          value={capacity}
          onChange={(e) => setCapacity(e.target.value)}
          style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #ccc", width: "100px" }}
        />
        <button type="submit" className="btn">+ Add Room</button>
      </form>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Room Name</th>
              <th>Type</th>
              <th>Capacity</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {rooms.map((r) => (
              <tr key={r.id || r.name}>
                <td><strong>{r.name}</strong></td>
                <td>{r.type === "Lab" ? "🔬 Lab" : "📚 Classroom"}</td>
                <td>{r.capacity} seats</td>
                <td>
                  <button className="btn btn-danger" style={{ padding: "4px 8px", fontSize: "0.8rem" }} onClick={async () => { await api.deleteRoom(r.id); load(); }}>
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

// -------------------------------------------------------------
// 5. SUBJECTS VIEW
// -------------------------------------------------------------
function SubjectsView({ notify }) {
  const [subjects, setSubjects] = useState([]);
  const [name, setName] = useState("");
  const [lec, setLec] = useState(3);
  const [lab, setLab] = useState(0);

  useEffect(() => { load(); }, []);

  const load = async () => {
    const data = await api.fetchSubjects();
    setSubjects(data || []);
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!name) return;
    await api.saveSubject({
      name,
      lectures_per_week: Number(lec),
      labs_per_week: Number(lab),
      requires_lab: Number(lab) > 0,
    });
    setName("");
    notify("Subject added");
    load();
  };

  return (
    <div>
      <form onSubmit={handleAdd} className="card" style={{ display: "flex", gap: "12px", alignItems: "center", marginBottom: "20px" }}>
        <input
          placeholder="Subject Name (e.g. Data Structures)"
          value={name}
          onChange={(e) => setName(e.target.value)}
          style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #ccc", flex: 1 }}
        />
        <label>Lectures/wk:</label>
        <input
          type="number"
          value={lec}
          onChange={(e) => setLec(e.target.value)}
          style={{ padding: "8px", borderRadius: "6px", border: "1px solid #ccc", width: "70px" }}
        />
        <label>Labs/wk:</label>
        <input
          type="number"
          value={lab}
          onChange={(e) => setLab(e.target.value)}
          style={{ padding: "8px", borderRadius: "6px", border: "1px solid #ccc", width: "70px" }}
        />
        <button type="submit" className="btn">+ Add Subject</button>
      </form>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Subject</th>
              <th>Lectures / Week</th>
              <th>Labs / Week</th>
              <th>Requires Lab</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {subjects.map((s) => (
              <tr key={s.id || s.name}>
                <td><strong>{s.name}</strong></td>
                <td>{s.lectures_per_week}</td>
                <td>{s.labs_per_week}</td>
                <td>{s.requires_lab ? "✅ Yes" : "❌ No"}</td>
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

// -------------------------------------------------------------
// 6. SECTIONS VIEW
// -------------------------------------------------------------
function SectionsView({ notify }) {
  const [sections, setSections] = useState([]);
  const [name, setName] = useState("");
  const [strength, setStrength] = useState(60);

  useEffect(() => { load(); }, []);

  const load = async () => {
    const data = await api.fetchSections();
    setSections(data || []);
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!name) return;
    await api.saveSection({ name, strength: Number(strength) });
    setName("");
    notify("Section added");
    load();
  };

  return (
    <div>
      <form onSubmit={handleAdd} className="card" style={{ display: "flex", gap: "12px", alignItems: "center", marginBottom: "20px" }}>
        <input
          placeholder="Section Name (e.g. CSE-A)"
          value={name}
          onChange={(e) => setName(e.target.value)}
          style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #ccc", flex: 1 }}
        />
        <input
          type="number"
          placeholder="Student Strength"
          value={strength}
          onChange={(e) => setStrength(e.target.value)}
          style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #ccc", width: "120px" }}
        />
        <button type="submit" className="btn">+ Add Section</button>
      </form>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Section Name</th>
              <th>Student Strength</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {sections.map((sec) => (
              <tr key={sec.id || sec.name}>
                <td><strong>{sec.name}</strong></td>
                <td>{sec.strength} students</td>
                <td>
                  <button className="btn btn-danger" style={{ padding: "4px 8px", fontSize: "0.8rem" }} onClick={async () => { await api.deleteSection(sec.id); load(); }}>
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

// -------------------------------------------------------------
// 7. PREFERENCES VIEW
// -------------------------------------------------------------
function PreferencesView() {
  return (
    <div className="card">
      <h3 style={{ marginBottom: "12px" }}>⚙️ Customization: Hard Restrictions vs. Soft Preferences</h3>
      <p style={{ color: "#64748b", lineHeight: 1.6, marginBottom: "16px" }}>
        ClashFree allows precise customization for faculty members to suit departmental requirements:
      </p>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
        <div style={{ background: "#f8fafc", padding: "16px", borderRadius: "8px", borderLeft: "4px solid #ef4444" }}>
          <h4>🛑 Hard Availability Restriction</h4>
          <p style={{ fontSize: "0.875rem", color: "#475569", marginTop: "8px" }}>
            The scheduler <strong>STRICTLY PROHIBITS</strong> scheduling the faculty outside their available hours (e.g., 09:00 - 13:00).
          </p>
        </div>
        <div style={{ background: "#f8fafc", padding: "16px", borderRadius: "8px", borderLeft: "4px solid #2563eb" }}>
          <h4>✨ Soft Preference</h4>
          <p style={{ fontSize: "0.875rem", color: "#475569", marginTop: "8px" }}>
            The scheduler prioritizes morning slots for faculty preferring morning teaching, falling back gracefully if slots are occupied.
          </p>
        </div>
      </div>
    </div>
  );
}

// -------------------------------------------------------------
// 8. CONFLICTS VIEW
// -------------------------------------------------------------
function ConflictsView() {
  const [conflicts, setConflicts] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    checkConflicts();
  }, []);

  const checkConflicts = async () => {
    setLoading(true);
    try {
      const res = await api.fetchConflicts();
      setConflicts(res.conflicts || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "16px" }}>
        <h3>⚠️ Constraint & Conflict Diagnostics</h3>
        <button className="btn btn-secondary" onClick={checkConflicts} disabled={loading}>
          {loading ? "Checking..." : "🔄 Refresh Conflicts"}
        </button>
      </div>

      {conflicts.length === 0 ? (
        <div style={{ padding: "20px", textAlign: "center", color: "#15803d", background: "#f0fdf4", borderRadius: "8px" }}>
          ✓ No constraint conflicts detected! All CSP variables and domains are feasible.
        </div>
      ) : (
        <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: "8px" }}>
          {conflicts.map((c, i) => (
            <li key={i} style={{ padding: "12px", background: "#fef2f2", borderLeft: "4px solid #ef4444", borderRadius: "4px", color: "#b91c1c" }}>
              {c}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// -------------------------------------------------------------
// 9. IMPORT EXCEL VIEW
// -------------------------------------------------------------
function ImportView({ notify, onSuccess }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    try {
      const res = await api.uploadExcelFile(file);
      if (res.success) {
        notify("Excel data imported successfully to Supabase!", "success");
        onSuccess();
      } else {
        notify(res.errors ? res.errors.join(", ") : res.error, "error");
      }
    } catch (e) {
      notify("Failed to upload Excel file", "error");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="card" style={{ maxWidth: "600px", margin: "0 auto", textAlign: "center", padding: "36px" }}>
      <h2>📥 Import Timetable Data (Excel)</h2>
      <p style={{ color: "#64748b", margin: "12px 0 24px" }}>
        Upload an Excel file (<code>.xlsx</code>) containing Faculty, Rooms, Subjects, and Sections.
      </p>

      <form onSubmit={handleUpload}>
        <input
          type="file"
          accept=".xlsx"
          onChange={(e) => setFile(e.target.files[0])}
          style={{ marginBottom: "20px" }}
        />
        <br />
        <button type="submit" className="btn" disabled={uploading}>
          {uploading ? "Importing..." : "Upload & Sync to Supabase"}
        </button>
      </form>
    </div>
  );
}
