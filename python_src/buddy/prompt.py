"""Prompt attachment helpers for companion mode."""

from __future__ import annotations

from typing import Any

from .companion import getCompanion


def companionIntroText(name: str, species: str) -> str:
    return (
        "# Companion\n\n"
        f"A small {species} named {name} sits beside the user's input box and occasionally comments in a speech bubble. "
        f"You're not {name}; it's a separate watcher.\n\n"
        f"When the user addresses {name} directly by name, stay out of the way: respond in one line or less, "
        "or answer only the part meant for you."
    )


def getCompanionIntroAttachment(messages: list[dict[str, Any]] | None = None, config: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    if config and config.get("companionMuted"):
        return []
    companion = getCompanion(config)
    if companion is None:
        return []
    for msg in messages or []:
        attachment = msg.get("attachment") if isinstance(msg, dict) else None
        if isinstance(attachment, dict) and attachment.get("type") == "companion_intro" and attachment.get("name") == companion.name:
            return []
    return [{"type": "companion_intro", "name": companion.name, "species": companion.species}]
