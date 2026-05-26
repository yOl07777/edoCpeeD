from __future__ import annotations

from typing import Any

from ._notification import first_mapping, notification, pick, truthy


async def useLspInitializationNotification(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    initializing = truthy(pick(options, "initializing", default=False))
    language = str(pick(options, "language", default="language server"))
    return notification(
        visible=initializing,
        title="LSP initializing",
        message=f"Starting {language} support for DeepSeek Code.",
        language=language,
    )
