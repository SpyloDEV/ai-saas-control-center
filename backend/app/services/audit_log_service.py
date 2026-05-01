from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.repositories.control_center import ControlCenterRepository


class AuditLogService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = ControlCenterRepository(session)

    async def record(
        self,
        *,
        action: str,
        workspace_id: str | None = None,
        actor_id: str | None = None,
        target_type: str | None = None,
        target_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditLog:
        return await self.repository.create_audit_log(
            data={
                "workspace_id": workspace_id,
                "actor_id": actor_id,
                "action": action,
                "target_type": target_type,
                "target_id": target_id,
                "metadata_json": metadata or {},
            }
        )

    async def list_logs(self, *, user_id: str, workspace_id: str) -> list[AuditLog]:
        if not await self.repository.ensure_workspace_member(
            workspace_id=workspace_id,
            user_id=user_id,
        ):
            from app.core.exceptions import PermissionDeniedError

            raise PermissionDeniedError("You do not have access to this workspace.")
        return await self.repository.list_audit_logs(
            user_id=user_id,
            workspace_id=workspace_id,
        )
