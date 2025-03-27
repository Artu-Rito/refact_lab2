from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI()

class TaskManager:
    def __init__(self):
        self.tasks = []
        self.counter = 0

    def create_task(self, task_data: dict) -> dict:
        self.counter += 1
        task_data["id"] = self.counter
        self.tasks.append(task_data)
        return task_data

    def get_task(self, task_id: int) -> Optional[dict]:
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None

    def get_all_tasks(self, completed: Optional[bool] = None) -> List[dict]:
        if completed is None:
            return self.tasks
        return [task for task in self.tasks if task["completed"] == completed]

    def update_task(self, task_id: int, updated_data: dict) -> Optional[dict]:
        for task in self.tasks:
            if task["id"] == task_id:
                task.update(updated_data)
                task["id"] = task_id
                return task
        return None

    def delete_task(self, task_id: int) -> bool:
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                del self.tasks[i]
                return True
        return False

    def clear(self):
        self.tasks.clear()
        self.counter = 0

task_manager = TaskManager()
tasks_db = task_manager.tasks  

class Task(BaseModel):
    id: Optional[int] = None
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    completed: bool = False

@app.post("/tasks/", response_model=Task)
def create_task(task: Task):
    return task_manager.create_task(task.model_dump())

@app.get("/tasks/", response_model=List[Task])
def read_tasks(completed: Optional[bool] = None):
    return task_manager.get_all_tasks(completed)

@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: int):
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: Task):
    task = task_manager.update_task(task_id, updated_task.model_dump())
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    if not task_manager.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}

def clear_tasks_db():
    task_manager.clear()