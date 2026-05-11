from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from python_src.utils.permissions.PermissionRule import PermissionRule


PERMISSIONS_FILE = ".deepseek_permissions.json"


def _settings_path(cwd: str | os.PathLike[str] | None = None) -> Path:
    return Path(cwd or os.getcwd()).resolve() / PERMISSIONS_FILE


def _coerce_rule(rule: PermissionRule | dict[str, Any]) -> dict[str, str]:
    if isinstance(rule, PermissionRule):
        return rule.to_dict()
    return {
        "tool": str(rule.get("tool", "*")),
        "value": str(rule.get("value", "*")),
        "behavior": str(rule.get("behavior", "ask")),
        "source": str(rule.get("source", "project")),
    }


async def loadAllPermissionRulesFromDisk(cwd: str | os.PathLike[str] | None = None) -> list[dict[str, str]]:
    path = _settings_path(cwd)
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    rules = data.get("rules", data if isinstance(data, list) else [])
    return [_coerce_rule(rule) for rule in rules]


async def addPermissionRulesToSettings(
    rules: list[PermissionRule | dict[str, Any]],
    *,
    cwd: str | os.PathLike[str] | None = None,
) -> list[dict[str, str]]:
    path = _settings_path(cwd)
    existing = await loadAllPermissionRulesFromDisk(cwd)
    seen = {(rule["tool"], rule["value"], rule["behavior"]) for rule in existing}
    for rule in rules:
        coerced = _coerce_rule(rule)
        key = (coerced["tool"], coerced["value"], coerced["behavior"])
        if key not in seen:
            existing.append(coerced)
            seen.add(key)
    path.write_text(json.dumps({"rules": existing}, ensure_ascii=False, indent=2), encoding="utf-8")
    return existing


async def deletePermissionRuleFromSettings(
    rule: PermissionRule | dict[str, Any],
    *,
    cwd: str | os.PathLike[str] | None = None,
) -> bool:
    target = _coerce_rule(rule)
    existing = await loadAllPermissionRulesFromDisk(cwd)
    kept = [
        item
        for item in existing
        if not (
            item["tool"] == target["tool"]
            and item["value"] == target["value"]
            and item["behavior"] == target["behavior"]
        )
    ]
    _settings_path(cwd).write_text(json.dumps({"rules": kept}, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(kept) != len(existing)


async def getPermissionRulesForSource(
    source: str,
    *,
    cwd: str | os.PathLike[str] | None = None,
) -> list[dict[str, str]]:
    return [rule for rule in await loadAllPermissionRulesFromDisk(cwd) if rule.get("source") == source]


async def shouldAllowManagedPermissionRulesOnly() -> bool:
    return os.getenv("DEEPSEEK_MANAGED_PERMISSIONS_ONLY", "").lower() in {"1", "true", "yes"}


async def shouldShowAlwaysAllowOptions() -> bool:
    return not await shouldAllowManagedPermissionRulesOnly()
