import asyncio

from app.db.session import AsyncSessionLocal
from app.models.workflow import Execution
from app.services.execution_service import ExecutionService
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.run_workflow_execution")
def run_workflow_execution(execution_id: str) -> None:
    asyncio.run(_run_execution(execution_id))


async def _run_execution(execution_id: str) -> None:
    async with AsyncSessionLocal() as session:
        execution = await session.get(Execution, execution_id)
        if execution is not None:
            await ExecutionService(session).run_execution(execution=execution)
            await session.commit()
