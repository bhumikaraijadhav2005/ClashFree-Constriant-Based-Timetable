// frontend/src/api.js
// Centralized API client communicating with Flask Backend

const API_BASE = (import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? "http://127.0.0.1:5000/api" : "/api")).replace(/\/$/, "");

export async function fetchStatus() {
  const res = await fetch(`${API_BASE}/status`);
  return res.json();
}

export async function fetchDashboard(department = "CSE") {
  const res = await fetch(`${API_BASE}/dashboard?department=${encodeURIComponent(department)}`);
  return res.json();
}

// -------------------------------------------------------------
// DEPARTMENTS & ACADEMIC STRUCTURE
// -------------------------------------------------------------
export async function fetchDepartments() {
  const res = await fetch(`${API_BASE}/departments`);
  return res.json();
}

export async function saveDepartment(dept) {
  const res = await fetch(`${API_BASE}/departments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dept),
  });
  return res.json();
}

export async function deleteDepartment(id) {
  const res = await fetch(`${API_BASE}/departments/${id}`, { method: "DELETE" });
  return res.json();
}

export async function fetchAcademicStructure(department = "CSE") {
  const res = await fetch(`${API_BASE}/academic-structure?department=${encodeURIComponent(department)}`);
  return res.json();
}

export async function saveAcademicStructure(structure) {
  const res = await fetch(`${API_BASE}/academic-structure`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(structure),
  });
  return res.json();
}

export async function fetchAcademicYears(department = "CSE") {
  const res = await fetch(`${API_BASE}/academic-years?department=${encodeURIComponent(department)}`);
  return res.json();
}

export async function fetchSemesters(department = "CSE", year = "") {
  let url = `${API_BASE}/semesters?department=${encodeURIComponent(department)}`;
  if (year) url += `&year=${encodeURIComponent(year)}`;
  const res = await fetch(url);
  return res.json();
}

export async function fetchDivisions(department = "CSE") {
  const res = await fetch(`${API_BASE}/divisions?department=${encodeURIComponent(department)}`);
  return res.json();
}

export async function saveDivision(division) {
  const res = await fetch(`${API_BASE}/divisions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(division),
  });
  return res.json();
}

export async function deleteDivision(id) {
  const res = await fetch(`${API_BASE}/divisions/${id}`, { method: "DELETE" });
  return res.json();
}

export async function fetchBatches(divisionName = "", department = "") {
  const params = new URLSearchParams();
  if (divisionName) params.set("division", divisionName);
  if (department) params.set("department", department);
  const suffix = params.toString();
  const url = `${API_BASE}/batches${suffix ? `?${suffix}` : ""}`;
  const res = await fetch(url);
  return res.json();
}

export async function saveBatch(batch) {
  const res = await fetch(`${API_BASE}/batches`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(batch),
  });
  return res.json();
}

export async function deleteBatch(id) {
  const res = await fetch(`${API_BASE}/batches/${id}`, { method: "DELETE" });
  return res.json();
}

// -------------------------------------------------------------
// FACULTY & WORKLOAD
// -------------------------------------------------------------
export async function fetchFaculty(department = "") {
  const url = department ? `${API_BASE}/faculty?department=${encodeURIComponent(department)}` : `${API_BASE}/faculty`;
  const res = await fetch(url);
  return res.json();
}

export async function saveFaculty(faculty) {
  const res = await fetch(`${API_BASE}/faculty`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(faculty),
  });
  return res.json();
}

export async function deleteFaculty(id) {
  const res = await fetch(`${API_BASE}/faculty/${id}`, { method: "DELETE" });
  return res.json();
}

export async function fetchFacultyWorkload(department = "CSE") {
  const res = await fetch(`${API_BASE}/faculty-workload?department=${encodeURIComponent(department)}`);
  return res.json();
}

