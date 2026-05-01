from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.enums import DocumentStatus


class DocumentRead(BaseModel):
    id: str
    workspace_id: str
    uploaded_by: str
    filename: str
    content_type: str
    size_bytes: int
    status: DocumentStatus
    extracted_result: dict[str, Any] | None
    validation_warnings: list[str] | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
