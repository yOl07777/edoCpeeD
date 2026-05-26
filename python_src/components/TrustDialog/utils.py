from __future__ import annotations

from typing import Any


async def formatListWithAnd(*args: Any, **kwargs: Any) -> Any:
    items = kwargs.get("items") or (args[0] if args else []) or []
    items = [str(item) for item in items]
    if len(items) <= 1:
        return "".join(items)
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{', '.join(items[:-1])}, and {items[-1]}"


def _source_payload(name: str, sources: Any) -> dict[str, Any]:
    if sources is None:
        sources = []
    if isinstance(sources, str):
        sources = [sources]
    return {"category": name, "sources": [str(source) for source in sources], "count": len(sources)}


async def getApiKeyHelperSources(*args: Any, **kwargs: Any) -> Any:
    sources = kwargs.get("sources") if "sources" in kwargs else (args[0] if args else None)
    return _source_payload("api_keys", sources if sources is not None else ["DEEPSEEK_API_KEYS", ".env"])


async def getAwsCommandsSources(*args: Any, **kwargs: Any) -> Any:
    return _source_payload("aws_commands", kwargs.get("sources") or (args[0] if args else []))


async def getBashPermissionSources(*args: Any, **kwargs: Any) -> Any:
    return _source_payload("shell_permissions", kwargs.get("sources") or (args[0] if args else []))


async def getDangerousEnvVarsSources(*args: Any, **kwargs: Any) -> Any:
    return _source_payload("dangerous_env_vars", kwargs.get("sources") or (args[0] if args else []))


async def getGcpCommandsSources(*args: Any, **kwargs: Any) -> Any:
    return _source_payload("gcp_commands", kwargs.get("sources") or (args[0] if args else []))


async def getHooksSources(*args: Any, **kwargs: Any) -> Any:
    return _source_payload("hooks", kwargs.get("sources") or (args[0] if args else []))


async def getOtelHeadersHelperSources(*args: Any, **kwargs: Any) -> Any:
    return _source_payload("otel_headers", kwargs.get("sources") or (args[0] if args else []))


__all__ = [
    "formatListWithAnd",
    "getApiKeyHelperSources",
    "getAwsCommandsSources",
    "getBashPermissionSources",
    "getDangerousEnvVarsSources",
    "getGcpCommandsSources",
    "getHooksSources",
    "getOtelHeadersHelperSources",
]