export async function fetchAcademicLoadReport(department = "CSE") {
  const res = await fetch(`${API_BASE}/academic-load-report?department=${encodeURIComponent(department)}`);
  return res.json();
}

// -------------------------------------------------------------
// ROOMS & RESOURCE RESERVATION
// -------------------------------------------------------------
export async function fetchRooms(department = "") {
  const url = department ? `${API_BASE}/rooms?department=${encodeURIComponent(department)}` : `${API_BASE}/rooms`;
  const res = await fetch(url);
  return res.json();
}

export async function saveRoom(room) {
  const res = await fetch(`${API_BASE}/rooms`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(room),
  });
  return res.json();
}

export async function deleteRoom(id) {
  const res = await fetch(`${API_BASE}/rooms/${id}`, { method: "DELETE" });
  return res.json();
}

export async function toggleRoomActive(roomId) {
  const res = await fetch(`${API_BASE}/rooms/${roomId}/toggle-active`, { method: "POST" });
  return res.json();
}

export async function fetchResourceConfig(department = "CSE") {
  const res = await fetch(`${API_BASE}/resource-config?department=${encodeURIComponent(department)}`);
  return res.json();
}

export async function saveResourceConfig(config) {
  const res = await fetch(`${API_BASE}/resource-config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });
  return res.json();
}

export async function fetchOccupancy(day = "Monday", period = "9:00 AM - 10:00 AM", department = "CSE", type = "ALL") {
  const url = `${API_BASE}/occupancy?day=${encodeURIComponent(day)}&period=${encodeURIComponent(period)}&department=${encodeURIComponent(department)}&type=${encodeURIComponent(type)}`;
  const res = await fetch(url);
  return res.json();
}

export async function fetchResourceSharing() {
  const res = await fetch(`${API_BASE}/resource-sharing`);
  return res.json();
}

export async function createResourceSharingRequest(reqData) {
  const res = await fetch(`${API_BASE}/resource-sharing`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(reqData),
  });
  return res.json();
}

export async function updateResourceSharingStatus(id, status, reviewedBy = "HOD") {
  const res = await fetch(`${API_BASE}/resource-sharing`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id, status, reviewed_by: reviewedBy }),
  });
  return res.json();
}

// -------------------------------------------------------------
// SUBJECTS
// -------------------------------------------------------------
export async function fetchSubjects(department = "") {
  const url = department ? `${API_BASE}/subjects?department=${encodeURIComponent(department)}` : `${API_BASE}/subjects`;
  const res = await fetch(url);
  return res.json();
}

export async function saveSubject(subject) {
  const res = await fetch(`${API_BASE}/subjects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(subject),
  });
  return res.json();
}

export async function deleteSubject(id) {
  const res = await fetch(`${API_BASE}/subjects/${id}`, { method: "DELETE" });
  return res.json();
}

// -------------------------------------------------------------
// TIMETABLE & SCHEDULER & VERSIONS
// -------------------------------------------------------------
export async function fetchTimetable(department = "CSE", versionId = "", options = {}) {
  let url = `${API_BASE}/timetable?department=${encodeURIComponent(department)}`;
  if (versionId) url += `&version_id=${encodeURIComponent(versionId)}`;
  if (options.year) url += `&year=${encodeURIComponent(options.year)}`;
  if (options.semester) url += `&semester=${encodeURIComponent(options.semester)}`;
  if (options.division) url += `&division=${encodeURIComponent(options.division)}`;
  const res = await fetch(url);
  return res.json();
}

