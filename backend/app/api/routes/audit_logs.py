from fastapi import APIRouter, Query

from app.api.dependencies import CurrentUser, DbSession
from app.schemas.audit_log import AuditLogRead
from app.services.audit_log_service import AuditLogService

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("", response_model=list[AuditLogRead])
async def list_audit_logs(
    current_user: CurrentUser,
    session: DbSession,
    workspace_id: str = Query(...),
) -> list[AuditLogRead]:
    return await AuditLogService(session).list_logs(
        user_id=current_user.id,
        workspace_id=workspace_id,
    )
