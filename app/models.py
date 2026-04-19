from pydantic import BaseModel,Field
from datetime import datetime
from enum import Enum
from datetime import datetime
from uuid import UUID

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




