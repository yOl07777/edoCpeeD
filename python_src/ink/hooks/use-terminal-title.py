from __future__ import annotations

from typing import Any

async def useTerminalTitle(*args: Any, **kwargs: Any) -> Any:
    title = str(args[0] if args else kwargs.get("title", "DeepSeek Code"))
    return {"provider": "deepseek", "title": title, "sequence": f"\x1b]0;{title}\x1b\\"}
