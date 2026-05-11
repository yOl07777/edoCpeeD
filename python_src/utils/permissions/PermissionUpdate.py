from __future__ import annotations

import os
from typing import Any

from python_src.utils.permissions.PermissionRule import PermissionRule
from python_src.utils.permissions.permissionsLoader import addPermissionRulesToSettings, deletePermissionRuleFromSettings


def _rules_from_update(update: dict[str, Any]) -> list[dict[str, Any]]:
    if "rules" in update and isinstance(update["rules"], list):
        return list(update["rules"])
    if "rule" in update:
        return [update["rule"]]
    if "tool" in update:
        return [update]
    return []


async def hasRules(update: dict[str, Any]) -> bool:
    return bool(_rules_from_update(update))


async def extractRules(update: dict[str, Any]) -> list[dict[str, Any]]:
    return _rules_from_update(update)


async def supportsPersistence(update: dict[str, Any]) -> bool:
    return bool(update.get("persist", True))


async def createReadRuleSuggestion(path: str, *, source: str = "project") -> PermissionRule:
    return PermissionRule(tool="read_file", value=path, behavior="allow", source=source)


async def applyPermissionUpdate(
    update: dict[str, Any],
    rules: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    current = list(rules or [])
    action = str(update.get("action", "add"))
    for rule in _rules_from_update(update):
        if action == "delete":
            current = [
                item
                for item in current
                if not (
                    item.get("tool") == rule.get("tool")
                    and item.get("value", "*") == rule.get("value", "*")
                    and item.get("behavior", "ask") == rule.get("behavior", "ask")
                )
            ]
        else:
            normalized = {
                "tool": str(rule.get("tool", "*")),
                "value": str(rule.get("value", "*")),
                "behavior": str(rule.get("behavior", "ask")),
                "source": str(rule.get("source", "project")),
            }
            if normalized not in current:
                current.append(normalized)
    return current


async def applyPermissionUpdates(
    updates: list[dict[str, Any]],
    rules: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    current = list(rules or [])
    for update in updates:
        current = await applyPermissionUpdate(update, current)
    return current


async def persistPermissionUpdate(update: dict[str, Any], *, cwd: str | os.PathLike[str] | None = None) -> list[dict[str, str]]:
    rules = _rules_from_update(update)
    if update.get("action") == "delete":
        for rule in rules:
            await deletePermissionRuleFromSettings(rule, cwd=cwd)
        from python_src.utils.permissions.permissionsLoader import loadAllPermissionRulesFromDisk

        return await loadAllPermissionRulesFromDisk(cwd)
    return await addPermissionRulesToSettings(rules, cwd=cwd)


async def persistPermissionUpdates(updates: list[dict[str, Any]], *, cwd: str | os.PathLike[str] | None = None) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for update in updates:
        result = await persistPermissionUpdate(update, cwd=cwd)
    return result
