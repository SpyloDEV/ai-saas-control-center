import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError
from app.models.enums import WorkspaceRole
from app.models.workspace import Workspace, WorkspaceMember
from app.repositories.users import UserRepository
from app.repositories.workspaces import WorkspaceRepository
from app.services.audit_log_service import AuditLogService


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "workspace"


class WorkspaceService:
    def __init__(self, session: AsyncSession) -> None:
        self.workspaces = WorkspaceRepository(session)
        self.users = UserRepository(session)
        self.audit_logs = AuditLogService(session)

    async def create_workspace(
        self,
        *,
        user_id: str,
        name: str,
        slug: str | None,
    ) -> Workspace:
        workspace_slug = _slugify(slug or name)
        if await self.workspaces.get_by_slug(workspace_slug) is not None:
            raise ConflictError("A workspace with this slug already exists.")
        workspace = await self.workspaces.create(name=name, slug=workspace_slug)
        await self.workspaces.add_member(
            workspace_id=workspace.id,
            user_id=user_id,
            role=WorkspaceRole.OWNER,
        )
        await self.audit_logs.record(
            action="workspace_created",
            workspace_id=workspace.id,
            actor_id=user_id,
            target_type="workspace",
            target_id=workspace.id,
        )
        return workspace

    async def list_workspaces(self, *, user_id: str) -> list[Workspace]:
        return await self.workspaces.list_for_user(user_id=user_id)

    async def get_workspace(self, *, workspace_id: str, user_id: str) -> Workspace:
        workspace = await self.workspaces.get(workspace_id)
        member = await self.workspaces.get_member(
            workspace_id=workspace_id,
            user_id=user_id,
        )
        if workspace is None or member is None:
            raise NotFoundError("Workspace not found.")
        return workspace

    async def update_workspace(
        self,
        *,
        workspace_id: str,
        user_id: str,
        data: dict,
    ) -> Workspace:
        workspace = await self.get_workspace(workspace_id=workspace_id, user_id=user_id)
        member = await self.workspaces.get_member(
            workspace_id=workspace_id,
            user_id=user_id,
        )
        if member is None or member.role not in {
            WorkspaceRole.OWNER,
            WorkspaceRole.ADMIN,
        }:
            raise PermissionDeniedError("Only owners and admins can update workspaces.")
        for field, value in data.items():
            setattr(workspace, field, value)
        return workspace

    async def invite_member(
        self,
        *,
        workspace_id: str,
        invited_by_user_id: str,
        email: str,
        role: WorkspaceRole,
    ) -> WorkspaceMember:
        inviter = await self.workspaces.get_member(
            workspace_id=workspace_id,
            user_id=invited_by_user_id,
        )
        if inviter is None:
            raise NotFoundError("Workspace not found.")
        if inviter.role not in {WorkspaceRole.OWNER, WorkspaceRole.ADMIN}:
            raise PermissionDeniedError("Only owners and admins can invite members.")
        invited_user = await self.users.get_by_email(email)
        if invited_user is None:
            raise NotFoundError("The invited user must register first in this demo.")
        existing = await self.workspaces.get_member(
            workspace_id=workspace_id,
            user_id=invited_user.id,
        )
        if existing is not None:
            raise ConflictError("This user already belongs to the workspace.")
        member = await self.workspaces.add_member(
            workspace_id=workspace_id,
            user_id=invited_user.id,
            role=role,
        )
        await self.audit_logs.record(
            action="team_member_invited",
            workspace_id=workspace_id,
            actor_id=invited_by_user_id,
            target_type="workspace_member",
            target_id=member.id,
            metadata={"email": email, "role": role},
        )
        return member
