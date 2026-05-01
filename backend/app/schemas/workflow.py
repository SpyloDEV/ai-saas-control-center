from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ExecutionStatus, LogLevel, WorkflowStatus


class WorkflowCreate(BaseModel):
    workspace_id: str
    name: str = Field(min_length=1, max_length=180)
    description: str | None = Field(default=None, max_length=5000)


class WorkflowUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=180)
    description: str | None = Field(default=None, max_length=5000)
    status: WorkflowStatus | None = None


class WorkflowStepCreate(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    step_type: str = Field(min_length=1, max_length=80)
    step_order: int = Field(ge=1)
    config: dict[str, Any] = Field(default_factory=dict)


class WorkflowRead(BaseModel):
    id: str
    workspace_id: str
    name: str
    description: str | None
    status: WorkflowStatus
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkflowStepRead(BaseModel):
    id: str
    workflow_id: str
    step_order: int
    name: str
    step_type: str
    config: dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExecutionRead(BaseModel):
    id: str
    workspace_id: str
    workflow_id: str | None
    status: ExecutionStatus
    trigger: str
    result: dict[str, Any] | None
    error_message: str | None
    duration_ms: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExecutionLogRead(BaseModel):
    id: str
    execution_id: str
    level: LogLevel
    message: str
    metadata: dict[str, Any] = Field(
        validation_alias="metadata_json",
        serialization_alias="metadata",
    )
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
