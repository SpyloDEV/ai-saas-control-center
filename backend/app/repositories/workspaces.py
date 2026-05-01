from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import WorkspaceRole
from app.models.workspace import Workspace, WorkspaceMember


class WorkspaceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, workspace_id: str) -> Workspace | None:
        return await self.session.get(Workspace, workspace_id)

    async def get_by_slug(self, slug: str) -> Workspace | None:
        result = await self.session.execute(
            select(Workspace).where(Workspace.slug == slug)
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, *, user_id: str) -> list[Workspace]:
        result = await self.session.execute(
            select(Workspace)
            .join(WorkspaceMember)
            .where(WorkspaceMember.user_id == user_id)
            .order_by(Workspace.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, *, name: str, slug: str) -> Workspace:
        workspace = Workspace(name=name, slug=slug)
        self.session.add(workspace)
        await self.session.flush()
        return workspace

    async def add_member(
        self,
        *,
        workspace_id: str,
        user_id: str,
        role: WorkspaceRole,
    ) -> WorkspaceMember:
        member = WorkspaceMember(workspace_id=workspace_id, user_id=user_id, role=role)
        self.session.add(member)
        await self.session.flush()
        return member

    async def get_member(
        self,
        *,
        workspace_id: str,
        user_id: str,
    ) -> WorkspaceMember | None:
        result = await self.session.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()
