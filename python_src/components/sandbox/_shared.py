from __future__ import annotations

from typing import Any


def sandbox_payload(component: str, **kwargs: Any) -> dict[str, Any]:
    payload = {"type": component, "provider": "deepseek"}
    payload.update(kwargs)
    return payload


def normalize_dependency(dep: Any, index: int = 0) -> dict[str, Any]:
    if isinstance(dep, dict):
        name = dep.get("name") or dep.get("id") or f"dependency-{index}"
        installed = bool(dep.get("installed", dep.get("ok", False)))
        version = dep.get("version")
    else:
        name = str(dep)
        installed = False
        version = None
    return {"index": index, "name": str(name), "installed": installed, "version": version}

