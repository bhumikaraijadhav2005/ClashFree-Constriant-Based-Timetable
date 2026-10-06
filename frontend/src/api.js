// frontend/src/api.js
// Centralized API handler communicating with Flask Backend

const API_BASE = "http://127.0.0.1:5000/api";

export async function fetchStatus() {
  const res = await fetch(`${API_BASE}/status`);
  return res.json();
}

export async function fetchDashboard() {
  const res = await fetch(`${API_BASE}/dashboard`);
  return res.json();
}

export async function fetchFaculty() {
  const res = await fetch(`${API_BASE}/faculty`);
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

export async function fetchRooms() {
  const res = await fetch(`${API_BASE}/rooms`);
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

export async function fetchSubjects() {
  const res = await fetch(`${API_BASE}/subjects`);
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

export async function fetchSections() {
  const res = await fetch(`${API_BASE}/sections`);
  return res.json();
}

export async function saveSection(section) {
  const res = await fetch(`${API_BASE}/sections`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(section),
  });
  return res.json();
}

export async function deleteSection(id) {
  const res = await fetch(`${API_BASE}/sections/${id}`, { method: "DELETE" });
  return res.json();
}

export async function fetchTimetable() {
  const res = await fetch(`${API_BASE}/timetable`);
  return res.json();
}

export async function generateTimetable() {
  const res = await fetch(`${API_BASE}/generate-timetable`, { method: "POST" });
  return res.json();
}

export async function fetchConflicts() {
  const res = await fetch(`${API_BASE}/conflicts`);
  return res.json();
}

export async function uploadExcelFile(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/import-excel`, {
    method: "POST",
    body: formData,
  });
  return res.json();
}

