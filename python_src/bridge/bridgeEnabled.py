"""Feature gates for Python bridge/remote-control support."""

from __future__ import annotations

import os
import re


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def _flag(name: str, default: bool = False) -> bool:
    return _truthy(os.getenv(name)) if os.getenv(name) is not None else default


def _version_tuple(version: str) -> tuple[int, ...]:
    parts = re.findall(r"\d+", version)
    return tuple(int(p) for p in parts[:3]) or (0,)


def isBridgeEnabled() -> bool:
    """Return whether bridge mode is enabled for this Python runtime.

    Anthropic OAuth entitlement checks do not apply to the DeepSeek migration,
    so the gate is intentionally controlled by local environment/config only.
    """

    return _flag("DEEPSEEK_BRIDGE_MODE") or _flag("BRIDGE_MODE")


async def isBridgeEnabledBlocking() -> bool:
    return isBridgeEnabled()


async def getBridgeDisabledReason() -> str | None:
    if isBridgeEnabled():
        return None
    return "Remote Control bridge is disabled. Set DEEPSEEK_BRIDGE_MODE=1 to enable it."


def isEnvLessBridgeEnabled() -> bool:
    return _flag("DEEPSEEK_BRIDGE_ENVLESS", True)


def isCseShimEnabled() -> bool:
    return _flag("DEEPSEEK_CSE_SHIM", True)


def checkBridgeMinVersion(
    current_version: str | None = None,
    min_version: str | None = None,
) -> str | None:
    current = current_version or os.getenv("DEEPCODE_VERSION", "0.0.0")
    required = min_version or os.getenv("DEEPSEEK_BRIDGE_MIN_VERSION", "0.0.0")
    if _version_tuple(current) < _version_tuple(required):
        return (
            f"Your version of DeepCode ({current}) is too old for Remote Control.\n"
            f"Version {required} or higher is required."
        )
    return None


def getCcrAutoConnectDefault() -> bool:
    return _flag("DEEPSEEK_CCR_AUTO_CONNECT")


def isCcrMirrorEnabled() -> bool:
    return _flag("DEEPSEEK_CCR_MIRROR") or _flag("CLAUDE_CODE_CCR_MIRROR")
