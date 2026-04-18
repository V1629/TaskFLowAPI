from fastapi import FastAPI , Query, Path, HTTPException , Depends
from dotenv import load_dotenv
from app.models import TaskCreate , TaskStatus, TaskFilter 
import os

load_dotenv()

fake_db = []

app = FastAPI(
    title=os.getenv("APP_NAME", "TaskFlow API"),
    description="A task management API built while learning FastAPI.",
    version="0.1.0",
)


@app.get("/", tags=["Health"])
async def root():
    """Health check — confirms the API is alive."""
    return {
        "status": "ok",
        "app": os.getenv("APP_NAME"),
        "debug": os.getenv("DEBUG"),
    }

@app.get("/tasks/{task_id}",tags=["Tasks"])
async def get_task(
    task_id: int = Path(
        ...,
        ge = 1,
        description = "The ID of the task to retrieve",
    )
):

    task = next((t for t in fake_db if t["task_id"] == task_id),None)

    if task is None:
        raise HTTPException(status_code=404,detail=f"Task {task_id} not found")

    return task

@app.get("/tasks", tags=["Tasks"])
async def list_tasks(filters: TaskFilter = Depends()):
    results = list(fake_db)

    if filters.status:
        results = [t for t in results if t["status"] == filters.status]

    if filters.search:
        results = [t for t in results if filters.search.lower() in t["title"].lower()]

    # fake_tasks = [
    #     {"task_id": i, "title": f"Task #{i}", "status": "pending"}
    #     for i in range(1, 20)
    # ]

    # if status != "all":
    #     fake_tasks = [t for t in fake_tasks if t["status"] == status]

    #Apply pagination
    return {
        "total" : len(results),
        "skip" : filters.skip,
        "limit" : filters.limit,
        "results" : results[filters.skip : filters.skip+filters.limit],
    }

@app.post("/create_tasks",tags = ["Create_Tasks"],status_code=201)
async def create_task(task : TaskCreate):
    """Create a new task and add it to the database"""
    new_task = {
        "task_id": len(fake_db) + 1,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "due_date": task.due_date,
        "assignee": task.assignee,
        "priority": task.priority,
    }
    fake_db.append(new_task)
    

    return {
        "message": "Task created successfully",
        "task":new_task
    }