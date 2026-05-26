"""Resume dry-run AgentTool background runs."""

from __future__ import annotations

from typing import Any

from ._registry import AGENT_RUNS


async def resumeAgentBackground(*args: Any, **kwargs: Any) -> dict[str, Any]:
    run_id = str(kwargs.get("runId") or kwargs.get("agentRunId") or (args[0] if args else ""))
    run = AGENT_RUNS.get(run_id)
    if run is None:
        return {"runId": run_id, "status": "missing", "resumed": False}
    run["status"] = kwargs.get("status", "running")
    run["resumed"] = True
    return run


__all__ = ["resumeAgentBackground"]
