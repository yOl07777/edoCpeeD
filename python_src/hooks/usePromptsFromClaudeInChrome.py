from __future__ import annotations

from typing import Any

from ._basic import first_mapping, pick


async def usePromptsFromClaudeInChrome(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    url = str(pick(options, "url", "currentUrl", default=""))
    selected = str(pick(options, "selection", "selectedText", default="")).strip()
    prompts = [
        "Summarize this page for DeepSeek Code.",
        "Extract action items from this page.",
    ]
    if selected:
        prompts.insert(0, f"Explain this selected text: {selected}")
    return {"provider": "deepseek", "url": url, "prompts": prompts, "source": "chrome"}
