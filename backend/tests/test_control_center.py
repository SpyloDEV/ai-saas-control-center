from collections.abc import Awaitable, Callable
from typing import Any

from httpx import AsyncClient

from tests.conftest import create_agent, create_workflow


async def test_agent_crud_flow(
    client: AsyncClient,
    auth_headers: dict[str, str],
    create_workspace: Callable[..., Awaitable[dict[str, Any]]],
) -> None:
    workspace = await create_workspace()
    agent = await create_agent(client, auth_headers, workspace["id"])

    list_response = await client.get(
        "/api/v1/agents",
        headers=auth_headers,
        params={"workspace_id": workspace["id"]},
    )
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1

    update_response = await client.patch(
        f"/api/v1/agents/{agent['id']}",
        headers=auth_headers,
        json={"temperature": 0.4, "status": "inactive"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["temperature"] == 0.4


async def test_document_upload_runs_mock_extraction(
    client: AsyncClient,
    auth_headers: dict[str, str],
    create_workspace: Callable[..., Awaitable[dict[str, Any]]],
) -> None:
    workspace = await create_workspace()
    response = await client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        data={"workspace_id": workspace["id"]},
        files={
            "file": (
                "invoice.txt",
                b"Invoice INV-2026-0428 total 1299 due date May 15",
                "text/plain",
            )
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["status"] == "completed"
    assert body["extracted_result"]["document_type"] == "invoice"


async def test_workflow_execution_writes_logs(
    client: AsyncClient,
    auth_headers: dict[str, str],
    create_workspace: Callable[..., Awaitable[dict[str, Any]]],
) -> None:
    workspace = await create_workspace()
    workflow = await create_workflow(client, auth_headers, workspace["id"])

    run_response = await client.post(
        f"/api/v1/workflows/{workflow['id']}/run",
        headers=auth_headers,
    )
    assert run_response.status_code == 200, run_response.text
    execution = run_response.json()
    assert execution["status"] == "completed"
    assert execution["result"]["summary"] == "Workflow completed."

    logs_response = await client.get(
        f"/api/v1/executions/{execution['id']}/logs",
        headers=auth_headers,
    )
    assert logs_response.status_code == 200
    messages = [item["message"] for item in logs_response.json()]
    assert "Workflow execution completed." in messages


async def test_workspace_permissions_block_foreign_documents(
    client: AsyncClient,
    auth_headers: dict[str, str],
    register_user: Callable[..., Awaitable[dict[str, Any]]],
    create_workspace: Callable[..., Awaitable[dict[str, Any]]],
) -> None:
    workspace = await create_workspace()
    other = await register_user(email="viewer@example.com")
    other_headers = {"Authorization": f"Bearer {other['access_token']}"}

    response = await client.get(
        "/api/v1/documents",
        headers=other_headers,
        params={"workspace_id": workspace["id"]},
    )
    assert response.status_code == 403


async def test_api_keys_and_audit_logs(
    client: AsyncClient,
    auth_headers: dict[str, str],
    create_workspace: Callable[..., Awaitable[dict[str, Any]]],
) -> None:
    workspace = await create_workspace()
    create_response = await client.post(
        "/api/v1/api-keys",
        headers=auth_headers,
        json={"workspace_id": workspace["id"], "name": "Backend SDK"},
    )
    assert create_response.status_code == 201, create_response.text
    assert create_response.json()["api_key"].startswith("sk_live_")

    audit_response = await client.get(
        "/api/v1/audit-logs",
        headers=auth_headers,
        params={"workspace_id": workspace["id"]},
    )
    assert audit_response.status_code == 200
    actions = {item["action"] for item in audit_response.json()}
    assert {"workspace_created", "api_key_created"}.issubset(actions)


async def test_analytics_overview(
    client: AsyncClient,
    auth_headers: dict[str, str],
    create_workspace: Callable[..., Awaitable[dict[str, Any]]],
) -> None:
    workspace = await create_workspace()
    await create_agent(client, auth_headers, workspace["id"])
    workflow = await create_workflow(client, auth_headers, workspace["id"])
    await client.post(f"/api/v1/workflows/{workflow['id']}/run", headers=auth_headers)

    response = await client.get(
        "/api/v1/analytics/overview",
        headers=auth_headers,
        params={"workspace_id": workspace["id"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_agents"] == 1
    assert body["total_workflows"] == 1
    assert body["total_executions"] == 1
    assert body["success_rate"] == 100.0
