"""File edit utility helpers."""

from __future__ import annotations

import difflib
from typing import Any

from python_src.tools.FileEditTool.FileEditTool import edit_file

LEFT_DOUBLE_CURLY_QUOTE = "\u201c"
RIGHT_DOUBLE_CURLY_QUOTE = "\u201d"
LEFT_SINGLE_CURLY_QUOTE = "\u2018"
RIGHT_SINGLE_CURLY_QUOTE = "\u2019"


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    return dict(kwargs)


def _old_new(data: dict[str, Any]) -> tuple[str, str]:
    old = data.get("old_text", data.get("oldText", ""))
    new = data.get("new_text", data.get("newText", ""))
    return str(old), str(new)


def _strip_trailing(value: str) -> str:
    return "\n".join(line.rstrip() for line in value.splitlines())


def _normalize_quotes(value: str) -> str:
    return (
        value.replace(LEFT_DOUBLE_CURLY_QUOTE, '"')
        .replace(RIGHT_DOUBLE_CURLY_QUOTE, '"')
        .replace(LEFT_SINGLE_CURLY_QUOTE, "'")
        .replace(RIGHT_SINGLE_CURLY_QUOTE, "'")
    )


def _patch(old: str, new: str, *, path: str = "file") -> str:
    return "\n".join(
        difflib.unified_diff(
            old.splitlines(),
            new.splitlines(),
            fromfile=f"a/{path}",
            tofile=f"b/{path}",
            lineterm="",
        )
    )


async def stripTrailingWhitespace(*args: Any, **kwargs: Any) -> str:
    value = str(args[0] if args else kwargs.get("text", ""))
    return _strip_trailing(value)


async def normalizeQuotes(*args: Any, **kwargs: Any) -> str:
    value = str(args[0] if args else kwargs.get("text", ""))
    return _normalize_quotes(value)


async def preserveQuoteStyle(*args: Any, **kwargs: Any) -> str:
    data = _payload(args, kwargs)
    source = str(data.get("source") or data.get("old_text") or data.get("oldText") or "")
    replacement = str(data.get("replacement") or data.get("new_text") or data.get("newText") or "")
    if any(ch in source for ch in (LEFT_DOUBLE_CURLY_QUOTE, RIGHT_DOUBLE_CURLY_QUOTE)):
        replacement = replacement.replace('"', LEFT_DOUBLE_CURLY_QUOTE, 1)
        if replacement.count('"'):
            replacement = replacement.replace('"', RIGHT_DOUBLE_CURLY_QUOTE, 1)
    if any(ch in source for ch in (LEFT_SINGLE_CURLY_QUOTE, RIGHT_SINGLE_CURLY_QUOTE)):
        replacement = replacement.replace("'", LEFT_SINGLE_CURLY_QUOTE, 1)
        if replacement.count("'"):
            replacement = replacement.replace("'", RIGHT_SINGLE_CURLY_QUOTE, 1)
    return replacement


