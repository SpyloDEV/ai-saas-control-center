from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_key import ApiKey
from app.models.audit_log import AuditLog
from app.models.document import Document
from app.models.enums import ExecutionStatus
from app.models.workflow import Execution, ExecutionLog, Workflow, WorkflowStep
from app.models.workspace import WorkspaceMember


class ControlCenterRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def ensure_workspace_member(self, *, workspace_id: str, user_id: str) -> bool:
        member = await self.session.scalar(
            select(WorkspaceMember.id).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        )
        return member is not None

    async def create_document(self, *, data: dict) -> Document:
        document = Document(**data)
        self.session.add(document)
        await self.session.flush()
        return document

    async def list_documents(
        self, *, user_id: str, workspace_id: str
    ) -> list[Document]:
        result = await self.session.execute(
            select(Document)
            .join(
                WorkspaceMember, WorkspaceMember.workspace_id == Document.workspace_id
            )
            .where(
                Document.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
            .order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_document_for_user(
        self, *, document_id: str, user_id: str
    ) -> Document | None:
        result = await self.session.execute(
            select(Document)
            .join(
                WorkspaceMember, WorkspaceMember.workspace_id == Document.workspace_id
            )
            .where(Document.id == document_id, WorkspaceMember.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_workflow(self, *, data: dict) -> Workflow:
        workflow = Workflow(**data)
        self.session.add(workflow)
        await self.session.flush()
        return workflow

    async def get_workflow_for_user(
        self, *, workflow_id: str, user_id: str
    ) -> Workflow | None:
        result = await self.session.execute(
            select(Workflow)
            .join(
                WorkspaceMember, WorkspaceMember.workspace_id == Workflow.workspace_id
            )
            .where(Workflow.id == workflow_id, WorkspaceMember.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_workflows(
        self, *, user_id: str, workspace_id: str
    ) -> list[Workflow]:
        result = await self.session.execute(
            select(Workflow)
            .join(
                WorkspaceMember, WorkspaceMember.workspace_id == Workflow.workspace_id
            )
            .where(
                Workflow.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
            .order_by(Workflow.created_at.desc())
        )
        return list(result.scalars().all())

    async def add_step(self, *, data: dict) -> WorkflowStep:
        step = WorkflowStep(**data)
        self.session.add(step)
        await self.session.flush()
        return step

    async def list_steps(self, *, workflow_id: str) -> list[WorkflowStep]:
        result = await self.session.execute(
            select(WorkflowStep)
            .where(WorkflowStep.workflow_id == workflow_id)
            .order_by(WorkflowStep.step_order.asc())
        )
        return list(result.scalars().all())

    async def create_execution(self, *, data: dict) -> Execution:
        execution = Execution(**data)
        self.session.add(execution)
        await self.session.flush()
        return execution

    async def get_execution_for_user(
        self,
        *,
        execution_id: str,
        user_id: str,
    ) -> Execution | None:
        result = await self.session.execute(
            select(Execution)
            .join(
                WorkspaceMember, WorkspaceMember.workspace_id == Execution.workspace_id
            )
            .where(Execution.id == execution_id, WorkspaceMember.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_executions(
        self, *, user_id: str, workspace_id: str
    ) -> list[Execution]:
        result = await self.session.execute(
            select(Execution)
            .join(
                WorkspaceMember, WorkspaceMember.workspace_id == Execution.workspace_id
            )
            .where(
                Execution.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
            .order_by(Execution.created_at.desc())
        )
        return list(result.scalars().all())

    async def create_log(self, *, data: dict) -> ExecutionLog:
        log = ExecutionLog(**data)
        self.session.add(log)
        await self.session.flush()
        return log

    async def list_logs(self, *, execution_id: str) -> list[ExecutionLog]:
        result = await self.session.execute(
            select(ExecutionLog)
            .where(ExecutionLog.execution_id == execution_id)
            .order_by(ExecutionLog.created_at.asc())
        )
        return list(result.scalars().all())

    async def create_api_key(self, *, data: dict) -> ApiKey:
        api_key = ApiKey(**data)
        self.session.add(api_key)
        await self.session.flush()
        return api_key

    async def list_api_keys(self, *, user_id: str, workspace_id: str) -> list[ApiKey]:
        result = await self.session.execute(
            select(ApiKey)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == ApiKey.workspace_id)
            .where(
                ApiKey.workspace_id == workspace_id, WorkspaceMember.user_id == user_id
            )
            .order_by(ApiKey.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_api_key_for_user(
        self, *, api_key_id: str, user_id: str
    ) -> ApiKey | None:
        result = await self.session.execute(
            select(ApiKey)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == ApiKey.workspace_id)
            .where(ApiKey.id == api_key_id, WorkspaceMember.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_audit_log(self, *, data: dict) -> AuditLog:
        log = AuditLog(**data)
        self.session.add(log)
        await self.session.flush()
        return log

    async def list_audit_logs(
        self, *, user_id: str, workspace_id: str
    ) -> list[AuditLog]:
        result = await self.session.execute(
            select(AuditLog)
            .join(
                WorkspaceMember, WorkspaceMember.workspace_id == AuditLog.workspace_id
            )
            .where(
                AuditLog.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
            .order_by(AuditLog.created_at.desc())
            .limit(30)
        )
        return list(result.scalars().all())

    async def analytics(self, *, user_id: str, workspace_id: str) -> dict:
        filters = [
            WorkspaceMember.user_id == user_id,
            WorkspaceMember.workspace_id == workspace_id,
        ]
        total_executions = await self.session.scalar(
            select(func.count(Execution.id))
            .join(
                WorkspaceMember, WorkspaceMember.workspace_id == Execution.workspace_id
            )
            .where(Execution.workspace_id == workspace_id, *filters)
        )
        completed = await self.session.scalar(
            select(func.count(Execution.id))
            .join(
                WorkspaceMember, WorkspaceMember.workspace_id == Execution.workspace_id
            )
            .where(
                Execution.workspace_id == workspace_id,
                Execution.status == ExecutionStatus.COMPLETED,
                *filters,
            )
        )
        failed = await self.session.scalar(
            select(func.count(Execution.id))
            .join(
                WorkspaceMember, WorkspaceMember.workspace_id == Execution.workspace_id
            )
            .where(
                Execution.workspace_id == workspace_id,
                Execution.status == ExecutionStatus.FAILED,
                *filters,
            )
        )
        avg_duration = await self.session.scalar(
            select(func.avg(Execution.duration_ms))
            .join(
                WorkspaceMember, WorkspaceMember.workspace_id == Execution.workspace_id
            )
            .where(Execution.workspace_id == workspace_id, *filters)
        )
        total = int(total_executions or 0)
        return {
            "total_executions": total,
            "failed_executions": int(failed or 0),
            "success_rate": (
                round((int(completed or 0) / total) * 100, 2) if total else 0.0
            ),
            "average_processing_time_ms": (
                round(float(avg_duration), 2) if avg_duration is not None else None
            ),
        }
