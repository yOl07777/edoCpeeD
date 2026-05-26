"""Authentication handlers for the DeepSeek Python CLI."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def _config_home() -> Path:
    root = os.getenv("DEEPCODE_CONFIG_HOME") or os.getenv("DEEPSEEK_CODE_HOME")
    return Path(root).expanduser() if root else Path.home() / ".deepcode"


def _auth_path() -> Path:
    return _config_home() / "auth.json"


def _read_auth() -> dict[str, Any]:
    try:
        return json.loads(_auth_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _write_auth(data: dict[str, Any]) -> None:
    path = _auth_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


async def installOAuthTokens(tokens: dict[str, Any]) -> dict[str, Any]:
    data = _read_auth()
    data["oauth"] = dict(tokens)
    if tokens.get("accessToken"):
        data["api_key"] = tokens["accessToken"]
    _write_auth(data)
    return {"installed": True, "path": str(_auth_path()), "hasAccessToken": bool(tokens.get("accessToken"))}


async def authLogin(opts: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
    opts = {**(opts or {}), **kwargs}
    api_key = opts.get("api_key") or opts.get("apiKey") or os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        keys = [part.strip() for part in os.getenv("DEEPSEEK_API_KEYS", "").split(",") if part.strip()]
        api_key = keys[0] if keys else None
    if not api_key:
        return {"loggedIn": False, "reason": "missing DEEPSEEK_API_KEY or DEEPSEEK_API_KEYS"}
    data = _read_auth()
    data["provider"] = "deepseek"
    data["api_key"] = api_key
    if opts.get("model"):
        data["model"] = opts["model"]
    _write_auth(data)
    return {"loggedIn": True, "provider": "deepseek", "path": str(_auth_path())}


async def authStatus(opts: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
    opts = {**(opts or {}), **kwargs}
    data = _read_auth()
    env_keys = [part.strip() for part in os.getenv("DEEPSEEK_API_KEYS", "").split(",") if part.strip()]
    has_env_key = bool(os.getenv("DEEPSEEK_API_KEY") or env_keys)
    has_stored_key = bool(data.get("api_key") or data.get("oauth", {}).get("accessToken"))
    status = {
        "loggedIn": has_env_key or has_stored_key,
        "provider": data.get("provider") or "deepseek",
        "authTokenSource": "env" if has_env_key else "local" if has_stored_key else None,
        "hasApiKey": has_env_key or bool(data.get("api_key")),
        "storedPath": str(_auth_path()),
    }
    if opts.get("json"):
        return status
    return status


async def authLogout() -> dict[str, Any]:
    path = _auth_path()
    existed = path.exists()
    try:
        path.unlink()
    except FileNotFoundError:
        pass
    return {"loggedOut": True, "removed": existed, "path": str(path)}
