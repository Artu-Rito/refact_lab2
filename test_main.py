import pytest
from fastapi.testclient import TestClient
from main_before_refactoring import app, tasks_db, Task

client = TestClient(app)


def test_create_task():
    # Очищаем базу перед тестом
    tasks_db.clear()

    # Тест создания задачи
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

    # Тест получения всех задач
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert len(response.json()) == 2

    # Тест фильтрации по completed
    response = client.get("/tasks/?completed=true")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Task 2"


def test_read_task():
    tasks_db.clear()
    client.post("/tasks/", json={"title": "Test task"})

    # Тест получения существующей задачи
    response = client.get("/tasks/1")
    assert response.status_code == 200
    assert response.json()["title"] == "Test task"

    # Тест получения несуществующей задачи
    response = client.get("/tasks/999")
    assert response.status_code == 404


def test_update_task():
    tasks_db.clear()
    client.post("/tasks/", json={"title": "Original task"})

    # Тест обновления задачи
    updated_data = {"title": "Updated task", "completed": True}
    response = client.put("/tasks/1", json=updated_data)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated task"
    assert response.json()["completed"] == True

    # Проверяем, что данные действительно обновились в базе
    response = client.get("/tasks/1")
    assert response.json()["title"] == "Updated task"


def test_delete_task():
    tasks_db.clear()
    client.post("/tasks/", json={"title": "Task to delete"})

    # Тест удаления задачи
    response = client.delete("/tasks/1")
    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted"

    # Проверяем, что задача действительно удалена
    response = client.get("/tasks/1")
    assert response.status_code == 404