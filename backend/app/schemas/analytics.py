from pydantic import BaseModel


class AnalyticsOverview(BaseModel):
    total_agents: int
    total_documents: int
    total_workflows: int
    total_executions: int
    success_rate: float
    failed_executions: int
    average_processing_time_ms: float | None


class ExecutionsPerDay(BaseModel):
    date: str
    count: int
