from pydantic import BaseModel,Field
from fastapi import Form as FastAPIForm
from datetime import datetime
from enum import Enum
from uuid import UUID
from typing import Annotated


class LoginForm(BaseModel):
    username : str = Field(
        ...,
        min_length =5,
        max_length = 100,
        description = "User email address",
        examples = ["john@example.com"],
    )
    password : str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="User password",
        examples=["password123"],
 )
    @classmethod
    def as_form(
        cls,
        username: Annotated[str, FastAPIForm(min_length=5, max_length=100, description="user email address")],
        password: Annotated[str, FastAPIForm(min_length=6, max_length=100, description="user password")]
    ) -> "LoginForm":
        return cls(username=username, password=password)



class SessionCookies(BaseModel):
    session_id : str | None = Field(
        default = None,
        description = "Session id stored in cookie after login",

    )

class ClientHeaders(BaseModel):
    x_client_version: str | None = Field(
        default = None,
        alias = "x-client-version",
        description = "CLient app version",

    )
    x_api_key : str | None = Field(
        default = None,
        alias = "x_api_key",
        description = "CLient app version"
    )
    model_config = {"populate_by_name": True}

    
class TaskStatus(str, Enum):
    pending = "pending"
    ongoing = "ongoing"
    completed = "completed"

class Assignee(BaseModel):
    user_id: int = Field(..., ge=1)
    name: str = Field(..., min_length=2, max_length=50)
    email: str = Field(..., description="Assignee email address")


class Tag(BaseModel):
    name: str = Field(..., min_length=1, max_length=30)
    color: str = Field(default="gray", pattern="^(gray|red|blue|green|yellow)$")


class TaskBase(BaseModel):
    title : str = Field(...,min_length = 3,max_length=100,examples = ["Buy groceries"])
    description : str = Field(...,min_length = 10,max_length = 500, examples = ["Pick up milk, eggs, and bread from the store"])
    status : str = Field(default = "pending",pattern = "^(pending|ongoing|completed)$")
    due_date : datetime | None = Field(default = None,examples = ["2026-05-01T10:00:00"])
    assignee : Assignee | None = Field(default = None)
    tags : list[Tag] = Field(default = [])

    
class TaskCreate(TaskBase):
     model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Buy groceries",
                    "description": "Pick up milk, eggs, and bread from the store",
                    "status": "pending",
                    "due_date": "2026-05-01T10:00:00",
                    "assignee": {"user_id": 1, "name": "John Doe", "email": "john@example.com"},
                    "tags": [{"name": "shopping", "color": "blue"}]
                }
            ]
        }
    }



class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=100)
    description: str | None = Field(default=None, min_length=10, max_length=500)
    status: str | None = Field(default=None, pattern="^(pending|ongoing|completed)$")
    due_date: datetime | None = Field(default=None)
    assignee: Assignee | None = Field(default=None)
    tags: list[Tag] | None = Field(default=None)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "in_progress",    # only send what you want to update
                    "tags": [{"name": "urgent", "color": "red"}]
                }
            ]
        }
    }


class TaskResponse(BaseModel):
    task_id: UUID
    created_at: datetime
    title: str
    description: str
    status: str
    due_date: datetime | None
    assignee: Assignee | None
    tags: list[Tag]


class TaskInDB(TaskBase):
    task_id : UUID
    created_at : datetime
    updated_at : datetime | None = None


class TaskListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    results: list[TaskResponse]



class TaskFilter(BaseModel):
    status: str | None = Field(
        default = None,
        pattern = "^(pending|ongoing|completed)$",
        description = "Filter tasks by status"
    )
    limit: int = Field(
        default = 10,
        ge = 1,
        le = 100,
        description = "Number of tasks to return"
    )
    skip: int = Field(
        default=0,
        ge = 0,
        description="Number of tasks to skip"
    )
    search: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,  
        description="Search tasks by title keyword,"
    )


class HealthResponse(BaseModel):
    status: str
    app: str | None
    debug: str | None


class AdminTasksResponse(BaseModel):
    total: int
    tasks: list[TaskResponse]


class SessionResponse(BaseModel):
    message: str
    session_id: str | None = None


class AuthMessageResponse(BaseModel):
    message: str


class FileUploadResponse(BaseModel):
    filename: str
    content_type: str
    size_mb: float
    saved_to: str


class MultipleFilesUploadResponse(BaseModel):
    uploaded: int
    files: list[dict]




