import pytest
from fastapi.testclient import TestClient
from main import app, tasks_db, Task, clear_tasks_db
from pydantic import ValidationError

client = TestClient(app)


def test_create_task():
    clear_tasks_db()
    response = client.post(
        "/tasks/",
        json={"title": "Test task", "description": "Test description"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test task"
    assert response.json()["id"] == 1
    assert len(tasks_db) == 1


def test_read_tasks():
    clear_tasks_db()
    client.post("/tasks/", json={"title": "Task 1"})
    client.post("/tasks/", json={"title": "Task 2", "completed": True})

    response = client.get("/tasks/")
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = client.get("/tasks/?completed=true")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_read_task_boundary_conditions():
    clear_tasks_db()
    response = client.post("/tasks/", json={"title": "Boundary task"})
    assert response.status_code == 200  # Убедимся, что задача создана

    task_id = response.json()["id"]  # Получаем ID созданной задачи
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Boundary task"

    response = client.get("/tasks/0")
    assert response.status_code == 404

    response = client.get("/tasks/-1")
    assert response.status_code == 404


def test_create_task_with_missing_fields():
    clear_tasks_db()

    response = client.post(
        "/tasks/",
        json={"description": "Missing title"}
    )
    assert response.status_code == 422

    response = client.post("/tasks/", json={})
    assert response.status_code == 422


def test_update_task_with_invalid_data():
    clear_tasks_db()
    client.post("/tasks/", json={"title": "Task to update"})

    response = client.put("/tasks/1", json={"completed": True})
    assert response.status_code == 422

    response = client.put("/tasks/1", json={})
    assert response.status_code == 422


def test_task_validation():
    # Тест на успешное создание объекта
    task = Task(title="Valid Task", description="This is a valid task", completed=False)
    assert task.title == "Valid Task"
    assert task.description == "This is a valid task"
    assert task.completed is False

    # Тест на ошибку при отсутствии обязательного поля title
    with pytest.raises(ValidationError):
        Task(description="Missing title")

    # Тест на ошибку при превышении длины title
    with pytest.raises(ValidationError):
        Task(title="A" * 256, description="Too long title")


def test_delete_task_boundary_conditions():
    clear_tasks_db()
    response = client.post("/tasks/", json={"title": "Task to delete"})
    assert response.status_code == 200  # Убедимся, что задача создана

    task_id = response.json()["id"]  # Получаем ID созданной задачи
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted"

    response = client.delete("/tasks/0")
    assert response.status_code == 404

    response = client.delete("/tasks/-1")
    assert response.status_code == 404


def test_create_task_with_long_title():
    clear_tasks_db()

    long_title = "A" * 256
    response = client.post(
        "/tasks/",
        json={"title": long_title, "description": "Test long title"}
    )
    assert response.status_code == 422