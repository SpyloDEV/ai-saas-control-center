from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ApiKeyStatus


class ApiKeyCreate(BaseModel):
    workspace_id: str
    name: str = Field(min_length=1, max_length=180)


class ApiKeyRead(BaseModel):
    id: str
    workspace_id: str
    name: str
    key_prefix: str
    status: ApiKeyStatus
    revoked_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApiKeyCreateResponse(BaseModel):
    api_key: str
    record: ApiKeyRead
