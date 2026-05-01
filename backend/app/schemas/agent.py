from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AgentStatus


class AgentCreate(BaseModel):
    workspace_id: str
    name: str = Field(min_length=1, max_length=180)
    description: str | None = Field(default=None, max_length=5000)
    role: str = Field(min_length=1, max_length=120)
    instructions: str | None = Field(default=None, max_length=10000)
    model_provider: str = Field(default="mock", max_length=80)
    model_name: str = Field(default="mock-control-v1", max_length=120)
    temperature: float = Field(default=0.2, ge=0, le=2)
    status: AgentStatus = AgentStatus.ACTIVE


class AgentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=180)
    description: str | None = Field(default=None, max_length=5000)
    role: str | None = Field(default=None, min_length=1, max_length=120)
    instructions: str | None = Field(default=None, max_length=10000)
    model_provider: str | None = Field(default=None, max_length=80)
    model_name: str | None = Field(default=None, max_length=120)
    temperature: float | None = Field(default=None, ge=0, le=2)
    status: AgentStatus | None = None


class AgentRead(BaseModel):
    id: str
    workspace_id: str
    name: str
    description: str | None
    role: str
    instructions: str | None
    model_provider: str
    model_name: str
    temperature: float
    status: AgentStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
