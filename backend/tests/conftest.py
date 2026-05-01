import os
from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import Any
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_control_center.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-control-center")
os.environ.setdefault("ENABLE_BACKGROUND_JOBS", "false")

import app.models  # noqa: E402, F401
from app.api import dependencies  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.main import app  # noqa: E402


def _engine_options(database_url: str) -> dict[str, Any]:
    if database_url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {"poolclass": NullPool}


test_engine = create_async_engine(
    os.environ["DATABASE_URL"],
    **_engine_options(os.environ["DATABASE_URL"]),
)
TestingSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def reset_database() -> AsyncGenerator[None, None]:
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator:
        async with TestingSessionLocal() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[dependencies.get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
async def register_user(
    client: AsyncClient,
) -> Callable[..., Awaitable[dict[str, Any]]]:
    async def _register_user(
        email: str | None = None,
        password: str = "SecurePass123!",
        full_name: str = "Control Center Founder",
    ) -> dict[str, Any]:
        user_email = email or f"founder-{uuid4().hex[:8]}@example.com"
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": user_email,
                "password": password,
                "full_name": full_name,
            },
        )
        assert response.status_code == 201, response.text
        return response.json()

    return _register_user


@pytest.fixture
async def auth_headers(
    register_user: Callable[..., Awaitable[dict[str, Any]]],
) -> dict[str, str]:
    account = await register_user(email="founder@example.com")
    return {"Authorization": f"Bearer {account['access_token']}"}


@pytest.fixture
async def create_workspace(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> Callable[..., Awaitable[dict[str, Any]]]:
    async def _create_workspace(name: str | None = None) -> dict[str, Any]:
        workspace_name = name or f"Acme AI {uuid4().hex[:6]}"
        response = await client.post(
            "/api/v1/workspaces",
            headers=auth_headers,
            json={"name": workspace_name},
        )
        assert response.status_code == 201, response.text
        return response.json()

    return _create_workspace


async def create_agent(
    client: AsyncClient,
    headers: dict[str, str],
    workspace_id: str,
) -> dict[str, Any]:
    response = await client.post(
        "/api/v1/agents",
        headers=headers,
        json={
            "workspace_id": workspace_id,
            "name": "Invoice Operations Agent",
            "description": "Extracts and validates invoices.",
            "role": "document_processor",
            "instructions": "Extract structured fields and flag missing values.",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


async def create_workflow(
    client: AsyncClient,
    headers: dict[str, str],
    workspace_id: str,
) -> dict[str, Any]:
    response = await client.post(
        "/api/v1/workflows",
        headers=headers,
        json={
            "workspace_id": workspace_id,
            "name": "Document Intake",
            "description": "Extract, validate, and notify the operations team.",
        },
    )
    assert response.status_code == 201, response.text
    workflow = response.json()
    for index, (name, step_type) in enumerate(
        [
            ("Extract data", "ai_extraction"),
            ("Validate result", "validation"),
            ("Notify team", "notification"),
        ],
        start=1,
    ):
        step_response = await client.post(
            f"/api/v1/workflows/{workflow['id']}/steps",
            headers=headers,
            json={
                "name": name,
                "step_type": step_type,
                "step_order": index,
                "config": {"channel": "operations"},
            },
        )
        assert step_response.status_code == 201, step_response.text
    return workflow
