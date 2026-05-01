from fastapi import APIRouter, Query

from app.api.dependencies import CurrentUser, DbSession
from app.schemas.analytics import AnalyticsOverview, ExecutionsPerDay
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=AnalyticsOverview)
async def overview(
    current_user: CurrentUser,
    session: DbSession,
    workspace_id: str = Query(...),
) -> AnalyticsOverview:
    return await AnalyticsService(session).overview(
        user_id=current_user.id,
        workspace_id=workspace_id,
    )


@router.get("/executions-per-day", response_model=list[ExecutionsPerDay])
async def executions_per_day(
    current_user: CurrentUser,
    session: DbSession,
    workspace_id: str = Query(...),
) -> list[ExecutionsPerDay]:
    return await AnalyticsService(session).executions_per_day(
        user_id=current_user.id,
        workspace_id=workspace_id,
    )
