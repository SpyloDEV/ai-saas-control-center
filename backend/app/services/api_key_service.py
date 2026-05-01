from datetime import UTC, datetime
from hashlib import sha256

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.core.security import generate_api_key
from app.models.api_key import ApiKey
from app.models.enums import ApiKeyStatus
from app.repositories.control_center import ControlCenterRepository
from app.services.audit_log_service import AuditLogService


class ApiKeyService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = ControlCenterRepository(session)
        self.audit_logs = AuditLogService(session)

    async def create_api_key(
        self, *, user_id: str, workspace_id: str, name: str
    ) -> tuple[str, ApiKey]:
        if not await self.repository.ensure_workspace_member(
            workspace_id=workspace_id,
            user_id=user_id,
        ):
            raise PermissionDeniedError("You do not have access to this workspace.")
        raw_key = generate_api_key()
        record = await self.repository.create_api_key(
            data={
                "workspace_id": workspace_id,
                "name": name,
                "key_hash": sha256(raw_key.encode()).hexdigest(),
                "key_prefix": raw_key[:14],
                "status": ApiKeyStatus.ACTIVE,
            }
        )
        await self.audit_logs.record(
            action="api_key_created",
            workspace_id=workspace_id,
            actor_id=user_id,
            target_type="api_key",
            target_id=record.id,
        )
        return raw_key, record

    async def list_api_keys(self, *, user_id: str, workspace_id: str) -> list[ApiKey]:
        return await self.repository.list_api_keys(
            user_id=user_id,
            workspace_id=workspace_id,
        )

    async def revoke_api_key(self, *, user_id: str, api_key_id: str) -> ApiKey:
        api_key = await self.repository.get_api_key_for_user(
            api_key_id=api_key_id,
            user_id=user_id,
        )
        if api_key is None:
            raise NotFoundError("API key not found.")
        api_key.status = ApiKeyStatus.REVOKED
        api_key.revoked_at = datetime.now(UTC)
        return api_key
