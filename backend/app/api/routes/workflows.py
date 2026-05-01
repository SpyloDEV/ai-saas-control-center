from fastapi import APIRouter, Query, status

from app.api.dependencies import CurrentUser, DbSession
from app.schemas.common import Message
from app.schemas.workflow import (
    ExecutionRead,
    WorkflowCreate,
    WorkflowRead,
    WorkflowStepCreate,
    WorkflowStepRead,
    WorkflowUpdate,
)
from app.services.execution_service import ExecutionService
from app.services.workflow_service import WorkflowService

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.post("", response_model=WorkflowRead, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    payload: WorkflowCreate,
    current_user: CurrentUser,
    session: DbSession,
) -> WorkflowRead:
    workflow = await WorkflowService(session).create_workflow(
        user_id=current_user.id,
        data=payload.model_dump(),
    )
    await session.commit()
    await session.refresh(workflow)
    return workflow


@router.get("", response_model=list[WorkflowRead])
async def list_workflows(
    current_user: CurrentUser,
    session: DbSession,
    workspace_id: str = Query(...),
) -> list[WorkflowRead]:
    return await WorkflowService(session).list_workflows(
        user_id=current_user.id,
        workspace_id=workspace_id,
    )


@router.get("/{workflow_id}", response_model=WorkflowRead)
async def get_workflow(
    workflow_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> WorkflowRead:
    return await WorkflowService(session).get_workflow(
        workflow_id=workflow_id,
        user_id=current_user.id,
    )


@router.patch("/{workflow_id}", response_model=WorkflowRead)
async def update_workflow(
    workflow_id: str,
    payload: WorkflowUpdate,
    current_user: CurrentUser,
    session: DbSession,
) -> WorkflowRead:
    workflow = await WorkflowService(session).update_workflow(
        workflow_id=workflow_id,
        user_id=current_user.id,
        data=payload.model_dump(exclude_unset=True),
    )
    await session.commit()
    await session.refresh(workflow)
    return workflow


@router.delete("/{workflow_id}", response_model=Message)
async def delete_workflow(
    workflow_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> Message:
    workflow = await WorkflowService(session).get_workflow(
        workflow_id=workflow_id,
        user_id=current_user.id,
    )
    await session.delete(workflow)
    await session.commit()
    return Message(message="Workflow deleted.")


@router.post("/{workflow_id}/activate", response_model=WorkflowRead)
async def activate_workflow(
    workflow_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> WorkflowRead:
    workflow = await WorkflowService(session).activate(
        workflow_id=workflow_id,
        user_id=current_user.id,
    )
    await session.commit()
    await session.refresh(workflow)
    return workflow


@router.post("/{workflow_id}/pause", response_model=WorkflowRead)
async def pause_workflow(
    workflow_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> WorkflowRead:
    workflow = await WorkflowService(session).pause(
        workflow_id=workflow_id,
        user_id=current_user.id,
    )
    await session.commit()
    await session.refresh(workflow)
    return workflow


@router.post(
    "/{workflow_id}/steps",
    response_model=WorkflowStepRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_step(
    workflow_id: str,
    payload: WorkflowStepCreate,
    current_user: CurrentUser,
    session: DbSession,
) -> WorkflowStepRead:
    step = await WorkflowService(session).add_step(
        workflow_id=workflow_id,
        user_id=current_user.id,
        data=payload.model_dump(),
    )
    await session.commit()
    await session.refresh(step)
    return step


@router.get("/{workflow_id}/steps", response_model=list[WorkflowStepRead])
async def list_steps(
    workflow_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> list[WorkflowStepRead]:
    return await WorkflowService(session).list_steps(
        workflow_id=workflow_id,
        user_id=current_user.id,
    )


@router.post("/{workflow_id}/run", response_model=ExecutionRead)
async def run_workflow(
    workflow_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> ExecutionRead:
    execution = await WorkflowService(session).create_execution(
        workflow_id=workflow_id,
        user_id=current_user.id,
        trigger="manual",
    )
    await ExecutionService(session).run_execution(execution=execution)
    await session.commit()
    await session.refresh(execution)
    return execution