export async function generateTimetable(payload = {}) {
  const res = await fetch(`${API_BASE}/generate-timetable`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function fetchTimetableVersions(department = "CSE") {
  const res = await fetch(`${API_BASE}/timetable-versions?department=${encodeURIComponent(department)}`);
  return res.json();
}

export async function activateTimetableVersion(versionId, department = "CSE") {
  const res = await fetch(`${API_BASE}/timetable-versions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ version_id: versionId, department }),
  });
  return res.json();
}

export async function restoreTimetableVersion(versionId, department = "CSE") {
  const res = await fetch(`${API_BASE}/timetable-versions/${versionId}/restore`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ department }),
  });
  return res.json();
}

// -------------------------------------------------------------
// CONFLICTS & VALIDATION
// -------------------------------------------------------------
export async function fetchConflicts(department = "CSE") {
  const res = await fetch(`${API_BASE}/conflicts?department=${encodeURIComponent(department)}`);
  return res.json();
}

// -------------------------------------------------------------
// TIME SLOTS & SETTINGS
// -------------------------------------------------------------
export async function fetchTimeSlots(department = "") {
  const suffix = department ? `?department=${encodeURIComponent(department)}` : "";
  const res = await fetch(`${API_BASE}/time-slots${suffix}`);
  return res.json();
}

export async function saveTimeSlots(slots, department = "") {
  const suffix = department ? `?department=${encodeURIComponent(department)}` : "";
  const res = await fetch(`${API_BASE}/time-slots${suffix}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(slots),
  });
  return res.json();
}

export async function fetchTimeSettings() {
  const res = await fetch(`${API_BASE}/time-settings`);
  return res.json();
}

export async function saveTimeSettings(settings) {
  const res = await fetch(`${API_BASE}/time-settings`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(settings),
  });
  return res.json();
}

// -------------------------------------------------------------
// EXCEL IMPORT & EXPORT
// -------------------------------------------------------------
export async function validateExcelFile(file, department = "CSE", academicYear = "2026-2027", semester = "Semester 3") {
  try {
    const formData = new FormData();
    formData.append("file", file);
    if (department) formData.append("department", department);
    if (academicYear) formData.append("academic_year", academicYear);
    if (semester) formData.append("semester", semester);
    const res = await fetch(`${API_BASE}/validate-excel`, {
      method: "POST",
      body: formData,
    });
    return await res.json();
  } catch (err) {
    return {
      success: false,
      errors: ["Could not connect to Flask Backend API (http://127.0.0.1:5000). Please ensure backend is running."]
    };
  }
}

export async function uploadExcelFile(file, department = "CSE", academicYear = "2026-2027", semester = "Semester 3") {
  try {
    const formData = new FormData();
    formData.append("file", file);
    if (department) formData.append("department", department);
    if (academicYear) formData.append("academic_year", academicYear);
    if (semester) formData.append("semester", semester);
    const res = await fetch(`${API_BASE}/import-excel`, {
      method: "POST",
      body: formData,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      return { success: false, errors: data.errors || [data.error || `Server returned error (${res.status})`] };
    }
    return data;
  } catch (err) {
    return {
      success: false,
      error: "Could not connect to Flask Backend API (http://127.0.0.1:5000). Please start the backend using 'python backend/app.py' or 'run.bat'."
    };
  }
}

export function getDownloadTemplateUrl() {
  return `${API_BASE}/download-template`;
}

export async function fetchClashHistory() {
  const res = await fetch(`${API_BASE}/clash-history`);
  return res.json();
}

export function getExportTimetableUrl(department = "CSE", division = "") {
  let url = `${API_BASE}/export/timetable?department=${encodeURIComponent(department)}`;
  if (division && division.trim()) {
    url += `&division=${encodeURIComponent(division.trim())}`;
  }
  return url;
}

export async function applyDYPatilPreset() {
  const res = await fetch(`${API_BASE}/structure/apply-dypatil-preset`, {
    method: "POST",
    headers: { "Content-Type": "application/json" }
  });
  return res.json();
}

// Alias for applyDYPatilPreset — use this in Settings UI (no college-specific naming)
export async function applyStructurePreset() {
  return applyDYPatilPreset();
}

export function getExportWorkloadUrl(department = "CSE") {
  return `${API_BASE}/export/workload?department=${encodeURIComponent(department)}`;
}
