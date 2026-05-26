from __future__ import annotations

from typing import Any

from ._notification import first_mapping, notification, pick, truthy


async def useNpmDeprecationNotification(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    deprecated = truthy(pick(options, "deprecated", default=False))
    package = str(pick(options, "package", "name", default="package"))
    return notification(
        visible=deprecated,
        level="warning",
        title="Deprecated package",
        message=f"{package} is deprecated for DeepSeek Code installs.",
        package=package,
    )
