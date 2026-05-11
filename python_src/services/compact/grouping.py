from __future__ import annotations

from typing import Any


async def groupMessagesByApiRound(messages: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    rounds: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    for message in messages:
        role = message.get("role")
        if role == "user" and current:
            rounds.append(current)
            current = []
        current.append(message)
    if current:
        rounds.append(current)
    return rounds
