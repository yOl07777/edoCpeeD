"""Implementation for `/exit` and `/quit`."""

from __future__ import annotations

import random
from typing import Any, Callable

GOODBYE_MESSAGES = ("Goodbye!", "See ya!", "Bye!", "Catch you later!")


def getRandomGoodbyeMessage(seed: int | None = None) -> str:
    rng = random.Random(seed) if seed is not None else random
    return rng.choice(GOODBYE_MESSAGES)


async def call(onDone: Callable[..., Any] | None = None, *_args: Any, **kwargs: Any) -> dict[str, Any]:
    message = str(kwargs.get("message") or getRandomGoodbyeMessage(kwargs.get("seed")))
    if onDone:
        onDone(message)
    return {"ok": True, "exit": True, "message": message, "code": int(kwargs.get("code", 0))}
