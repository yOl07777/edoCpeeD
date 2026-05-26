from __future__ import annotations

from typing import Any

from python_src.services.tips.tipHistory import getSessionsSinceLastShown, recordTipShown
from python_src.services.tips.tipRegistry import getRelevantTips


async def selectTipWithLongestTimeSinceShown(tips: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not tips:
        return None
    scored = []
    for tip in tips:
        gap = await getSessionsSinceLastShown(str(tip["id"]))
        scored.append((float("inf") if gap is None else gap, tip))
    scored.sort(key=lambda item: item[0], reverse=True)
    return scored[0][1]


async def recordShownTip(tip: dict[str, Any] | str) -> dict[str, Any]:
    tip_id = tip if isinstance(tip, str) else str(tip.get("id"))
    return await recordTipShown(tip_id)


async def getTipToShowOnSpinner(context: dict[str, Any] | None = None) -> dict[str, Any] | None:
    tip = await selectTipWithLongestTimeSinceShown(await getRelevantTips(context))
    if tip:
        await recordShownTip(tip)
    return tip
