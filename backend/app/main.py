from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import install_exception_handlers
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        summary="Backend API for an AI SaaS operations control center.",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        openapi_tags=[
            {"name": "Authentication", "description": "JWT login and identity."},
            {"name": "Workspaces", "description": "Workspace and team access."},
            {"name": "Agents", "description": "AI agent configuration."},
            {"name": "Documents", "description": "Document uploads and AI extraction."},
            {"name": "Workflows", "description": "Automation workflow management."},
            {"name": "Executions", "description": "Execution history and live logs."},
            {"name": "Analytics", "description": "SaaS operating metrics."},
            {"name": "API Keys", "description": "Workspace API key management."},
            {"name": "Audit Logs", "description": "Workspace activity trail."},
            {"name": "Health", "description": "Service readiness checks."},
        ],
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    install_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/health", tags=["Health"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "environment": settings.environment}

    return app


app = create_app()
