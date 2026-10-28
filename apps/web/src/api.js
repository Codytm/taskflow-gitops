const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    throw new Error(`Request failed (${response.status})`);
  }
  if (response.status === 204) {
    return null;
  }
  return response.json();
}

export function listTasks() {
  return request("/tasks");
}

export function createTask(title, notes) {
  return request("/tasks", {
    method: "POST",
    body: JSON.stringify({ title, notes }),
  });
}

export function updateTask(id, changes) {
  return request(`/tasks/${id}`, {
    method: "PATCH",
    body: JSON.stringify(changes),
  });
}

export function deleteTask(id) {
  return request(`/tasks/${id}`, { method: "DELETE" });
}
