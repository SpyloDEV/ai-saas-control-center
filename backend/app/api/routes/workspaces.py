from fastapi import APIRouter, status

from app.api.dependencies import CurrentUser, DbSession
from app.schemas.workspace import (
    TeamInviteRequest,
    WorkspaceCreate,
    WorkspaceMemberRead,
    WorkspaceRead,
    WorkspaceUpdate,
)
from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.post("", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    payload: WorkspaceCreate,
    current_user: CurrentUser,
    session: DbSession,
) -> WorkspaceRead:
    workspace = await WorkspaceService(session).create_workspace(
        user_id=current_user.id,
        name=payload.name,
        slug=payload.slug,
    )
    await session.commit()
    await session.refresh(workspace)
    return workspace


@router.get("", response_model=list[WorkspaceRead])
async def list_workspaces(
    current_user: CurrentUser,
    session: DbSession,
) -> list[WorkspaceRead]:
    return await WorkspaceService(session).list_workspaces(user_id=current_user.id)


@router.get("/{workspace_id}", response_model=WorkspaceRead)
async def get_workspace(
    workspace_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> WorkspaceRead:
    return await WorkspaceService(session).get_workspace(
        workspace_id=workspace_id,
        user_id=current_user.id,
    )


@router.patch("/{workspace_id}", response_model=WorkspaceRead)
async def update_workspace(
    workspace_id: str,
    payload: WorkspaceUpdate,
    current_user: CurrentUser,
    session: DbSession,
) -> WorkspaceRead:
    workspace = await WorkspaceService(session).update_workspace(
        workspace_id=workspace_id,
        user_id=current_user.id,
        data=payload.model_dump(exclude_unset=True),
    )
    await session.commit()
    await session.refresh(workspace)
    return workspace


@router.post(
    "/{workspace_id}/members",
    response_model=WorkspaceMemberRead,
    status_code=status.HTTP_201_CREATED,
)
async def invite_member(
    workspace_id: str,
    payload: TeamInviteRequest,
    current_user: CurrentUser,
    session: DbSession,
) -> WorkspaceMemberRead:
    member = await WorkspaceService(session).invite_member(
        workspace_id=workspace_id,
        invited_by_user_id=current_user.id,
        email=payload.email,
        role=payload.role,
    )
    await session.commit()
    await session.refresh(member)
    return member
