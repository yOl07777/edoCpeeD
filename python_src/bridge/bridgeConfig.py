"""Bridge auth and base URL resolution for the DeepSeek Python runtime."""

from __future__ import annotations

import os


def getBridgeTokenOverride() -> str | None:
    return (
        os.getenv("DEEPSEEK_BRIDGE_OAUTH_TOKEN")
        or os.getenv("DEEPSEEK_API_KEY")
        or os.getenv("DEEPSEEK_API_KEYS", "").split(",", 1)[0].strip()
        or None
    )


def getBridgeBaseUrlOverride() -> str | None:
    return os.getenv("DEEPSEEK_BRIDGE_BASE_URL") or os.getenv("DEEPSEEK_ENDPOINT")


def getBridgeAccessToken() -> str | None:
    return getBridgeTokenOverride()


def getBridgeBaseUrl() -> str:
    endpoints = os.getenv("DEEPSEEK_ENDPOINTS", "")
    first_endpoint = endpoints.split(",", 1)[0].strip() if endpoints else ""
    return (getBridgeBaseUrlOverride() or first_endpoint or "https://api.deepseek.com/v1").rstrip("/")
