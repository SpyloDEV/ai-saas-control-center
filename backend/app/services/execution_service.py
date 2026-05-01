from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.enums import ExecutionStatus, LogLevel
from app.models.workflow import Execution, ExecutionLog
from app.repositories.control_center import ControlCenterRepository
from app.websockets.manager import websocket_manager


class ExecutionService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = ControlCenterRepository(session)

    async def list_executions(
        self,
        *,
        user_id: str,
        workspace_id: str,
    ) -> list[Execution]:
        return await self.repository.list_executions(
            user_id=user_id,
            workspace_id=workspace_id,
        )

    async def get_execution(self, *, execution_id: str, user_id: str) -> Execution:
        execution = await self.repository.get_execution_for_user(
            execution_id=execution_id,
            user_id=user_id,
        )
        if execution is None:
            raise NotFoundError("Execution not found.")
        return execution

    async def list_logs(
        self,
        *,
        execution_id: str,
        user_id: str,
    ) -> list[ExecutionLog]:
        await self.get_execution(execution_id=execution_id, user_id=user_id)
        return await self.repository.list_logs(execution_id=execution_id)

    async def run_execution(self, *, execution: Execution) -> Execution:
        started_at = datetime.now(UTC)
        execution.status = ExecutionStatus.RUNNING
        await self._log(
            execution_id=execution.id,
            level=LogLevel.INFO,
            message="Workflow execution started.",
            metadata={"trigger": execution.trigger},
        )
        steps = (
            await self.repository.list_steps(workflow_id=execution.workflow_id)
            if execution.workflow_id
            else []
        )
        step_outputs: list[dict[str, Any]] = []
        try:
            context: dict[str, Any] = {"trigger": execution.trigger}
            for step in steps:
                await self._log(
                    execution_id=execution.id,
                    level=LogLevel.INFO,
                    message=f"Step started: {step.name}",
                    metadata={"step_id": step.id, "step_type": step.step_type},
                )
                output = self._run_step(
                    step_type=step.step_type, config=step.config, context=context
                )
                context[step.name] = output
                step_outputs.append(
                    {
                        "step_id": step.id,
                        "name": step.name,
                        "type": step.step_type,
                        "output": output,
                    }
                )
                await self._log(
                    execution_id=execution.id,
                    level=LogLevel.INFO,
                    message=f"Step completed: {step.name}",
                    metadata={"step_id": step.id, "output": output},
                )
            execution.status = ExecutionStatus.COMPLETED
            execution.result = {"steps": step_outputs, "summary": "Workflow completed."}
            await self._log(
                execution_id=execution.id,
                level=LogLevel.INFO,
                message="Workflow execution completed.",
                metadata={"steps": len(step_outputs)},
            )
        except Exception as exc:
            execution.status = ExecutionStatus.FAILED
            execution.error_message = str(exc)
            await self._log(
                execution_id=execution.id,
                level=LogLevel.ERROR,
                message="Workflow execution failed.",
                metadata={"error": str(exc)},
            )
        finally:
            duration = datetime.now(UTC) - started_at
            execution.duration_ms = int(duration.total_seconds() * 1000)
            await websocket_manager.broadcast_execution(
                execution.id,
                {
                    "type": "execution_status",
                    "execution_id": execution.id,
                    "status": execution.status,
                    "duration_ms": execution.duration_ms,
                },
            )
        return execution

    async def cancel_execution(self, *, execution_id: str, user_id: str) -> Execution:
        execution = await self.get_execution(execution_id=execution_id, user_id=user_id)
        execution.status = ExecutionStatus.CANCELLED
        await self._log(
            execution_id=execution.id,
            level=LogLevel.WARNING,
            message="Workflow execution cancelled.",
            metadata={},
        )
        return execution

    async def _log(
        self,
        *,
        execution_id: str,
        level: LogLevel,
        message: str,
        metadata: dict[str, Any],
    ) -> ExecutionLog:
        log = await self.repository.create_log(
            data={
                "execution_id": execution_id,
                "level": level,
                "message": message,
                "metadata_json": metadata,
            }
        )
        await websocket_manager.broadcast_execution(
            execution_id,
            {
                "type": "execution_log",
                "execution_id": execution_id,
                "level": level,
                "message": message,
                "metadata": metadata,
            },
        )
        return log

    def _run_step(
        self,
        *,
        step_type: str,
        config: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        if step_type == "ai_extraction":
            return {
                "document_type": "invoice",
                "confidence": 0.92,
                "fields": {"vendor": "Northstar AI Labs", "amount": 1299.0},
            }
        if step_type == "validation":
            return {"valid": True, "warnings": []}
        if step_type == "notification":
            return {"delivered": True, "channel": config.get("channel", "in_app")}
        if step_type == "http_request":
            return {"status_code": 200, "body": {"mock": True}}
        if step_type == "delay":
            return {"delayed_ms": int(config.get("milliseconds", 100))}
        return {"ok": True, "context_keys": sorted(context.keys())}
