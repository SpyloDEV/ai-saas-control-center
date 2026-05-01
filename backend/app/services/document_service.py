from pathlib import Path
from typing import BinaryIO

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, PermissionDeniedError, ValidationAppError
from app.models.document import Document
from app.models.enums import DocumentStatus
from app.repositories.control_center import ControlCenterRepository
from app.services.audit_log_service import AuditLogService

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "text/csv",
    "text/plain",
}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


class DocumentService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = ControlCenterRepository(session)
        self.audit_logs = AuditLogService(session)

    async def upload_document(
        self,
        *,
        workspace_id: str,
        user_id: str,
        filename: str,
        content_type: str,
        file: BinaryIO,
    ) -> Document:
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise ValidationAppError("Unsupported document type.")
        content = file.read()
        if not content:
            raise ValidationAppError("Uploaded documents cannot be empty.")
        if len(content) > MAX_UPLOAD_BYTES:
            raise ValidationAppError("Document exceeds the 10 MB upload limit.")
        if not await self.repository.ensure_workspace_member(
            workspace_id=workspace_id,
            user_id=user_id,
        ):
            raise PermissionDeniedError("You do not have access to this workspace.")
        safe_filename = Path(filename).name
        document = await self.repository.create_document(
            data={
                "workspace_id": workspace_id,
                "uploaded_by": user_id,
                "filename": safe_filename,
                "content_type": content_type,
                "size_bytes": len(content),
                "status": DocumentStatus.PROCESSING,
            }
        )
        await self.process_document(document=document, content=content)
        await self.audit_logs.record(
            action="document_uploaded",
            workspace_id=workspace_id,
            actor_id=user_id,
            target_type="document",
            target_id=document.id,
            metadata={"filename": safe_filename, "content_type": content_type},
        )
        return document

    async def process_document(self, *, document: Document, content: bytes) -> Document:
        text = content.decode("utf-8", errors="ignore")
        result = self._mock_extract(document.filename, text)
        warnings = self._validation_warnings(result)
        document.status = DocumentStatus.COMPLETED
        document.extracted_result = result
        document.validation_warnings = warnings
        return document

    async def list_documents(
        self,
        *,
        user_id: str,
        workspace_id: str,
    ) -> list[Document]:
        if not await self.repository.ensure_workspace_member(
            workspace_id=workspace_id,
            user_id=user_id,
        ):
            raise PermissionDeniedError("You do not have access to this workspace.")
        return await self.repository.list_documents(
            user_id=user_id,
            workspace_id=workspace_id,
        )

    async def get_document(self, *, document_id: str, user_id: str) -> Document:
        document = await self.repository.get_document_for_user(
            document_id=document_id,
            user_id=user_id,
        )
        if document is None:
            raise NotFoundError("Document not found.")
        return document

    def _mock_extract(self, filename: str, text: str) -> dict:
        lowered = f"{filename} {text}".lower()
        is_invoice = any(token in lowered for token in ["invoice", "rechnung", "inv-"])
        total = 1299.0 if "1299" in lowered else 482.5
        return {
            "document_type": "invoice" if is_invoice else "business_document",
            "vendor_name": "Northstar AI Labs" if is_invoice else "Acme Operations",
            "customer_name": "Demo Workspace",
            "invoice_number": "INV-2026-0428" if is_invoice else None,
            "total_amount": total,
            "currency": "USD",
            "tax_amount": round(total * 0.19, 2),
            "confidence_score": 0.93 if is_invoice else 0.78,
            "line_items": [
                {
                    "description": "AI operations platform usage",
                    "quantity": 1,
                    "amount": total,
                }
            ],
        }

    def _validation_warnings(self, result: dict) -> list[str]:
        warnings: list[str] = []
        for field in ["vendor_name", "invoice_number", "total_amount", "currency"]:
            if not result.get(field):
                warnings.append(f"Missing important field: {field}")
        if result.get("confidence_score", 0) < 0.85:
            warnings.append("Confidence score is below review threshold.")
        return warnings
