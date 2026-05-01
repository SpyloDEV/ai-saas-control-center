from fastapi import APIRouter, Query, status

from app.api.dependencies import CurrentUser, DbSession
from app.schemas.api_key import ApiKeyCreate, ApiKeyCreateResponse, ApiKeyRead
from app.schemas.common import Message
from app.services.api_key_service import ApiKeyService

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


@router.post(
    "", response_model=ApiKeyCreateResponse, status_code=status.HTTP_201_CREATED
)
async def create_api_key(
    payload: ApiKeyCreate,
    current_user: CurrentUser,
    session: DbSession,
) -> ApiKeyCreateResponse:
    raw_key, record = await ApiKeyService(session).create_api_key(
        user_id=current_user.id,
        workspace_id=payload.workspace_id,
        name=payload.name,
    )
    await session.commit()
    await session.refresh(record)
    return ApiKeyCreateResponse(api_key=raw_key, record=record)


@router.get("", response_model=list[ApiKeyRead])
async def list_api_keys(
    current_user: CurrentUser,
    session: DbSession,
    workspace_id: str = Query(...),
) -> list[ApiKeyRead]:
    return await ApiKeyService(session).list_api_keys(
        user_id=current_user.id,
        workspace_id=workspace_id,
    )


@router.delete("/{api_key_id}", response_model=Message)
async def revoke_api_key(
    api_key_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> Message:
    await ApiKeyService(session).revoke_api_key(
        user_id=current_user.id,
        api_key_id=api_key_id,
    )
    await session.commit()
    return Message(message="API key revoked.")
