import pytest
from fastapi.testclient import TestClient
from main import app, tasks_db, Task

client = TestClient(app)


def test_create_task():
    tasks_db.clear()
    response = client.post(
        "/tasks/",
        json={"title": "Test task", "description": "Test description"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test task"
    assert response.json()["id"] == 1
    assert len(tasks_db) == 1


def test_read_tasks():
    tasks_db.clear()
    client.post("/tasks/", json={"title": "Task 1"})
    client.post("/tasks/", json={"title": "Task 2", "completed": True})

    response = client.get("/tasks/")
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = client.get("/tasks/?completed=true")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_create_task_with_missing_fields():
    tasks_db.clear()

    response = client.post(
        "/tasks/",
        json={"description": "Missing title"}
    )
    assert response.status_code == 422

    response = client.post("/tasks/", json={})
    assert response.status_code == 422


def test_read_task_boundary_conditions():
    tasks_db.clear()
    client.post("/tasks/", json={"title": "Boundary task"})

    response = client.get("/tasks/1")
    assert response.status_code == 200
    assert response.json()["title"] == "Boundary task"

    response = client.get("/tasks/0")
    assert response.status_code == 404

    response = client.get("/tasks/-1")
    assert response.status_code == 404


def test_update_task_with_invalid_data():
    tasks_db.clear()
    client.post("/tasks/", json={"title": "Task to update"})

    response = client.put("/tasks/1", json={"completed": True})
    assert response.status_code == 422

    response = client.put("/tasks/1", json={})
    assert response.status_code == 422


def test_delete_task_boundary_conditions():
    tasks_db.clear()
    client.post("/tasks/", json={"title": "Task to delete"})

    response = client.delete("/tasks/1")
    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted"

    response = client.delete("/tasks/0")
    assert response.status_code == 404

    response = client.delete("/tasks/-1")
    assert response.status_code == 404


def test_create_task_with_long_title():
    tasks_db.clear()

    long_title = "A" * 256
    response = client.post(
        "/tasks/",
        json={"title": long_title, "description": "Test long title"}
    )
    assert response.status_code == 422