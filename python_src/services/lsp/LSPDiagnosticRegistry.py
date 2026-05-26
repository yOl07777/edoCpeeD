"""In-memory registry for LSP diagnostics."""

from __future__ import annotations

from pathlib import Path
from typing import Any

_PENDING: dict[str, list[dict[str, Any]]] = {}
_DELIVERED: set[str] = set()


def _key(path: str | Path) -> str:
    return str(Path(path).resolve())


async def registerPendingLSPDiagnostic(path: str | Path, diagnostic: dict[str, Any] | str) -> dict[str, Any]:
    entry = diagnostic if isinstance(diagnostic, dict) else {"message": str(diagnostic)}
    entry = {"path": _key(path), "severity": entry.get("severity", "warning"), **entry}
    _PENDING.setdefault(_key(path), []).append(entry)
    return entry


async def checkForLSPDiagnostics(path: str | Path | None = None, mark_delivered: bool = True) -> list[dict[str, Any]]:
    if path is None:
        diagnostics = [diag for values in _PENDING.values() for diag in values]
    else:
        diagnostics = list(_PENDING.get(_key(path), []))
    if mark_delivered:
        for diag in diagnostics:
            _DELIVERED.add(f"{diag.get('path')}:{diag.get('line', '')}:{diag.get('message', '')}")
    return diagnostics


async def getPendingLSPDiagnosticCount(path: str | Path | None = None) -> int:
    if path is None:
        return sum(len(values) for values in _PENDING.values())
    return len(_PENDING.get(_key(path), []))


async def clearDeliveredDiagnosticsForFile(path: str | Path) -> int:
    prefix = _key(path) + ":"
    before = len(_DELIVERED)
    for item in list(_DELIVERED):
        if item.startswith(prefix):
            _DELIVERED.remove(item)
    return before - len(_DELIVERED)


async def clearAllLSPDiagnostics() -> None:
    _PENDING.clear()


async def resetAllLSPDiagnosticState() -> None:
    _PENDING.clear()
    _DELIVERED.clear()
