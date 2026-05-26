"""Local `/chrome` command shim for browser-control settings."""

from __future__ import annotations

from typing import Any

from python_src.utils.config import getGlobalConfig, saveGlobalConfig


CHROME_EXTENSION_URL = "https://api-docs.deepseek.com/"
CHROME_PERMISSIONS_URL = "https://api-docs.deepseek.com/"
CHROME_RECONNECT_URL = "https://api-docs.deepseek.com/"
CONFIG_KEY = "deepseekInChromeDefaultEnabled"


async def getChromeStatus() -> dict[str, Any]:
    config = await getGlobalConfig()
    enabled = bool(config.get(CONFIG_KEY) or config.get("claudeInChromeDefaultEnabled"))
    return {
        "type": "chrome_settings",
        "enabledByDefault": enabled,
        "extensionInstalled": False,
        "connected": False,
        "installUrl": CHROME_EXTENSION_URL,
        "permissionsUrl": CHROME_PERMISSIONS_URL,
        "reconnectUrl": CHROME_RECONNECT_URL,
        "message": "DeepSeek browser control is represented as a local settings shim in this Python migration.",
    }


async def setChromeDefaultEnabled(enabled: bool) -> dict[str, Any]:
    await saveGlobalConfig({CONFIG_KEY: bool(enabled)})
    return await getChromeStatus()


async def call(onDone: Any = None, _context: Any = None, args: str = "") -> dict[str, Any] | None:
    arg = (args or "").strip().lower()
    if arg in {"on", "enable", "enabled", "true"}:
        status = await setChromeDefaultEnabled(True)
        message = "DeepSeek browser control default enabled."
    elif arg in {"off", "disable", "disabled", "false"}:
        status = await setChromeDefaultEnabled(False)
        message = "DeepSeek browser control default disabled."
    elif arg in {"install", "permissions", "reconnect"}:
        status = await getChromeStatus()
        url = status[f"{'install' if arg == 'install' else arg}Url"]
        message = f"Open this URL manually to continue: {url}"
    else:
        status = await getChromeStatus()
        message = status["message"]

    status["action"] = arg or "status"
    if callable(onDone):
        try:
            onDone(message, {"display": "system"})
        except TypeError:
            onDone(message)
        return None
    status["resultMessage"] = message
    return status
