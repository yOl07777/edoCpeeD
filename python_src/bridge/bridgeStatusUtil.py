"""Bridge status text, URL, and shimmer helpers."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from urllib.parse import urlencode

FAILED_FOOTER_TEXT = "Something went wrong, please try again"
SHIMMER_INTERVAL_MS = 150
TOOL_DISPLAY_EXPIRY_MS = 30_000


def timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


def _width(text: str) -> int:
    return sum(2 if ord(ch) > 0x2E80 else 1 for ch in text)


def truncatePrompt(text: str, max_width: int) -> str:
    if _width(text) <= max_width:
        return text
    result = ""
    used = 0
    for ch in text:
        ch_width = 2 if ord(ch) > 0x2E80 else 1
        if used + ch_width > max_width - 1:
            break
        result += ch
        used += ch_width
    return result + "…"


def formatDuration(ms: int | float) -> str:
    seconds = max(0, round(ms / 1000))
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def abbreviateActivity(summary: str) -> str:
    return truncatePrompt(summary, 30)


def buildBridgeConnectUrl(environmentId: str, ingressUrl: str | None = None) -> str:
    base = (ingressUrl or "https://chat.deepseek.com").rstrip("/")
    return f"{base}/code?{urlencode({'bridge': environmentId})}"


def buildBridgeSessionUrl(
    sessionId: str,
    environmentId: str,
    ingressUrl: str | None = None,
) -> str:
    base = (ingressUrl or "https://chat.deepseek.com").rstrip("/")
    return f"{base}/session/{sessionId}?{urlencode({'bridge': environmentId})}"


def computeGlimmerIndex(tick: int, messageWidth: int) -> int:
    cycle_length = messageWidth + 20
    return messageWidth + 10 - (tick % cycle_length)


def computeShimmerSegments(text: str, glimmerIndex: int) -> dict[str, str]:
    message_width = _width(text)
    shimmer_start = glimmerIndex - 1
    shimmer_end = glimmerIndex + 1
    if shimmer_start >= message_width or shimmer_end < 0:
        return {"before": text, "shimmer": "", "after": ""}

    clamped_start = max(0, shimmer_start)
    col_pos = 0
    before = ""
    shimmer = ""
    after = ""
    for ch in text:
        ch_width = 2 if ord(ch) > 0x2E80 else 1
        if col_pos + ch_width <= clamped_start:
            before += ch
        elif col_pos > shimmer_end:
            after += ch
        else:
            shimmer += ch
        col_pos += ch_width
    return {"before": before, "shimmer": shimmer, "after": after}


def getBridgeStatus(state: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, str]:
    data = dict(state or {})
    data.update(kwargs)
    if data.get("error"):
        return {"label": "Remote Control failed", "color": "error"}
    if data.get("reconnecting"):
        return {"label": "Remote Control reconnecting", "color": "warning"}
    if data.get("sessionActive") or data.get("connected"):
        return {"label": "Remote Control active", "color": "success"}
    return {"label": "Remote Control connecting…", "color": "warning"}


def buildIdleFooterText(url: str) -> str:
    return f"Code everywhere with the DeepSeek app or {url}"


def buildActiveFooterText(url: str) -> str:
    return f"Continue coding in the DeepSeek app or {url}"


def wrapWithOsc8Link(text: str, url: str) -> str:
    return f"\033]8;;{url}\a{text}\033]8;;\a"
