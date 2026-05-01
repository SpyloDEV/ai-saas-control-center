from fastapi import APIRouter

from app.api.routes import (
    agents,
    analytics,
    api_keys,
    audit_logs,
    auth,
    documents,
    executions,
    webhooks,
    workflows,
    workspaces,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(workspaces.router)
api_router.include_router(agents.router)
api_router.include_router(documents.router)
api_router.include_router(workflows.router)
api_router.include_router(executions.router)
api_router.include_router(analytics.router)
api_router.include_router(api_keys.router)
api_router.include_router(audit_logs.router)
api_router.include_router(webhooks.router)
