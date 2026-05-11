from __future__ import annotations

import fnmatch
import os
from typing import Any

from python_src.utils.permissions.PermissionRule import PermissionRule
from python_src.utils.permissions.permissionRuleParser import permissionRuleValueFromString
from python_src.utils.permissions.permissionsLoader import (
    addPermissionRulesToSettings,
    deletePermissionRuleFromSettings,
    loadAllPermissionRulesFromDisk,
)


def _coerce_rule(rule: PermissionRule | dict[str, Any] | str) -> dict[str, str]:
    if isinstance(rule, PermissionRule):
        return rule.to_dict()
    if isinstance(rule, str):
        return {"tool": rule, "value": "*", "behavior": "allow", "source": "runtime"}
    return {
        "tool": str(rule.get("tool", "*")),
        "value": str(rule.get("value", "*")),
        "behavior": str(rule.get("behavior", "ask")),
        "source": str(rule.get("source", "runtime")),
    }


def _matches(rule: dict[str, str], tool_name: str, value: str = "*") -> bool:
    tool_pattern = rule.get("tool", "*")
    value_pattern = rule.get("value", "*")
    return fnmatch.fnmatchcase(tool_name, tool_pattern) and (
        value_pattern == "*" or fnmatch.fnmatchcase(value, value_pattern)
    )


async def syncPermissionRulesFromDisk(cwd: str | os.PathLike[str] | None = None) -> list[dict[str, str]]:
    return await loadAllPermissionRulesFromDisk(cwd)


async def getAllowRules(rules: list[PermissionRule | dict[str, Any]] | None = None) -> list[dict[str, str]]:
    return [rule for rule in map(_coerce_rule, rules or []) if rule["behavior"] == "allow"]


async def getAskRules(rules: list[PermissionRule | dict[str, Any]] | None = None) -> list[dict[str, str]]:
    return [rule for rule in map(_coerce_rule, rules or []) if rule["behavior"] == "ask"]


async def getDenyRules(rules: list[PermissionRule | dict[str, Any]] | None = None) -> list[dict[str, str]]:
    return [rule for rule in map(_coerce_rule, rules or []) if rule["behavior"] == "deny"]


async def getRuleByContentsForToolName(
    rules: list[PermissionRule | dict[str, Any]],
    tool_name: str,
    value: str = "*",
) -> dict[str, str] | None:
    for rule in map(_coerce_rule, rules):
        if _matches(rule, tool_name, value):
            return rule
    return None


async def getRuleByContentsForTool(
    rules: list[PermissionRule | dict[str, Any]],
    tool: dict[str, Any] | str,
    value: str = "*",
) -> dict[str, str] | None:
    name = tool if isinstance(tool, str) else str(tool.get("name") or tool.get("tool") or "*")
    return await getRuleByContentsForToolName(rules, name, value)


async def getDenyRuleForTool(rules: list[PermissionRule | dict[str, Any]], tool_name: str, value: str = "*") -> dict[str, str] | None:
    return await getRuleByContentsForToolName(await getDenyRules(rules), tool_name, value)


async def getAskRuleForTool(rules: list[PermissionRule | dict[str, Any]], tool_name: str, value: str = "*") -> dict[str, str] | None:
    return await getRuleByContentsForToolName(await getAskRules(rules), tool_name, value)


async def getDenyRuleForAgent(rules: list[PermissionRule | dict[str, Any]], agent_name: str) -> dict[str, str] | None:
    return await getRuleByContentsForToolName(await getDenyRules(rules), "agent", agent_name)


async def filterDeniedAgents(
    agents: list[dict[str, Any]],
    rules: list[PermissionRule | dict[str, Any]],
) -> list[dict[str, Any]]:
    kept = []
    for agent in agents:
        name = str(agent.get("name") or agent.get("id") or "")
        if await getDenyRuleForAgent(rules, name) is None:
            kept.append(agent)
    return kept


async def checkRuleBasedPermissions(
    tool_name: str,
    value: str = "*",
    *,
    rules: list[PermissionRule | dict[str, Any]] | None = None,
    cwd: str | os.PathLike[str] | None = None,
) -> dict[str, Any]:
    all_rules = list(map(_coerce_rule, rules or await loadAllPermissionRulesFromDisk(cwd)))
    for behavior in ("deny", "allow", "ask"):
        match = await getRuleByContentsForToolName(
            [rule for rule in all_rules if rule["behavior"] == behavior],
            tool_name,
            value,
        )
        if match:
            return {"behavior": behavior, "allowed": behavior == "allow", "rule": match}
    return {"behavior": "ask", "allowed": False, "rule": None}


async def applyPermissionRulesToPermissionContext(context: dict[str, Any], rules: list[PermissionRule | dict[str, Any]]) -> dict[str, Any]:
    tool_name = str(context.get("tool_name") or context.get("tool") or "")
    value = str(context.get("value") or context.get("input") or "*")
    result = await checkRuleBasedPermissions(tool_name, value, rules=rules)
    return {**context, "permission": result}


async def createPermissionRequestMessage(tool_name: str, value: str = "*") -> str:
    return f"工具 `{tool_name}` 请求访问 `{value}`，需要权限确认。"


async def permissionRuleSourceDisplayString(source: str) -> str:
    return {"project": "项目配置", "user": "用户配置", "managed": "托管策略", "runtime": "运行时规则"}.get(source, source)


async def toolAlwaysAllowedRule(tool_name: str, value: str = "*", source: str = "project") -> PermissionRule:
    return PermissionRule(tool=tool_name, value=value, behavior="allow", source=source)


async def deletePermissionRule(rule: PermissionRule | dict[str, Any], *, cwd: str | os.PathLike[str] | None = None) -> bool:
    return await deletePermissionRuleFromSettings(rule, cwd=cwd)


async def addRuleFromString(value: str, *, cwd: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    rule = await permissionRuleValueFromString(value)
    rules = await addPermissionRulesToSettings([rule], cwd=cwd)
    return {"rule": rule.to_dict(), "rules": rules}


hasPermissionsToUseTool = checkRuleBasedPermissions
