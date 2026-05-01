from fastapi import APIRouter, Query, status

from app.api.dependencies import CurrentUser, DbSession
from app.schemas.agent import AgentCreate, AgentRead, AgentUpdate
from app.schemas.common import Message, Page
from app.services.agent_service import AgentService

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.post("", response_model=AgentRead, status_code=status.HTTP_201_CREATED)
async def create_agent(
    payload: AgentCreate,
    current_user: CurrentUser,
    session: DbSession,
) -> AgentRead:
    agent = await AgentService(session).create_agent(
        user_id=current_user.id,
        data=payload.model_dump(),
    )
    await session.commit()
    await session.refresh(agent)
    return agent


@router.get("", response_model=Page[AgentRead])
async def list_agents(
    current_user: CurrentUser,
    session: DbSession,
    workspace_id: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> Page[AgentRead]:
    agents, total = await AgentService(session).list_agents(
        user_id=current_user.id,
        workspace_id=workspace_id,
        limit=limit,
        offset=offset,
    )
    return Page(items=agents, total=total, limit=limit, offset=offset)


@router.get("/{agent_id}", response_model=AgentRead)
async def get_agent(
    agent_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> AgentRead:
    return await AgentService(session).get_agent(
        agent_id=agent_id,
        user_id=current_user.id,
    )


@router.patch("/{agent_id}", response_model=AgentRead)
async def update_agent(
    agent_id: str,
    payload: AgentUpdate,
    current_user: CurrentUser,
    session: DbSession,
) -> AgentRead:
    agent = await AgentService(session).update_agent(
        agent_id=agent_id,
        user_id=current_user.id,
        data=payload.model_dump(exclude_unset=True),
    )
    await session.commit()
    await session.refresh(agent)
    return agent


@router.delete("/{agent_id}", response_model=Message)
async def delete_agent(
    agent_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> Message:
    await AgentService(session).delete_agent(agent_id=agent_id, user_id=current_user.id)
    await session.commit()
    return Message(message="Agent deactivated.")
