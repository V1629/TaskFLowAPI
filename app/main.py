from fastapi import FastAPI , Query, Path, HTTPException , Depends , Cookie , Header
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from .models import (
    TaskCreate, TaskStatus, TaskFilter, SessionCookies, ClientHeaders,
    TaskListResponse, TaskResponse, HealthResponse, AdminTasksResponse,
    SessionResponse, AuthMessageResponse
)
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


@app.get("/", tags=["Health"], response_model=HealthResponse)
async def root(headers: Annotated[ClientHeaders, Depends()]):
    """Health check — confirms the API is alive."""
    return {
        "status": "ok",
        "app": os.getenv("APP_NAME"),
        "debug": os.getenv("DEBUG"),
    }

@app.get("/admin/tasks", tags=["Admin"], response_model=AdminTasksResponse)
async def admin_list_tasks(
    headers: Annotated[ClientHeaders, Depends()]
):
    """Admin only  - requires x-api header"""
    if headers.x_api_key != "secret-admin-key":
        raise HTTPException(
            status_code = 403,
            detail = " INvalid or missing api key"
        )
    
    return {"total" : len(fake_db), "tasks" : fake_db}



@app.get("/me", tags=["Auth"], response_model=SessionResponse)
async def get_session(
    cookies: Annotated[SessionCookies, Depends()]
):
    if cookies.session_id is None:
        return {"message" : "No session found  - please log in"}
    
    return {"message" : "Session active", "session_id" : cookies.session_id}

from fastapi.responses import JSONResponse

@app.post("/login", tags=["Auth"], response_model=AuthMessageResponse)
async def login():
    response = JSONResponse(content = {"message" : "Logged in successfully" , })
    response.set_cookie(
        key = "session_id",
        value = str(uuid4()),
        httponly = True,
        max_age = 3600
    )
    return response

@app.post("/logout", tags=["Auth"], response_model=AuthMessageResponse)
async def logout():
    response = JSONResponse(content = {"message" : "logged out"})
    response.delete_cookie("session_id")
    return response



@app.get("/tasks/{task_id}",tags=["Tasks"], response_model = TaskResponse)
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

@app.get("/tasks", tags=["Tasks"], response_model = TaskListResponse)
async def list_tasks(filters: TaskFilter = Depends()):
    results = list(fake_db)

    if filters.status:
        results = [t for t in results if t["status"] == filters.status]

    if filters.search:
        results = [t for t in results if filters.search.lower() in t["title"].lower()]

    #Apply pagination
    return {
        "total" : len(results),
        "skip" : filters.skip,
        "limit" : filters.limit,
        "results" : results[filters.skip : filters.skip+filters.limit],
    }

@app.post("/create_tasks",tags = ["Create_Tasks"],status_code=201,response_model = TaskResponse)
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
    
    return new_task