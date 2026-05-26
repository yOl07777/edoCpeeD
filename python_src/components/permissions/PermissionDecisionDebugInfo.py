from __future__ import annotations

from typing import Any


async def PermissionDecisionDebugInfo(*args: Any, **kwargs: Any) -> dict[str, Any]:
    decision = kwargs.get("decision") or (args[0] if args else {}) or {}
    context = kwargs.get("context") or (args[1] if len(args) > 1 else {}) or {}
    return {
        "type": "permission_decision_debug_info",
        "provider": "deepseek",
        "decision": decision,
        "context": context,
        "summary": f"behavior={decision.get('behavior', 'unknown')}" if isinstance(decision, dict) else str(decision),
    }


__all__ = ["PermissionDecisionDebugInfo"]
