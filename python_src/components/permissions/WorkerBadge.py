from __future__ import annotations

from typing import Any


async def WorkerBadge(*args: Any, **kwargs: Any) -> dict[str, Any]:
    worker = kwargs.get("worker") or kwargs.get("agent") or (args[0] if args else {}) or {}
    name = worker.get("name") if isinstance(worker, dict) else str(worker)
    return {
        "type": "worker_badge",
        "provider": "deepseek",
        "name": name or "worker",
        "status": kwargs.get("status", "active"),
    }


__all__ = ["WorkerBadge"]