async def normalizeFileEditInput(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    old, new = _old_new(data)
    return {
        **data,
        "old_text": await normalizeQuotes(await stripTrailingWhitespace(old)),
        "new_text": await normalizeQuotes(await stripTrailingWhitespace(new)),
        "replace_all": bool(data.get("replace_all") or data.get("replaceAll", False)),
    }


async def areFileEditsInputsEquivalent(*args: Any, **kwargs: Any) -> bool:
    data = _payload(args, kwargs)
    left = data.get("left") or data.get("a") or (args[0] if args else {})
    right = data.get("right") or data.get("b") or (args[1] if len(args) > 1 else {})
    left_norm = await normalizeFileEditInput(left if isinstance(left, dict) else {"old_text": left})
    right_norm = await normalizeFileEditInput(right if isinstance(right, dict) else {"old_text": right})
    return (
        left_norm.get("path") == right_norm.get("path")
        and left_norm["old_text"] == right_norm["old_text"]
        and left_norm["new_text"] == right_norm["new_text"]
    )


async def areFileEditsEquivalent(*args: Any, **kwargs: Any) -> bool:
    return await areFileEditsInputsEquivalent(*args, **kwargs)


async def findActualString(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    content = str(data.get("content") if "content" in data else (args[0] if args else ""))
    needle = str(data.get("needle") or data.get("old_text") or data.get("oldText") or (args[1] if len(args) > 1 else ""))
    candidates = [needle, _normalize_quotes(needle), _strip_trailing(needle)]
    for candidate in candidates:
        index = content.find(candidate)
        if index >= 0:
            return {"found": True, "actual": candidate, "index": index, "count": content.count(candidate)}
    return {"found": False, "actual": None, "index": -1, "count": 0}


async def getPatchForEdit(*args: Any, **kwargs: Any) -> str:
    data = _payload(args, kwargs)
    old, new = _old_new(data)
    path = str(data.get("path") or "file")
    return _patch(old, new, path=path)


async def getPatchForEdits(*args: Any, **kwargs: Any) -> str:
    edits = list(args[0] if args and isinstance(args[0], list) else kwargs.get("edits", []) or [])
    patches = [await getPatchForEdit(edit) for edit in edits if isinstance(edit, dict)]
    return "\n".join(patch for patch in patches if patch)


async def getEditsForPatch(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    patch = str(args[0] if args else kwargs.get("patch", ""))
    return [{"patch": patch, "additions": patch.count("\n+"), "deletions": patch.count("\n-")}]


async def getSnippet(*args: Any, **kwargs: Any) -> str:
    data = _payload(args, kwargs)
    text = str(data.get("text") if "text" in data else (args[0] if args else ""))
    line = int(data.get("line") or data.get("lineNumber") or 1)
    context = int(data.get("context") or 2)
    lines = text.splitlines()
    start = max(line - context - 1, 0)
    end = min(line + context, len(lines))
    return "\n".join(f"{idx + 1}: {lines[idx]}" for idx in range(start, end))


async def getSnippetForPatch(*args: Any, **kwargs: Any) -> str:
    patch = str(args[0] if args else kwargs.get("patch", ""))
    lines = patch.splitlines()
    interesting = [line for line in lines if line.startswith(("@@", "+", "-")) and not line.startswith(("+++", "---"))]
    return "\n".join(interesting[:40])


async def getSnippetForTwoFileDiff(*args: Any, **kwargs: Any) -> str:
    data = _payload(args, kwargs)
    old = str(data.get("old") or data.get("before") or (args[0] if args else ""))
    new = str(data.get("new") or data.get("after") or (args[1] if len(args) > 1 else ""))
    return await getSnippetForPatch(_patch(old, new, path=str(data.get("path") or "file")))


async def applyEditToFile(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    old, new = _old_new(data)
    path = data.get("path")
    if not path:
        raise ValueError("path is required")
    cwd = data.get("cwd")
    result = await edit_file(
        str(path),
        old,
        new,
        cwd=str(cwd) if cwd else None,
        replace_all=bool(data.get("replace_all") or data.get("replaceAll", False)),
    )
    result["patch"] = await getPatchForEdit({"path": path, "old_text": old, "new_text": new})
    return result


__all__ = [
    "LEFT_DOUBLE_CURLY_QUOTE",
    "LEFT_SINGLE_CURLY_QUOTE",
    "RIGHT_DOUBLE_CURLY_QUOTE",
    "RIGHT_SINGLE_CURLY_QUOTE",
    "applyEditToFile",
    "areFileEditsEquivalent",
    "areFileEditsInputsEquivalent",
    "findActualString",
    "getEditsForPatch",
    "getPatchForEdit",
    "getPatchForEdits",
    "getSnippet",
    "getSnippetForPatch",
    "getSnippetForTwoFileDiff",
    "normalizeFileEditInput",
    "normalizeQuotes",
    "preserveQuoteStyle",
    "stripTrailingWhitespace",
]
