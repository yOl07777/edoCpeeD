from __future__ import annotations

from typing import Any

from python_src.components.PromptInput.inputPaste import maybeTruncateInput


async def useMaybeTruncateInput(*args: Any, **kwargs: Any) -> Any:
    return await maybeTruncateInput(*args, **kwargs)


__all__ = ["useMaybeTruncateInput"]
