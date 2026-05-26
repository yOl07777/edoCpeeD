"""Terminal-friendly companion rendering shims."""

from __future__ import annotations

from typing import Any

from .companion import getCompanion
from .sprites import renderFace, renderSprite, spriteFrameCount

MIN_COLS_FOR_FULL_SPRITE = 100
SPRITE_BODY_WIDTH = 12
SPRITE_PADDING_X = 2
BUBBLE_WIDTH = 36


def _display_width(text: str) -> int:
    return len(text)


def companionReservedColumns(terminalColumns: int, speaking: bool = False, config: dict[str, Any] | None = None) -> int:
    companion = getCompanion(config)
    if companion is None or (config and config.get("companionMuted")):
        return 0
    if terminalColumns < MIN_COLS_FOR_FULL_SPRITE:
        return 0
    name_width = _display_width(companion.name) + 2
    bubble = BUBBLE_WIDTH if speaking else 0
    return max(SPRITE_BODY_WIDTH, name_width) + SPRITE_PADDING_X + bubble


def CompanionSprite(
    *,
    terminalColumns: int = 120,
    reaction: str | None = None,
    focused: bool = False,
    tick: int = 0,
    config: dict[str, Any] | None = None,
) -> str | None:
    companion = getCompanion(config)
    if companion is None or (config and config.get("companionMuted")):
        return None
    if terminalColumns < MIN_COLS_FOR_FULL_SPRITE:
        label = f'"{reaction[:23]}"' if reaction else (f" {companion.name} " if focused else companion.name)
        return f"{renderFace(companion)} {label}"
    frame_count = spriteFrameCount(companion.species)
    body = renderSprite(companion, tick % frame_count)
    if reaction:
        body = [f"[ {reaction} ]", *body]
    body.append(f" {companion.name} " if focused else companion.name)
    return "\n".join(body)


def CompanionFloatingBubble(reaction: str | None = None, *, config: dict[str, Any] | None = None, tick: int = 0) -> str | None:
    companion = getCompanion(config)
    if not reaction or companion is None or (config and config.get("companionMuted")):
        return None
    fading = tick >= 14
    marker = "~" if fading else "*"
    return f"{marker} {companion.name}: {reaction} {marker}"
