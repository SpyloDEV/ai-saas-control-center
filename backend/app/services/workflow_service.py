from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.models.enums import ExecutionStatus, WorkflowStatus
from app.models.workflow import Execution, Workflow, WorkflowStep
from app.repositories.control_center import ControlCenterRepository
from app.services.audit_log_service import AuditLogService


class WorkflowService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = ControlCenterRepository(session)
        self.audit_logs = AuditLogService(session)

    async def create_workflow(self, *, user_id: str, data: dict) -> Workflow:
        workspace_id = data["workspace_id"]
        if not await self.repository.ensure_workspace_member(
            workspace_id=workspace_id,
            user_id=user_id,
        ):
            raise PermissionDeniedError("You do not have access to this workspace.")
        workflow = await self.repository.create_workflow(
            data={**data, "created_by": user_id},
        )
        await self.audit_logs.record(
            action="workflow_created",
            workspace_id=workspace_id,
            actor_id=user_id,
            target_type="workflow",
            target_id=workflow.id,
        )
        return workflow

    async def list_workflows(
        self,
        *,
        user_id: str,
        workspace_id: str,
    ) -> list[Workflow]:
        if not await self.repository.ensure_workspace_member(
            workspace_id=workspace_id,
            user_id=user_id,
        ):
            raise PermissionDeniedError("You do not have access to this workspace.")
        return await self.repository.list_workflows(
            user_id=user_id,
            workspace_id=workspace_id,
        )

    async def get_workflow(self, *, workflow_id: str, user_id: str) -> Workflow:
        workflow = await self.repository.get_workflow_for_user(
            workflow_id=workflow_id,
            user_id=user_id,
        )
        if workflow is None:
            raise NotFoundError("Workflow not found.")
        return workflow

    async def update_workflow(
        self,
        *,
        workflow_id: str,
        user_id: str,
        data: dict,
    ) -> Workflow:
        workflow = await self.get_workflow(workflow_id=workflow_id, user_id=user_id)
        for field, value in data.items():
            setattr(workflow, field, value)
        return workflow

    async def activate(self, *, workflow_id: str, user_id: str) -> Workflow:
        workflow = await self.get_workflow(workflow_id=workflow_id, user_id=user_id)
        workflow.status = WorkflowStatus.ACTIVE
        return workflow

    async def pause(self, *, workflow_id: str, user_id: str) -> Workflow:
        workflow = await self.get_workflow(workflow_id=workflow_id, user_id=user_id)
        workflow.status = WorkflowStatus.PAUSED
        return workflow

    async def add_step(
        self,
        *,
        workflow_id: str,
        user_id: str,
        data: dict,
    ) -> WorkflowStep:
        await self.get_workflow(workflow_id=workflow_id, user_id=user_id)
        return await self.repository.add_step(data={**data, "workflow_id": workflow_id})

    async def list_steps(
        self,
        *,
        workflow_id: str,
        user_id: str,
    ) -> list[WorkflowStep]:
        await self.get_workflow(workflow_id=workflow_id, user_id=user_id)
        return await self.repository.list_steps(workflow_id=workflow_id)

    async def create_execution(
        self,
        *,
        workflow_id: str,
        user_id: str,
        trigger: str,
    ) -> Execution:
        workflow = await self.get_workflow(workflow_id=workflow_id, user_id=user_id)
        execution = await self.repository.create_execution(
            data={
                "workspace_id": workflow.workspace_id,
                "workflow_id": workflow.id,
                "status": ExecutionStatus.QUEUED,
                "trigger": trigger,
            }
        )
        await self.audit_logs.record(
            action="workflow_executed",
            workspace_id=workflow.workspace_id,
            actor_id=user_id,
            target_type="execution",
            target_id=execution.id,
            metadata={"workflow_id": workflow_id, "trigger": trigger},
        )
        return execution
