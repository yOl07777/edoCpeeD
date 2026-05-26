from __future__ import annotations

import json
from typing import Any


def tool_result_payload(component: str, **kwargs: Any) -> dict[str, Any]:
    payload = {"type": component, "provider": "deepseek"}
    payload.update(kwargs)
    return payload


def coerce_tool_result(value: Any = None, **kwargs: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        data = dict(value)
    elif isinstance(value, str):
        try:
            data = json.loads(value)
            if not isinstance(data, dict):
                data = {"content": value}
        except json.JSONDecodeError:
            data = {"content": value}
    else:
        data = {}
    data.update({key: val for key, val in kwargs.items() if val is not None})
    tool_name = data.get("toolName") or data.get("name") or data.get("tool") or "tool"
    status = data.get("status") or ("error" if data.get("error") else "success")
    return {
        "toolName": str(tool_name),
        "status": str(status),
        "content": data.get("content", data.get("result", "")),
        "error": data.get("error"),
        "toolUseId": data.get("toolUseId") or data.get("tool_call_id") or data.get("id"),
    }


def summary_for(result: dict[str, Any]) -> str:
    name = result["toolName"]
    status = result["status"]
    if status == "success":
        return f"{name} completed"
    if status == "canceled":
        return f"{name} canceled"
    if status in {"rejected", "denied"}:
        return f"{name} rejected"
    if result.get("error"):
        return f"{name} failed: {result['error']}"
    return f"{name}: {status}"

