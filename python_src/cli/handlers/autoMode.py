"""Auto-mode rule handlers."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

DEFAULT_AUTO_MODE_RULES = [
    "Prefer read-only inspection before modifying files.",
    "Avoid destructive filesystem or git operations unless explicitly requested.",
    "Run focused verification after code changes when practical.",
]


def _config_path() -> Path:
    root = os.getenv("DEEPCODE_CONFIG_HOME") or os.getenv("DEEPSEEK_CODE_HOME")
    base = Path(root).expanduser() if root else Path.home() / ".deepcode"
    return base / "auto_mode.json"


def _read_rules() -> list[str]:
    try:
        data = json.loads(_config_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    rules = data.get("rules") if isinstance(data, dict) else None
    return [str(rule) for rule in rules] if isinstance(rules, list) else []


def _write_rules(rules: list[str]) -> None:
    path = _config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"rules": rules}, ensure_ascii=False, indent=2), encoding="utf-8")


def autoModeDefaultsHandler() -> dict[str, Any]:
    return {"rules": list(DEFAULT_AUTO_MODE_RULES)}


def autoModeConfigHandler(rules: list[str] | None = None) -> dict[str, Any]:
    if rules is not None:
        _write_rules([str(rule) for rule in rules])
    custom = _read_rules()
    return {"rules": custom, "defaults": list(DEFAULT_AUTO_MODE_RULES), "path": str(_config_path())}


async def autoModeCritiqueHandler(options: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
    options = {**(options or {}), **kwargs}
    custom = _read_rules()
    defaults = list(DEFAULT_AUTO_MODE_RULES)
    issues: list[str] = []
    all_rules = custom or defaults
    if not all_rules:
        issues.append("No auto-mode rules are configured.")
    if any("always" in rule.lower() and "delete" in rule.lower() for rule in all_rules):
        issues.append("A rule appears to allow broad deletion; narrow it or require confirmation.")
    if not any("verify" in rule.lower() or "test" in rule.lower() for rule in all_rules):
        issues.append("Consider adding a verification rule for code changes.")
    return {
        "model": options.get("model", "deepseek-chat"),
        "rules": all_rules,
        "issues": issues,
        "summary": "OK" if not issues else "Needs review",
    }
