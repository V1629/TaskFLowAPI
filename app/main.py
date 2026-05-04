from fastapi import FastAPI , Query, Path, HTTPException , Depends , Cookie , Header, status, Response, Form, UploadFile, File
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.errors import (
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from .models import (
    TaskCreate, TaskStatus, TaskFilter, SessionCookies, ClientHeaders,
    TaskListResponse, TaskResponse, TaskUpdate, HealthResponse, AdminTasksResponse,
    SessionResponse, AuthMessageResponse, LoginForm, FileUploadResponse,
    MultipleFilesUploadResponse
)
import os
from uuid import UUID, uuid4
from datetime import datetime   
from typing import Annotated , List

load_dotenv()

fake_db = []
fake_users = {
    "john@example.com": {"name": "John Doe", "password": "password123"},
    "jane@example.com": {"name": "Jane Doe", "password": "secret456"},
}

app = FastAPI(
    title=os.getenv("APP_NAME", "TaskFlow API"),
    description="A task management API built while learning FastAPI.",
    version="0.1.0",
)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


@app.get("/",
          tags=["Health"], response_model=HealthResponse,
          status_code = status.HTTP_200_OK,
          summary = "Health check",
          description = "CHeck if the api is running")
async def root(headers: Annotated[ClientHeaders, Depends()]):
    """Health check — confirms the API is alive."""
    return {
        "status": "ok",
        "app": os.getenv("APP_NAME"),
        "debug": os.getenv("DEBUG"),
    }

@app.get("/admin/tasks", 
         tags=["Admin"], response_model=AdminTasksResponse,
         summary="Admin — List All Tasks",
        description="Returns all tasks in the system. Requires a valid `X-API-Key` header.",
        response_description="All tasks with total count")
async def admin_list_tasks(
    headers: Annotated[ClientHeaders, Depends()]
):
    """Admin only  - requires x-api header"""
    if headers.x_api_key != "secret-admin-key":
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = " INvalid or missing api key"
        )
    
    return {"total" : len(fake_db), "tasks" : fake_db}



@app.get("/me", 
        tags=["Auth"], 
        response_model=SessionResponse,
        summary="Get Current Session",
        description="Returns the current session info if a valid session cookie exists.",
        response_description="Session status and session ID")
async def get_session(
    cookies: Annotated[SessionCookies, Depends()]
):
    if cookies.session_id is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "NO session found  - please login"
        )
    
    return {"message" : "Session active", "session_id" : cookies.session_id}

from fastapi.responses import JSONResponse

@app.post("/login", 
          tags=["Auth"], response_model=AuthMessageResponse,
          summary="Fake Login",
          description="Sets a session cookie without credentials. Used for testing cookie behaviour only.",
          response_description="Success message with session cookie set")
async def login():
    response = JSONResponse(content = {"message" : "Logged in successfully" , })
    response.set_cookie(
        key = "session_id",
        value = str(uuid4()),
        httponly = True,
        max_age = 3600
    )
    return response


@app.post("/login/form",
          tags=["Auth"],
          status_code=status.HTTP_200_OK,
          summary="Form Login",
          description="""
                    Login using HTML form data with email and password.
                    
                    - Accepts **application/x-www-form-urlencoded** — not JSON
                    - Returns a session cookie on success
                    - Use `john@example.com` / `password123` for testing
                    """,
          response_description="Welcome message with session cookie set")
async def login_form(form: Annotated[LoginForm, Depends(LoginForm.as_form)]):
    
    user = fake_users.get(form.username)
    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid email or password",
        )
    
    if user["password"] != form.password:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid password",
        )
    
    response = JSONResponse(content = {
        "message" : f"welcome back, {user['name']}!",
         "username" : form.username,
    })

    response.set_cookie(key="session_id",value=str(uuid4()),httponly=True,max_age=3600)
    return response



@app.post("/logout", 
          tags=["Auth"], response_model=AuthMessageResponse,
          summary="Logout",
          description="Clears the session cookie. Call this to end the current session.",
          response_description="Logout confirmation")
async def logout():
    response = JSONResponse(content = {"message" : "logged out"})
    response.delete_cookie("session_id")
    return response



@app.get("/tasks/{task_id}",
         tags=["Tasks"],
         status_code=status.HTTP_200_OK,
         response_model = TaskResponse,
         summary="Get Task",
         description="Fetch a single task by its UUID. Returns 404 if the task does not exist.",
         response_description="The requested task")
async def get_task(
    task_id: UUID = Path(
        ...,
        description = "The ID of the task to retrieve",
    )
):

    task = next((t for t in fake_db if t["task_id"] == task_id),None)

    if task is None:
        raise HTTPException(status_code=404,detail=f"Task {task_id} not found")

    return task


