from __future__ import annotations

from typing import Any


async def parsePluginArgs(args: str | None = None, *unused: Any, **kwargs: Any) -> dict[str, Any]:
    raw = (args if args is not None else kwargs.get("args", "") or "").strip()
    if not raw:
        return {"type": "menu"}
    parts = raw.split()
    command = parts[0].lower()
    if command in {"help", "--help", "-h"}:
        return {"type": "help"}
    if command in {"install", "i"}:
        target = parts[1] if len(parts) > 1 else None
        if not target:
            return {"type": "install"}
        if "@" in target:
            plugin, marketplace = target.split("@", 1)
            return {"type": "install", "plugin": plugin or None, "marketplace": marketplace or None}
        is_marketplace = target.startswith(("http://", "https://", "file://")) or "/" in target or "\\" in target
        return {"type": "install", "marketplace": target} if is_marketplace else {"type": "install", "plugin": target}
    if command == "manage":
        return {"type": "manage"}
    if command == "uninstall":
        return {"type": "uninstall", "plugin": parts[1] if len(parts) > 1 else None}
    if command == "enable":
        return {"type": "enable", "plugin": parts[1] if len(parts) > 1 else None}
    if command == "disable":
        return {"type": "disable", "plugin": parts[1] if len(parts) > 1 else None}
    if command == "validate":
        target = " ".join(parts[1:]).strip()
        return {"type": "validate", "path": target or None}
    if command in {"marketplace", "market"}:
        action = parts[1].lower() if len(parts) > 1 else None
        target = " ".join(parts[2:]).strip()
        if action in {"add", "remove", "rm", "update", "list"}:
            return {
                "type": "marketplace",
                "action": "remove" if action == "rm" else action,
                "target": target or None,
            }
        return {"type": "marketplace"}
    return {"type": "menu"}


__all__ = ["parsePluginArgs"]
