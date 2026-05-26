"""VS Code SDK MCP notification shim."""

from __future__ import annotations

from typing import Any

LogEventNotificationSchema: dict[str, Any] = {
    "method": "log_event",
    "params": {"eventName": "string", "eventData": "object"},
}

_vscode_mcp_client: Any = None
_notifications: list[dict[str, Any]] = []


async def _maybe_await(value: Any) -> Any:
    if hasattr(value, "__await__"):
        return await value
    return value


async def notifyVscodeFileUpdated(*args: Any, **kwargs: Any) -> dict[str, Any]:
    filePath = str(kwargs.get("filePath") or (args[0] if args else ""))
    oldContent = kwargs.get("oldContent") if "oldContent" in kwargs else (args[1] if len(args) > 1 else None)
    newContent = kwargs.get("newContent") if "newContent" in kwargs else (args[2] if len(args) > 2 else None)
    payload = {"method": "file_updated", "params": {"filePath": filePath, "oldContent": oldContent, "newContent": newContent}}
    _notifications.append(payload)
    client = getattr(_vscode_mcp_client, "client", None) if _vscode_mcp_client is not None else None
    notify = getattr(client, "notification", None)
    if callable(notify):
        await _maybe_await(notify(payload))
        return {"sent": True, "notification": payload}
    return {"sent": False, "notification": payload, "reason": "VS Code MCP client is not connected"}


async def setupVscodeSdkMcp(*args: Any, **kwargs: Any) -> dict[str, Any]:
    global _vscode_mcp_client
    sdkClients = kwargs.get("sdkClients") or (args[0] if args else [])
    for client in sdkClients or []:
        name = client.get("name") if isinstance(client, dict) else getattr(client, "name", None)
        kind = client.get("type") if isinstance(client, dict) else getattr(client, "type", None)
        if name == "claude-vscode" and kind == "connected":
            _vscode_mcp_client = client
            return {"connected": True, "name": name, "experimentGates": {}}
    _vscode_mcp_client = None
    return {"connected": False, "name": "claude-vscode", "experimentGates": {}}


def getVscodeNotificationsForTesting() -> list[dict[str, Any]]:
    return list(_notifications)


__all__ = [
    "LogEventNotificationSchema",
    "getVscodeNotificationsForTesting",
    "notifyVscodeFileUpdated",
    "setupVscodeSdkMcp",
]
