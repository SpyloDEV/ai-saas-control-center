from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.api.dependencies import CurrentUser, DbSession
from app.schemas.common import Message
from app.schemas.workflow import ExecutionLogRead, ExecutionRead
from app.services.execution_service import ExecutionService
from app.websockets.manager import websocket_manager

router = APIRouter(prefix="/executions", tags=["Executions"])


@router.get("", response_model=list[ExecutionRead])
async def list_executions(
    current_user: CurrentUser,
    session: DbSession,
    workspace_id: str = Query(...),
) -> list[ExecutionRead]:
    return await ExecutionService(session).list_executions(
        user_id=current_user.id,
        workspace_id=workspace_id,
    )


@router.get("/{execution_id}", response_model=ExecutionRead)
async def get_execution(
    execution_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> ExecutionRead:
    return await ExecutionService(session).get_execution(
        execution_id=execution_id,
        user_id=current_user.id,
    )


@router.get("/{execution_id}/logs", response_model=list[ExecutionLogRead])
async def list_execution_logs(
    execution_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> list[ExecutionLogRead]:
    return await ExecutionService(session).list_logs(
        execution_id=execution_id,
        user_id=current_user.id,
    )


@router.post("/{execution_id}/cancel", response_model=ExecutionRead)
async def cancel_execution(
    execution_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> ExecutionRead:
    execution = await ExecutionService(session).cancel_execution(
        execution_id=execution_id,
        user_id=current_user.id,
    )
    await session.commit()
    await session.refresh(execution)
    return execution


@router.post("/{execution_id}/retry", response_model=Message)
async def retry_execution(
    execution_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> Message:
    await ExecutionService(session).get_execution(
        execution_id=execution_id,
        user_id=current_user.id,
    )
    return Message(message="Retry accepted. Background worker can enqueue this task.")


@router.websocket("/ws/{execution_id}")
async def execution_logs_socket(websocket: WebSocket, execution_id: str) -> None:
    await websocket_manager.connect(execution_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(execution_id, websocket)
