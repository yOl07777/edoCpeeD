from __future__ import annotations

from typing import Any

from ._basic import first_mapping, listify, pick, text_filter


def _replace_token(value: str, token: str, replacement: str) -> str:
    if token and token in value:
        before, _, after = value.rpartition(token)
        return f"{before}{replacement}{after}"
    return f"{value}{replacement}"


async def applyDirectorySuggestion(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    value = str(pick(options, "value", "input", default=args[0] if args and not isinstance(args[0], dict) else ""))
    suggestion = str(pick(options, "suggestion", default=args[1] if len(args) > 1 else ""))
    token = await extractCompletionToken(value)
    return _replace_token(value, str(token["token"]), suggestion)

async def applyShellSuggestion(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    value = str(pick(options, "value", "input", default=args[0] if args and not isinstance(args[0], dict) else ""))
    suggestion = str(pick(options, "suggestion", default=args[1] if len(args) > 1 else ""))
    token = await extractSearchToken(value)
    return _replace_token(value, str(token["token"]), suggestion)

async def extractCompletionToken(*args: Any, **kwargs: Any) -> Any:
    value = str(args[0] if args else kwargs.get("value", ""))
    cursor = int(kwargs.get("cursor", len(value)))
    prefix = value[:cursor]
    token = prefix.split()[-1] if prefix.split() else ""
    return {"provider": "deepseek", "token": token, "start": cursor - len(token), "end": cursor}

async def extractSearchToken(*args: Any, **kwargs: Any) -> Any:
    return await extractCompletionToken(*args, **kwargs)

async def formatReplacementValue(*args: Any, **kwargs: Any) -> Any:
    value = str(args[0] if args else kwargs.get("value", ""))
    kind = str(kwargs.get("kind", "text"))
    if kind == "directory" and value and not value.endswith(("/", "\\")):
        return value + "/"
    return value

async def useTypeahead(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    value = str(pick(options, "value", "input", default=""))
    token = await extractCompletionToken(value, cursor=int(pick(options, "cursor", default=len(value))))
    suggestions = text_filter(listify(pick(options, "suggestions", default=[])), str(token["token"]))
    return {"provider": "deepseek", "token": token, "suggestions": suggestions, "active": suggestions[0] if suggestions else None}
