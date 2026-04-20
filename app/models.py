from pydantic import BaseModel,Field
from datetime import datetime
from enum import Enum
from datetime import datetime
from uuid import UUID


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
    
class TaskCreate(BaseModel):
    title: str = Field( ...,min_length = 3,max_length=100,description="Title of the task",examples = ["Buy groceries"])
    description: str = Field(...,min_length=10,max_length=500,description="detailed description of the task",examples = ["Pick up milk, eggs, and bread from the store"])
    status: TaskStatus = Field(
        default = "pending",
        pattern = "^(pending|ongoing|completed)",
        description="Filter task by status",
        examples = ["pending"]
    )
    due_date: datetime | None = Field(
        default=None,
        description="Optional due date for the task",
        examples = ["2026-05-01T10:00:00"]
    )   
    assignee : Assignee | None = Field(default=None)
    tags :list[Tag] = Field(default=[],examples = [ {"name": "shopping", "color": "blue"},{"name": "urgent", "color": "red"}])


class TaskResponse(BaseModel):
    task_id: UUID
    created_at: datetime
    title: str
    description: str
    status: str
    due_date: datetime | None
    assignee: Assignee | None
    tags: list[Tag]



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




