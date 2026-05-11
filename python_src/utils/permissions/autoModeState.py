from __future__ import annotations


_ACTIVE = False
_CIRCUIT_BROKEN = False
_CLI_FLAG = False


async def isAutoModeActive() -> bool:
    return _ACTIVE and not _CIRCUIT_BROKEN


async def setAutoModeActive(active: bool) -> bool:
    global _ACTIVE
    _ACTIVE = bool(active)
    return _ACTIVE


async def isAutoModeCircuitBroken() -> bool:
    return _CIRCUIT_BROKEN


async def setAutoModeCircuitBroken(value: bool) -> bool:
    global _CIRCUIT_BROKEN
    _CIRCUIT_BROKEN = bool(value)
    return _CIRCUIT_BROKEN


async def getAutoModeFlagCli() -> bool:
    return _CLI_FLAG


async def setAutoModeFlagCli(value: bool) -> bool:
    global _CLI_FLAG
    _CLI_FLAG = bool(value)
    return _CLI_FLAG


async def _resetForTesting() -> None:
    global _ACTIVE, _CIRCUIT_BROKEN, _CLI_FLAG
    _ACTIVE = False
    _CIRCUIT_BROKEN = False
    _CLI_FLAG = False
