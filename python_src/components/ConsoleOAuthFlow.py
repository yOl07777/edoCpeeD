from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option


async def ConsoleOAuthFlow(*args: Any, **kwargs: Any) -> Any:
    url = str(option(args, kwargs, "url", option(args, kwargs, "verificationUri", "")))
    code = str(option(args, kwargs, "code", option(args, kwargs, "userCode", "")))
    return component_payload("console_oauth_flow", url=url, code=code, waiting=bool(url or code), opensBrowser=False)


__all__ = ["ConsoleOAuthFlow"]
