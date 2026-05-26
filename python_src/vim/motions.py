from __future__ import annotations

import re
from typing import Any


WORD_RE = re.compile(r"\w+|\W+", re.UNICODE)


def _text(cursor: Any) -> str:
    if isinstance(cursor, dict):
        return str(cursor.get("text", ""))
    return str(getattr(cursor, "text", getattr(getattr(cursor, "measuredText", None), "text", "")))


def _offset(cursor: Any) -> int:
    return int(cursor.get("offset", 0) if isinstance(cursor, dict) else getattr(cursor, "offset", 0))


def _make(cursor: Any, offset: int) -> Any:
    text = _text(cursor)
    offset = max(0, min(offset, len(text)))
    if isinstance(cursor, dict):
        result = dict(cursor)
        result["offset"] = offset
        result.setdefault("text", text)
        return result
    try:
        return cursor.__class__(getattr(cursor, "measuredText", text), offset)
    except Exception:
        return {"text": text, "offset": offset}


def _line_bounds(text: str, offset: int) -> tuple[int, int]:
    start = text.rfind("\n", 0, offset) + 1
    end = text.find("\n", offset)
    return start, len(text) if end == -1 else end


def _line_starts(text: str) -> list[int]:
    return [0] + [match.end() for match in re.finditer("\n", text)]


def _line_col(text: str, offset: int) -> tuple[int, int]:
    starts = _line_starts(text)
    line = max(i for i, start in enumerate(starts) if start <= offset)
    return line, offset - starts[line]


def _offset_for_line_col(text: str, line: int, col: int) -> int:
    starts = _line_starts(text)
    line = max(0, min(line, len(starts) - 1))
    start = starts[line]
    end = text.find("\n", start)
    end = len(text) if end == -1 else end
    return min(start + col, end)


def _next_word(text: str, offset: int) -> int:
    start_at = offset + 1
    for match in WORD_RE.finditer(text):
        if match.start() <= offset < match.end() and match.group(0).strip():
            start_at = match.end()
            break
    for match in WORD_RE.finditer(text, start_at):
        if match.group(0).strip() and re.match(r"\w", match.group(0)[0]):
            return match.start()
    return len(text)


def _prev_word(text: str, offset: int) -> int:
    previous = 0
    for match in WORD_RE.finditer(text, 0, max(0, offset)):
        if match.group(0).strip() and re.match(r"\w", match.group(0)[0]):
            previous = match.start()
    return previous


def _end_word(text: str, offset: int) -> int:
    for match in WORD_RE.finditer(text, offset):
        if match.group(0).strip() and re.match(r"\w", match.group(0)[0]):
            return max(match.end() - 1, match.start())
    return max(0, len(text) - 1)


def resolveMotion(key: str, cursor: Any, count: int) -> Any:
    result = cursor
    for _ in range(max(1, int(count))):
        text = _text(result)
        offset = _offset(result)
        line, col = _line_col(text, offset)
        if key == "h":
            offset -= 1
        elif key == "l":
            offset += 1
        elif key in {"j", "gj"}:
            offset = _offset_for_line_col(text, line + 1, col)
        elif key in {"k", "gk"}:
            offset = _offset_for_line_col(text, line - 1, col)
        elif key in {"w", "W"}:
            offset = _next_word(text, offset)
        elif key in {"b", "B"}:
            offset = _prev_word(text, offset)
        elif key in {"e", "E"}:
            offset = _end_word(text, offset)
        elif key == "0":
            offset = _line_bounds(text, offset)[0]
        elif key == "^":
            start, end = _line_bounds(text, offset)
            line_text = text[start:end]
            offset = start + (len(line_text) - len(line_text.lstrip()))
        elif key == "$":
            offset = _line_bounds(text, offset)[1]
        elif key == "G":
            offset = _line_starts(text)[-1]
        elif key == "gg":
            offset = 0
        result = _make(result, offset)
    return result


def isInclusiveMotion(key: str) -> bool:
    return key in {"e", "E", "$"}


def isLinewiseMotion(key: str) -> bool:
    return key in {"j", "k", "G", "gg"}
