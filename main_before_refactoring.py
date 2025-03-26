from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Хранилище данных в памяти
tasks_db = []

class Task(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    completed: bool = False

@app.post("/tasks/", response_model=Task)
def create_task(task: Task):
    task.id = len(tasks_db) + 1
    tasks_db.append(task.dict())
    return task

@app.get("/tasks/", response_model=List[Task])
def read_tasks(completed: Optional[bool] = None):
    if completed is None:
        return tasks_db
    return [task for task in tasks_db if task["completed"] == completed]

@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: int):
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: Task):
    for task in tasks_db:
        if task["id"] == task_id:
            task.update(updated_task.dict())
            task["id"] = task_id
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    global tasks_db
    for i, task in enumerate(tasks_db):
        if task["id"] == task_id:
            del tasks_db[i]
            return {"message": "Task deleted"}
    raise HTTPException(status_code=404, detail="Task not found")