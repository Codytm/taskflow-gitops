import { useEffect, useState } from "react";
import { createTask, deleteTask, listTasks, updateTask } from "./api.js";

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [title, setTitle] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function refresh() {
    setError("");
    try {
      setTasks(await listTasks());
    } catch {
      setError("The API is not reachable. Start it, then reload this page.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function onCreate(event) {
    event.preventDefault();
    const nextTitle = title.trim();
    if (!nextTitle) {
      return;
    }
    setError("");
    try {
      await createTask(nextTitle, notes.trim());
      setTitle("");
      setNotes("");
      await refresh();
    } catch {
      setError("Could not save that task.");
    }
  }

  async function onToggle(task) {
    setError("");
    try {
      await updateTask(task.id, { done: !task.done });
      await refresh();
    } catch {
      setError("Could not update that task.");
    }
  }

  async function onDelete(task) {
    setError("");
    try {
      await deleteTask(task.id);
      await refresh();
    } catch {
      setError("Could not delete that task.");
    }
  }

  return (
    <main className="page">
      <header>
        <p className="eyebrow">TaskFlow</p>
        <h1>Tasks</h1>
        <p className="lede">A small list, stored in the database, so the deploy pipeline has something real to ship.</p>
      </header>

      <form className="composer" onSubmit={onCreate}>
        <label>
          Title
          <input
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            maxLength={200}
            required
            placeholder="Write the deploy notes"
          />
        </label>
        <label>
          Notes
          <textarea
            value={notes}
            onChange={(event) => setNotes(event.target.value)}
            rows={3}
            placeholder="Optional details"
          />
        </label>
        <button type="submit">Add task</button>
      </form>

      {error ? <p className="banner">{error}</p> : null}

      {loading ? <p>Loading tasks…</p> : null}

      {!loading && tasks.length === 0 ? <p className="empty">No tasks yet.</p> : null}

      <ul className="tasks">
        {tasks.map((task) => (
          <li key={task.id} className={task.done ? "done" : ""}>
            <label>
              <input type="checkbox" checked={task.done} onChange={() => onToggle(task)} />
              <span>
                <strong>{task.title}</strong>
                {task.notes ? <small>{task.notes}</small> : null}
              </span>
            </label>
            <button type="button" onClick={() => onDelete(task)}>
              Delete
            </button>
          </li>
        ))}
      </ul>
    </main>
  );
}
