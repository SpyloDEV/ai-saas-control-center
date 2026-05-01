from fastapi import APIRouter, File, Form, Query, UploadFile, status

from app.api.dependencies import CurrentUser, DbSession
from app.schemas.common import Message
from app.schemas.document import DocumentRead
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/upload",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    current_user: CurrentUser,
    session: DbSession,
    workspace_id: str = Form(...),
    file: UploadFile = File(...),
) -> DocumentRead:
    document = await DocumentService(session).upload_document(
        workspace_id=workspace_id,
        user_id=current_user.id,
        filename=file.filename or "document",
        content_type=file.content_type or "application/octet-stream",
        file=file.file,
    )
    await session.commit()
    await session.refresh(document)
    return document


@router.get("", response_model=list[DocumentRead])
async def list_documents(
    current_user: CurrentUser,
    session: DbSession,
    workspace_id: str = Query(...),
) -> list[DocumentRead]:
    return await DocumentService(session).list_documents(
        user_id=current_user.id,
        workspace_id=workspace_id,
    )


@router.get("/{document_id}", response_model=DocumentRead)
async def get_document(
    document_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> DocumentRead:
    return await DocumentService(session).get_document(
        document_id=document_id,
        user_id=current_user.id,
    )


@router.delete("/{document_id}", response_model=Message)
async def delete_document(
    document_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> Message:
    document = await DocumentService(session).get_document(
        document_id=document_id,
        user_id=current_user.id,
    )
    await session.delete(document)
    await session.commit()
    return Message(message="Document deleted.")
