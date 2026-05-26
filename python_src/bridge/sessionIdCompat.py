"""Session ID retagging helpers for CCR compatibility."""

from __future__ import annotations

from collections.abc import Callable

_is_cse_shim_enabled: Callable[[], bool] | None = None


def setCseShimGate(gate: Callable[[], bool]) -> None:
    global _is_cse_shim_enabled
    _is_cse_shim_enabled = gate


def toCompatSessionId(id: str) -> str:
    if not id.startswith("cse_"):
        return id
    if _is_cse_shim_enabled is not None and not _is_cse_shim_enabled():
        return id
    return "session_" + id[len("cse_") :]


def toInfraSessionId(id: str) -> str:
    if not id.startswith("session_"):
        return id
    return "cse_" + id[len("session_") :]
