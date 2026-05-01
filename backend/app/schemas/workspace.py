from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import WorkspaceRole


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    slug: str | None = Field(default=None, min_length=2, max_length=180)


class WorkspaceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=180)


class TeamInviteRequest(BaseModel):
    email: EmailStr
    role: WorkspaceRole = WorkspaceRole.MEMBER


class WorkspaceRead(BaseModel):
    id: str
    name: str
    slug: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkspaceMemberRead(BaseModel):
    id: str
    workspace_id: str
    user_id: str
    role: WorkspaceRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
