from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/{workflow_id}/{secret}")
async def receive_webhook(
    workflow_id: str, secret: str, payload: dict[str, Any]
) -> dict[str, Any]:
    return {
        "workflow_id": workflow_id,
        "received": True,
        "secret_prefix": secret[:6],
        "payload_keys": sorted(payload.keys()),
    }
