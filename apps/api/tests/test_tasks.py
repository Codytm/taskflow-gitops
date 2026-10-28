from fastapi.testclient import TestClient

from app.main import create_app


def test_create_and_list_task(client):
    created = client.post("/tasks", json={"title": "Buy milk", "notes": "Oat milk"})
    assert created.status_code == 201
    body = created.json()
    assert body["title"] == "Buy milk"
    assert body["notes"] == "Oat milk"
    assert body["done"] is False

    listed = client.get("/tasks")
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == body["id"]


def test_blank_title_is_rejected(client):
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 422


def test_update_and_delete_task(client):
    task_id = client.post("/tasks", json={"title": "Write tests"}).json()["id"]

    updated = client.patch(f"/tasks/{task_id}", json={"done": True, "notes": "pytest"})
    assert updated.status_code == 200
    assert updated.json()["done"] is True
    assert updated.json()["notes"] == "pytest"

    deleted = client.delete(f"/tasks/{task_id}")
    assert deleted.status_code == 204
    assert client.get("/tasks").json() == []


def test_missing_task_returns_404(client):
    assert client.patch("/tasks/999", json={"done": True}).status_code == 404
    assert client.delete("/tasks/999").status_code == 404


def test_task_persists_after_the_app_restarts(database_url):
    with TestClient(create_app(database_url)) as first:
        task_id = first.post("/tasks", json={"title": "Survive restart"}).json()["id"]

    with TestClient(create_app(database_url)) as second:
        tasks = second.get("/tasks").json()

    assert tasks[0]["id"] == task_id
    assert tasks[0]["title"] == "Survive restart"
