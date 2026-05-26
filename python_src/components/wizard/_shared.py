from __future__ import annotations

from typing import Any


def wizard_payload(component: str, **kwargs: Any) -> dict[str, Any]:
    payload = {"type": component, "provider": "deepseek"}
    payload.update(kwargs)
    return payload


def normalize_steps(steps: Any) -> list[dict[str, Any]]:
    rows = []
    for index, step in enumerate(steps or []):
        if isinstance(step, dict):
            step_id = step.get("id") or step.get("name") or f"step-{index + 1}"
            title = step.get("title") or step_id
            complete = bool(step.get("complete", False))
        else:
            step_id = str(step)
            title = step_id
            complete = False
        rows.append({"index": index, "id": str(step_id), "title": str(title), "complete": complete})
    return rows

