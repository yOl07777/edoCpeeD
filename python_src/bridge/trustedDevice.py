"""Trusted device token storage/enrollment for bridge requests."""

from __future__ import annotations

import json
import os
import platform
import socket
from pathlib import Path
from typing import Any

import httpx

from .bridgeConfig import getBridgeAccessToken, getBridgeBaseUrl

TRUSTED_DEVICE_GATE_ENV = "DEEPSEEK_TRUSTED_DEVICE_ENFORCEMENT"
_cached_token: str | None = None


def _enabled() -> bool:
    return os.getenv(TRUSTED_DEVICE_GATE_ENV, "").lower() in {"1", "true", "yes", "on"}


def _storage_path() -> Path:
    root = os.getenv("DEEPCODE_CONFIG_HOME") or os.getenv("DEEPSEEK_CODE_HOME")
    base = Path(root).expanduser() if root else Path.home() / ".deepcode"
    return base / "trusted_device.json"


def _read_storage() -> dict[str, Any]:
    try:
        return json.loads(_storage_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _write_storage(data: dict[str, Any]) -> None:
    path = _storage_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def getTrustedDeviceToken() -> str | None:
    global _cached_token
    if not _enabled():
        return None
    env_token = os.getenv("DEEPSEEK_TRUSTED_DEVICE_TOKEN") or os.getenv("CLAUDE_TRUSTED_DEVICE_TOKEN")
    if env_token:
        return env_token
    if _cached_token is None:
        token = _read_storage().get("trustedDeviceToken")
        _cached_token = token if isinstance(token, str) else None
    return _cached_token


def clearTrustedDeviceTokenCache() -> None:
    global _cached_token
    _cached_token = None


def clearTrustedDeviceToken() -> None:
    global _cached_token
    data = _read_storage()
    data.pop("trustedDeviceToken", None)
    try:
        _write_storage(data)
    except OSError:
        pass
    _cached_token = None


async def enrollTrustedDevice(
    *,
    baseUrl: str | None = None,
    accessToken: str | None = None,
    client: httpx.AsyncClient | None = None,
) -> str | None:
    global _cached_token
    if not _enabled() or os.getenv("DEEPSEEK_TRUSTED_DEVICE_TOKEN") or os.getenv("CLAUDE_TRUSTED_DEVICE_TOKEN"):
        return None
    token = accessToken or getBridgeAccessToken()
    if not token:
        return None
    owns_client = client is None
    http = client or httpx.AsyncClient(timeout=10.0)
    try:
        response = await http.post(
            f"{(baseUrl or getBridgeBaseUrl()).rstrip('/')}/api/auth/trusted_devices",
            json={"display_name": f"DeepCode on {socket.gethostname()} / {platform.system()}"},
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )
        if response.status_code not in {200, 201}:
            return None
        data = response.json()
        device_token = data.get("device_token") if isinstance(data, dict) else None
        if not isinstance(device_token, str) or not device_token:
            return None
        storage = _read_storage()
        storage["trustedDeviceToken"] = device_token
        _write_storage(storage)
        _cached_token = device_token
        return device_token
    except (httpx.HTTPError, OSError, ValueError):
        return None
    finally:
        if owns_client:
            await http.aclose()
