from __future__ import annotations

import json
from typing import Any


KNOWN_TOP_LEVEL_KEYS = {
    "model",
    "defaultModel",
    "provider",
    "permissions",
    "env",
    "mcpServers",
    "apiKeys",
    "endpoints",
    "tools",
    "plugins",
    "autoMode",
}


async def formatZodError(error: Exception | str) -> str:
    return str(error)


async def filterInvalidPermissionRules(rules: list[Any]) -> list[dict[str, Any]]:
    valid = []
    for rule in rules:
        if isinstance(rule, dict) and isinstance(rule.get("tool"), str):
            valid.append(rule)
    return valid


async def validateSettingsFileContent(content: str | dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if isinstance(content, str):
        try:
            data = json.loads(content) if content.strip() else {}
        except json.JSONDecodeError as exc:
            return {"ok": False, "settings": {}, "errors": [await formatZodError(exc)]}
    elif isinstance(content, dict):
        data = dict(content)
    else:
        return {"ok": False, "settings": {}, "errors": ["Settings content must be JSON object."]}

    if not isinstance(data, dict):
        return {"ok": False, "settings": {}, "errors": ["Settings root must be an object."]}
    for key in data:
        if key not in KNOWN_TOP_LEVEL_KEYS:
            errors.append(f"Unknown settings key: {key}")
    if "permissions" in data and not isinstance(data["permissions"], dict):
        errors.append("permissions must be an object.")
    if "env" in data and not isinstance(data["env"], dict):
        errors.append("env must be an object.")
    return {"ok": not errors, "settings": data, "errors": errors}
