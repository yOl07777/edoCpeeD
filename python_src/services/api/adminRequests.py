"""Local admin request state for migration compatibility."""

from __future__ import annotations

import time
import uuid
from typing import Any

_REQUESTS: list[dict[str, Any]] = []


async def checkAdminRequestEligibility(user: dict[str, Any] | None = None, config: dict[str, Any] | None = None) -> dict[str, Any]:
    config = config or {}
    user = user or {}
    allowed = bool(config.get("allowAdminRequests", True)) and not bool(user.get("disabled"))
    return {"eligible": allowed, "reason": None if allowed else "admin requests disabled"}


async def createAdminRequest(kind: str, payload: dict[str, Any] | None = None, user: dict[str, Any] | None = None) -> dict[str, Any]:
    eligibility = await checkAdminRequestEligibility(user)
    if not eligibility["eligible"]:
        return {"created": False, **eligibility}
    request = {
        "id": f"admin-{uuid.uuid4().hex[:12]}",
        "kind": kind,
        "payload": payload or {},
        "user": user or {},
        "status": "pending",
        "created_at": time.time(),
    }
    _REQUESTS.append(request)
    return {"created": True, "request": request}


async def getMyAdminRequests(user_id: str | None = None) -> list[dict[str, Any]]:
    if user_id is None:
        return list(_REQUESTS)
    return [request for request in _REQUESTS if str(request.get("user", {}).get("id")) == str(user_id)]

