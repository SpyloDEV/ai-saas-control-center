from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent
from app.models.workspace import WorkspaceMember


class AgentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_for_user(self, *, agent_id: str, user_id: str) -> Agent | None:
        result = await self.session.execute(
            select(Agent)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Agent.workspace_id)
            .where(Agent.id == agent_id, WorkspaceMember.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        *,
        user_id: str,
        workspace_id: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[Agent], int]:
        filters = [WorkspaceMember.user_id == user_id]
        if workspace_id:
            filters.append(Agent.workspace_id == workspace_id)
        total = await self.session.scalar(
            select(func.count(Agent.id))
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Agent.workspace_id)
            .where(*filters)
        )
        result = await self.session.execute(
            select(Agent)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Agent.workspace_id)
            .where(*filters)
            .order_by(Agent.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all()), int(total or 0)

    async def create(self, *, data: dict) -> Agent:
        agent = Agent(**data)
        self.session.add(agent)
        await self.session.flush()
        return agent
