from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def WorkflowMultiselectDialog(*args: Any, **kwargs: Any) -> dict[str, Any]:
    workflows = normalize_items(option(args, kwargs, "workflows", scalar_arg(args, [])), text_key="name")
    selected = {str(item) for item in option(args, kwargs, "selected", []) or []}
    for workflow in workflows:
        value = str(workflow.get("id") or workflow.get("name") or "")
        workflow["selected"] = value in selected
    return component_payload("workflow_multiselect_dialog", workflows=workflows, selected=sorted(selected), count=len(workflows))


__all__ = ["WorkflowMultiselectDialog"]