@app.patch("/tasks/{task_id}",
           tags=["Tasks"],
           response_model = TaskResponse,
           summary="Update Task",
           description="""
            Partially update a task — only send the fields you want to change.
            
            - Omitted fields remain **unchanged**
            - Cannot change `task_id` or `created_at`
            """)
async def update_task(
    task_id : UUID = Path(...,description = "The UUID of the task to update"),
    updates : TaskUpdate = None,
):
    """partially update a task  - only send field which you want to change"""

    task_index = next(
        (i for i, t in enumerate(fake_db) if t["task_id"] == task_id),
        None
    )
    if task_index is None:
        raise HTTPException(status_code = 404,detail = f"Task {task_id} not found ")
    
    update_data = updates.model_dump(exclude_unset =True)
    fake_db[task_index].update(update_data)

    return fake_db[task_index]


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

@app.post("/create_tasks",tags = ["Create_Tasks"],status_code=status.HTTP_201_CREATED,response_model = TaskResponse)
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


@app.delete("/tasks/{task_id}",tags = ["Tasks"],status_code = status.HTTP_204_NO_CONTENT,)
async def delete_task(task_id : UUID = Path(...,description = "the uuid of the task to delete"),):
    task_index = next(
        (i for i,t in enumerate(fake_db) if t["task_id"] == task_id), None
    )
    if task_index is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"Task {task_id} not found"
        )
    fake_db.pop(task_index)
    return Response(status_code = status.HTTP_204_NO_CONTENT)


@app.post("/tasks/{task_id}/attachments",tags = ["Files"],status_code = status.HTTP_201_CREATED)
async def attach_file_to_task(
    task_id : UUID = Path(..., description = "The UUID of the task"),
    file : UploadFile = File(...,description = "File to attach"),
    label : str = Form(...,description = "Label for this attachment e.g., 'screenshot', 'report' "),
    notes : str = Form(default = "",description = "Optional notes about this attachment")
):
    #check whether task exist
    task = next((t for t in fake_db if t["task_id"] == task_id),None)
    if task is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"Task {task_id} not found",
        )
    
    #validating file type
    allowed_types = ["image/jpeg","image/png","image/gif","application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"File type '{file.content_type}' not allowed",
        )
    
    #validate file size  - 5 Mb
    contents = await file.read()
    size_in_mb = len(contents)/(1024*1024)
    if size_in_mb > 5:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"FIle too large: {size_in_mb: .2f}MB. ",
        )
    
    #save file
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, f"{task_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    attachment = {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_mb": round(size_in_mb, 3),
        "label": label,
        "notes": notes,
        "path": file_path,

    }

    #add attachment list to taks if it does'nt exist
    if "attachments" not in task:
        task["attachments"] = []
    task["attachments"].append(attachment)

    return {
        "task_id" : task_id,
        "message" : "File attached successfully",
        "Attachment" : attachment,
    }








###FIle routes
@app.post("/uploads",tags=["files"],status_code=status.HTTP_201_CREATED,response_model=FileUploadResponse)
async def upload_file(file : UploadFile = File(...,description = "File to upload"),):
    """upload a single file"""

    allowed_types = ["image/jpeg", "image/gif", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"File type '{file.content_type}' not allowed. Allowed: {allowed_types}",
        )
    
    contents = await file.read()
    size_in_mb = len(contents) / (1024 *1024)
    if size_in_mb > 5:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"File too large: {size_in_mb:.2f}MB.Maximum allowed is 5MB."
        )
    
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    return {
        "filename" : file.filename,
        "content_type" : file.content_type,
        "size_mb" : round(size_in_mb, 3),
        "saved_to" : file_path
    }


@app.post("/uploads/multiple", tags=["Files"], status_code=status.HTTP_201_CREATED, response_model=MultipleFilesUploadResponse)
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
):
    """Upload multiple files at once."""
    allowed_types = ["image/jpeg", "image/png", "image/gif", "application/pdf"]
    results = []

    for file in files:
        # validate each file
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File '{file.filename}' has invalid type '{file.content_type}'",
            )

        contents = await file.read()
        size_in_mb = len(contents) / (1024 * 1024)

        if size_in_mb > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File '{file.filename}' is too large: {size_in_mb:.2f}MB",
            )

        upload_dir = "uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(contents)

        results.append({
            "filename": file.filename,
            "content_type": file.content_type,
            "size_mb": round(size_in_mb, 3),
        })

    return {
        "uploaded": len(results),
        "files": results,
    }