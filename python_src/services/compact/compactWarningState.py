from __future__ import annotations


compactWarningStore: dict[str, bool] = {"suppressed": False}


async def suppressCompactWarning() -> dict[str, bool]:
    compactWarningStore["suppressed"] = True
    return dict(compactWarningStore)


async def clearCompactWarningSuppression() -> dict[str, bool]:
    compactWarningStore["suppressed"] = False
    return dict(compactWarningStore)
