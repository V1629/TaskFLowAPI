from fastapi import FastAPI , Query, Path, HTTPException , Depends , Cookie , Header
from dotenv import load_dotenv
from .models import TaskCreate , TaskStatus, TaskFilter 
import os
from uuid import UUID, uuid4
from datetime import datetime   
from typing import Annotated 

load_dotenv()

fake_db = []

app = FastAPI(
    title=os.getenv("APP_NAME", "TaskFlow API"),
    description="A task management API built while learning FastAPI.",
    version="0.1.0",
)


@app.get("/", tags=["Health"])
async def root(
    x_client_version : Annotated[str | None, Header()] = None,
):
    """Health check — confirms the API is alive."""
    return {
        "status": "ok",
        "app": os.getenv("APP_NAME"),
        "debug": os.getenv("DEBUG"),
    }

@app.get("/admin/tasks",tags=["Admin"])
async def admin_list_tasks(
    x_api_key : Annotated[str | None, Header()] = None,
):
    """Admin only  - requires x-api header"""
    if x_api_key != "secret-admin-key":
        raise HTTPException(
            status_code = 403,
            detail = " INvalid or missing api key"
        )
    
    return {"total" : len(fake_db), "tasks" : fake_db}



@app.get("/me",tags=["Auth"])
async def get_session(
    session_id : Annotated[str | None, Cookie()] = None
):
    if session_id is None:
        return {"message" : "No session found  - please log in"}
    
    return {"message" : "Session active", "session_id" : session_id}

from fastapi.responses import JSONResponse

@app.post("/login",tags=["Auth"])
async def login():
    response = JSONResponse(content = {"message" : "Logged in successfully" , })
    response.set_cookie(
        key = "session_id",
        value = str(uuid4()),
        httponly = True,
        max_age = 3600
    )
    return response

@app.post("/logout",tags=["Auth"])
async def logout():
    response = JSONResponse(content = {"message" : "logged out"})
    response.delete_cookie("session_id")
    return response



@app.get("/tasks/{task_id}",tags=["Tasks"])
async def get_task(
    task_id: UUID = Path(
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
        "task_id": uuid4(),
        "created_at" : datetime.now(),
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "due_date": task.due_date,
        "assignee": task.assignee,
        "tags": task.tags,
    }
    fake_db.append(new_task)
    

    return {
        "message": "Task created successfully",
        "task":new_task
    }