from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent
from app.models.document import Document
from app.models.workflow import Execution, Workflow
from app.models.workspace import WorkspaceMember
from app.repositories.control_center import ControlCenterRepository


class AnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ControlCenterRepository(session)

    async def overview(self, *, user_id: str, workspace_id: str) -> dict:
        base = await self.repository.analytics(
            user_id=user_id, workspace_id=workspace_id
        )
        totals = {}
        for key, model in {
            "total_agents": Agent,
            "total_documents": Document,
            "total_workflows": Workflow,
        }.items():
            value = await self.session.scalar(
                select(func.count(model.id))
                .join(
                    WorkspaceMember, WorkspaceMember.workspace_id == model.workspace_id
                )
                .where(
                    model.workspace_id == workspace_id,
                    WorkspaceMember.user_id == user_id,
                )
            )
            totals[key] = int(value or 0)
        return {**totals, **base}

    async def executions_per_day(
        self,
        *,
        user_id: str,
        workspace_id: str,
        days: int = 7,
    ) -> list[dict[str, int | str]]:
        since = datetime.now(UTC) - timedelta(days=days - 1)
        result = await self.session.execute(
            select(Execution.created_at, Execution.id)
            .join(
                WorkspaceMember, WorkspaceMember.workspace_id == Execution.workspace_id
            )
            .where(
                Execution.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
                Execution.created_at >= since,
            )
        )
        counts: dict[str, int] = {}
        for created_at, _ in result.all():
            key = created_at.date().isoformat()
            counts[key] = counts.get(key, 0) + 1
        days_out: list[dict[str, int | str]] = []
        for offset in range(days):
            date_key = (since + timedelta(days=offset)).date().isoformat()
            days_out.append({"date": date_key, "count": counts.get(date_key, 0)})
        return days_out
