from __future__ import annotations

import re


PAIRS = {
    "(": ("(", ")"),
    ")": ("(", ")"),
    "b": ("(", ")"),
    "[": ("[", "]"),
    "]": ("[", "]"),
    "{": ("{", "}"),
    "}": ("{", "}"),
    "B": ("{", "}"),
    "<": ("<", ">"),
    ">": ("<", ">"),
    '"': ('"', '"'),
    "'": ("'", "'"),
    "`": ("`", "`"),
}


def _is_word(ch: str) -> bool:
    return bool(re.match(r"\w", ch, re.UNICODE))


def findTextObject(text: str, offset: int, objectType: str, isInner: bool) -> dict[str, int] | None:
    text = text or ""
    offset = max(0, min(offset, max(0, len(text) - 1)))
    if objectType in {"w", "W"}:
        return _find_word_object(text, offset, isInner, objectType == "W")
    pair = PAIRS.get(objectType)
    if not pair:
        return None
    open_ch, close_ch = pair
    if open_ch == close_ch:
        return _find_quote_object(text, offset, open_ch, isInner)
    return _find_bracket_object(text, offset, open_ch, close_ch, isInner)


def _find_word_object(text: str, offset: int, is_inner: bool, big_word: bool) -> dict[str, int] | None:
    if not text:
        return None

    def member(ch: str) -> bool:
        return not ch.isspace() if big_word else _is_word(ch)

    if not member(text[offset]):
        right = next((i for i in range(offset + 1, len(text)) if member(text[i])), None)
        left = next((i for i in range(offset - 1, -1, -1) if member(text[i])), None)
        if right is None and left is None:
            return None
        offset = right if right is not None else left  # type: ignore[assignment]

    start = offset
    end = offset + 1
    while start > 0 and member(text[start - 1]):
        start -= 1
    while end < len(text) and member(text[end]):
        end += 1
    if not is_inner:
        if end < len(text) and text[end].isspace():
            while end < len(text) and text[end].isspace():
                end += 1
        else:
            while start > 0 and text[start - 1].isspace():
                start -= 1
    return {"start": start, "end": end}


def _find_quote_object(text: str, offset: int, quote: str, is_inner: bool) -> dict[str, int] | None:
    line_start = text.rfind("\n", 0, offset) + 1
    line_end = text.find("\n", offset)
    if line_end == -1:
        line_end = len(text)
    positions = [line_start + i for i, ch in enumerate(text[line_start:line_end]) if ch == quote]
    for start, end in zip(positions[0::2], positions[1::2]):
        if start <= offset <= end:
            return {"start": start + 1, "end": end} if is_inner else {"start": start, "end": end + 1}
    return None


def _find_bracket_object(text: str, offset: int, open_ch: str, close_ch: str, is_inner: bool) -> dict[str, int] | None:
    depth = 0
    start = -1
    for i in range(offset, -1, -1):
        if text[i] == close_ch and i != offset:
            depth += 1
        elif text[i] == open_ch:
            if depth == 0:
                start = i
                break
            depth -= 1
    if start == -1:
        return None
    depth = 0
    end = -1
    for i in range(start + 1, len(text)):
        if text[i] == open_ch:
            depth += 1
        elif text[i] == close_ch:
            if depth == 0:
                end = i
                break
            depth -= 1
    if end == -1:
        return None
    return {"start": start + 1, "end": end} if is_inner else {"start": start, "end": end + 1}
