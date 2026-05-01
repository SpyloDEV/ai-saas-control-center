import asyncio

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.agent import Agent
from app.models.document import Document
from app.models.enums import (
    AgentStatus,
    DocumentStatus,
    ExecutionStatus,
    WorkspaceRole,
)
from app.models.user import User
from app.models.workflow import Execution, ExecutionLog, Workflow, WorkflowStep
from app.models.workspace import Workspace, WorkspaceMember
from app.services.audit_log_service import AuditLogService


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        user = User(
            email="demo@acme.ai",
            full_name="Demo Operator",
            hashed_password=hash_password("SecurePass123!"),
        )
        session.add(user)
        await session.flush()

        workspace = Workspace(name="Acme AI", slug="acme-ai")
        session.add(workspace)
        await session.flush()

        session.add(
            WorkspaceMember(
                workspace_id=workspace.id,
                user_id=user.id,
                role=WorkspaceRole.OWNER,
            )
        )

        agents = [
            Agent(
                workspace_id=workspace.id,
                name="Invoice Extractor",
                description="Extracts structured invoice fields.",
                role="document_processor",
                instructions="Extract totals, dates, vendors, and line items.",
                status=AgentStatus.ACTIVE,
            ),
            Agent(
                workspace_id=workspace.id,
                name="Revenue QA",
                description="Validates extraction results before export.",
                role="validation_agent",
                instructions="Flag missing or low-confidence fields.",
                status=AgentStatus.ACTIVE,
            ),
        ]
        session.add_all(agents)
        await session.flush()

        document = Document(
            workspace_id=workspace.id,
            uploaded_by=user.id,
            filename="northstar-invoice.pdf",
            content_type="application/pdf",
            size_bytes=182044,
            status=DocumentStatus.COMPLETED,
            extracted_result={
                "document_type": "invoice",
                "vendor_name": "Northstar AI Labs",
                "total_amount": 1299.0,
                "confidence_score": 0.93,
            },
            validation_warnings=[],
        )
        session.add(document)
        await session.flush()

        workflow = Workflow(
            workspace_id=workspace.id,
            name="Document Intake",
            description="Extract, validate, and notify operators.",
            created_by=user.id,
        )
        session.add(workflow)
        await session.flush()
        session.add_all(
            [
                WorkflowStep(
                    workflow_id=workflow.id,
                    step_order=1,
                    name="Extract data",
                    step_type="ai_extraction",
                    config={},
                ),
                WorkflowStep(
                    workflow_id=workflow.id,
                    step_order=2,
                    name="Validate result",
                    step_type="validation",
                    config={},
                ),
            ]
        )

        execution = Execution(
            workspace_id=workspace.id,
            workflow_id=workflow.id,
            status=ExecutionStatus.COMPLETED,
            trigger="manual",
            result={"summary": "Workflow completed.", "steps": 2},
            duration_ms=812,
        )
        session.add(execution)
        await session.flush()
        session.add(
            ExecutionLog(
                execution_id=execution.id,
                message="Workflow execution completed.",
                metadata_json={"duration_ms": 812},
            )
        )

        audit = AuditLogService(session)
        for action, target_type, target_id in [
            ("user_registered", "user", user.id),
            ("workspace_created", "workspace", workspace.id),
            ("agent_created", "agent", agents[0].id),
            ("document_uploaded", "document", document.id),
            ("workflow_executed", "execution", execution.id),
        ]:
            await audit.record(
                action=action,
                workspace_id=workspace.id,
                actor_id=user.id,
                target_type=target_type,
                target_id=target_id,
            )

        await session.commit()
        print("Seeded demo account demo@acme.ai / SecurePass123!")


if __name__ == "__main__":
    asyncio.run(seed())
