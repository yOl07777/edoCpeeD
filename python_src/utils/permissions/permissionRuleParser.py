from __future__ import annotations

from urllib.parse import quote, unquote

from python_src.utils.permissions.PermissionRule import PermissionRule


LEGACY_TOOL_NAMES = {
    "Bash": "run_shell",
    "PowerShell": "run_powershell",
    "Read": "read_file",
    "Write": "write_file",
    "Edit": "edit_file",
    "Glob": "glob_files",
    "Grep": "grep_files",
    "WebFetch": "web_fetch",
    "WebSearch": "web_search",
}


async def escapeRuleContent(content: str) -> str:
    return quote(content, safe="*._-/:\\ ")


async def unescapeRuleContent(content: str) -> str:
    return unquote(content)


async def getLegacyToolNames() -> dict[str, str]:
    return dict(LEGACY_TOOL_NAMES)


async def normalizeLegacyToolName(name: str) -> str:
    return LEGACY_TOOL_NAMES.get(name, name)


async def permissionRuleValueFromString(value: str, *, source: str = "project") -> PermissionRule:
    raw = value.strip()
    behavior = "ask"
    for prefix in ("allow:", "ask:", "deny:"):
        if raw.lower().startswith(prefix):
            behavior = prefix[:-1]
            raw = raw[len(prefix) :]
            break
    if ":" in raw:
        tool, content = raw.split(":", 1)
    elif "(" in raw and raw.endswith(")"):
        tool, content = raw[:-1].split("(", 1)
    else:
        tool, content = raw, "*"
    return PermissionRule(
        tool=await normalizeLegacyToolName(tool.strip()),
        value=await unescapeRuleContent(content.strip() or "*"),
        behavior=behavior,  # type: ignore[arg-type]
        source=source,
    )


async def permissionRuleValueToString(rule: PermissionRule | dict[str, str]) -> str:
    if isinstance(rule, PermissionRule):
        payload = rule.to_dict()
    else:
        payload = dict(rule)
    behavior = payload.get("behavior", "ask")
    tool = payload.get("tool", "")
    value = await escapeRuleContent(payload.get("value", "*"))
    return f"{behavior}:{tool}:{value}"
