from __future__ import annotations

from typing import Any

from ._basic import first_mapping, pick


async def usePrStatus(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    number = pick(options, "number", "prNumber", default=None)
    checks = options.get("checks", []) if isinstance(options.get("checks", []), list) else []
    failing = [check for check in checks if isinstance(check, dict) and check.get("status") not in {"success", "passed"}]
    return {
        "provider": "deepseek",
        "number": number,
        "state": pick(options, "state", default="unknown"),
        "checks": checks,
        "failingChecks": failing,
        "summary": f"PR #{number}" if number else "No pull request detected",
    }
