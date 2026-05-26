"""Command metadata for `/cost`."""

from __future__ import annotations

import os

from .cost import cost_command


async def call(*_args, **_kwargs):
    summary = await cost_command("summary")
    return {
        "type": "text",
        "value": (
            "Session cost summary:\n"
            f"Input tokens: {summary['input_tokens']}\n"
            f"Output tokens: {summary['output_tokens']}\n"
            f"Total USD: ${summary['total_usd']:.6f}"
        ),
    }


cost = {
    "type": "local",
    "name": "cost",
    "description": "Show the total cost and duration of the current session",
    "isHidden": lambda: os.getenv("USER_TYPE") != "ant" and os.getenv("DEEPSEEK_HIDE_COST_COMMAND") == "1",
    "supportsNonInteractive": True,
    "call": call,
}

default = cost
