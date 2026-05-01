from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.models.agent import Agent
from app.models.enums import AgentStatus
from app.repositories.agents import AgentRepository
from app.repositories.control_center import ControlCenterRepository
from app.services.audit_log_service import AuditLogService


class AgentService:
    def __init__(self, session: AsyncSession) -> None:
        self.agents = AgentRepository(session)
        self.control = ControlCenterRepository(session)
        self.audit_logs = AuditLogService(session)

    async def create_agent(self, *, user_id: str, data: dict) -> Agent:
        workspace_id = data["workspace_id"]
        if not await self.control.ensure_workspace_member(
            workspace_id=workspace_id,
            user_id=user_id,
        ):
            raise PermissionDeniedError("You do not have access to this workspace.")
        agent = await self.agents.create(data=data)
        await self.audit_logs.record(
            action="agent_created",
            workspace_id=workspace_id,
            actor_id=user_id,
            target_type="agent",
            target_id=agent.id,
        )
        return agent

    async def list_agents(
        self,
        *,
        user_id: str,
        workspace_id: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[Agent], int]:
        return await self.agents.list_for_user(
            user_id=user_id,
            workspace_id=workspace_id,
            limit=limit,
            offset=offset,
        )

    async def get_agent(self, *, agent_id: str, user_id: str) -> Agent:
        agent = await self.agents.get_for_user(agent_id=agent_id, user_id=user_id)
        if agent is None:
            raise NotFoundError("Agent not found.")
        return agent

    async def update_agent(
        self,
        *,
        agent_id: str,
        user_id: str,
        data: dict,
    ) -> Agent:
        agent = await self.get_agent(agent_id=agent_id, user_id=user_id)
        for field, value in data.items():
            setattr(agent, field, value)
        return agent

    async def delete_agent(self, *, agent_id: str, user_id: str) -> Agent:
        agent = await self.get_agent(agent_id=agent_id, user_id=user_id)
        agent.status = AgentStatus.INACTIVE
        return agent
