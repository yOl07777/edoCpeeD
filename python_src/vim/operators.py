from __future__ import annotations

from typing import Any

from python_src.vim.motions import isInclusiveMotion, isLinewiseMotion, resolveMotion
from python_src.vim.textObjects import findTextObject


def _get(ctx: Any, key: str, default: Any = None) -> Any:
    return ctx.get(key, default) if isinstance(ctx, dict) else getattr(ctx, key, default)


def _call(ctx: Any, name: str, *args: Any) -> None:
    fn = _get(ctx, name)
    if callable(fn):
        fn(*args)
        return
    if isinstance(ctx, dict):
        if name == "setText":
            ctx["text"] = args[0]
        elif name == "setOffset":
            ctx["offset"] = args[0]
        elif name == "enterInsert":
            ctx["mode"] = "INSERT"
            ctx["offset"] = args[0]
        elif name == "setRegister":
            ctx["register"] = args[0]
            ctx["registerIsLinewise"] = bool(args[1]) if len(args) > 1 else False
        elif name == "setLastFind":
            ctx["lastFind"] = {"type": args[0], "char": args[1]}
        elif name == "recordChange":
            ctx["lastChange"] = args[0]


def _text(ctx: Any) -> str:
    return str(_get(ctx, "text", ""))


def _offset(ctx: Any) -> int:
    cursor = _get(ctx, "cursor")
    if isinstance(cursor, dict):
        return int(cursor.get("offset", _get(ctx, "offset", 0)))
    return int(getattr(cursor, "offset", _get(ctx, "offset", 0)))


def _cursor(ctx: Any) -> dict[str, Any]:
    return {"text": _text(ctx), "offset": _offset(ctx)}


def _line_col(text: str, offset: int) -> tuple[int, int, list[str]]:
    lines = text.split("\n")
    current = 0
    remaining = offset
    for index, line in enumerate(lines):
        if remaining <= len(line):
            current = index
            break
        remaining -= len(line) + 1
    return current, remaining, lines


def _line_start(lines: list[str], index: int) -> int:
    return len("\n".join(lines[:index])) + (1 if index > 0 else 0)


def _set_register(ctx: Any, content: str, linewise: bool = False) -> None:
    _call(ctx, "setRegister", content, linewise)


def _record(ctx: Any, change: dict[str, Any]) -> None:
    _call(ctx, "recordChange", change)


def _apply_operator(op: str, start: int, end: int, ctx: Any, linewise: bool = False) -> None:
    text = _text(ctx)
    start, end = sorted((max(0, start), min(len(text), end)))
    content = text[start:end]
    if linewise and not content.endswith("\n"):
        content += "\n"
    _set_register(ctx, content, linewise)
    if op == "yank":
        _call(ctx, "setOffset", start)
    elif op == "delete":
        new_text = text[:start] + text[end:]
        _call(ctx, "setText", new_text)
        _call(ctx, "setOffset", min(start, max(0, len(new_text) - 1)))
    elif op == "change":
        new_text = text[:start] + text[end:]
        _call(ctx, "setText", new_text)
        _call(ctx, "enterInsert", start)


def executeOperatorMotion(op: str, motion: str, count: int, ctx: Any) -> None:
    cursor = _cursor(ctx)
    target = resolveMotion(motion, cursor, count)
    start, end = sorted((cursor["offset"], target["offset"]))
    linewise = isLinewiseMotion(motion)
    if isInclusiveMotion(motion) and end < len(cursor["text"]):
        end += 1
    _apply_operator(op, start, end, ctx, linewise)
    _record(ctx, {"type": "operator", "op": op, "motion": motion, "count": count})


def executeOperatorFind(op: str, findType: str, char: str, count: int, ctx: Any) -> None:
    text = _text(ctx)
    offset = _offset(ctx)
    pos = _find_char(text, offset, findType, char, count)
    if pos is None:
        return
    start, end = sorted((offset, pos))
    _apply_operator(op, start, min(len(text), end + 1), ctx)
    _call(ctx, "setLastFind", findType, char)
    _record(ctx, {"type": "operatorFind", "op": op, "find": findType, "char": char, "count": count})


def executeOperatorTextObj(op: str, scope: str, objType: str, count: int, ctx: Any) -> None:
    text = _text(ctx)
    found = findTextObject(text, _offset(ctx), objType, scope == "inner")
    if not found:
        return
    _apply_operator(op, found["start"], found["end"], ctx)
    _record(ctx, {"type": "operatorTextObj", "op": op, "objType": objType, "scope": scope, "count": count})


def executeLineOp(op: str, count: int, ctx: Any) -> None:
    text = _text(ctx)
    line, _col, lines = _line_col(text, _offset(ctx))
    start = _line_start(lines, line)
    end_line = min(len(lines), line + max(1, count))
    end = _line_start(lines, end_line) if end_line < len(lines) else len(text)
    _apply_operator(op, start, end, ctx, True)
    _record(ctx, {"type": "operator", "op": op, "motion": op[0], "count": count})


def executeX(count: int, ctx: Any) -> None:
    start = _offset(ctx)
    _apply_operator("delete", start, start + max(1, count), ctx)
    _record(ctx, {"type": "x", "count": count})


def executeReplace(char: str, count: int, ctx: Any) -> None:
    text = _text(ctx)
    offset = _offset(ctx)
    end = min(len(text), offset + max(1, count))
    new_text = text[:offset] + (char * (end - offset)) + text[end:]
    _call(ctx, "setText", new_text)
    _call(ctx, "setOffset", max(0, end - 1))
    _record(ctx, {"type": "replace", "char": char, "count": count})


def executeToggleCase(count: int, ctx: Any) -> None:
    text = _text(ctx)
    offset = _offset(ctx)
    chars = list(text)
    for i in range(offset, min(len(chars), offset + max(1, count))):
        chars[i] = chars[i].lower() if chars[i].isupper() else chars[i].upper()
    _call(ctx, "setText", "".join(chars))
    _call(ctx, "setOffset", min(len(chars), offset + max(1, count)))
    _record(ctx, {"type": "toggleCase", "count": count})


def executeJoin(count: int, ctx: Any) -> None:
    text = _text(ctx)
    line, _col, lines = _line_col(text, _offset(ctx))
    if line >= len(lines) - 1:
        return
    take = min(max(1, count), len(lines) - line - 1)
    joined = lines[line]
    for extra in lines[line + 1 : line + take + 1]:
        stripped = extra.lstrip()
        if stripped:
            joined += ("" if joined.endswith(" ") or not joined else " ") + stripped
    new_lines = lines[:line] + [joined] + lines[line + take + 1 :]
    _call(ctx, "setText", "\n".join(new_lines))
    _call(ctx, "setOffset", _line_start(new_lines, line))
    _record(ctx, {"type": "join", "count": count})


def executePaste(after: bool, count: int, ctx: Any) -> None:
    register = _get(ctx, "getRegister", lambda: _get(ctx, "register", ""))()
    if not register:
        return
    text = _text(ctx)
    offset = _offset(ctx) + (1 if after and _offset(ctx) < len(text) else 0)
    payload = str(register) * max(1, count)
    new_text = text[:offset] + payload + text[offset:]
    _call(ctx, "setText", new_text)
    _call(ctx, "setOffset", offset + len(payload) - 1)


def executeIndent(dir: str, count: int, ctx: Any) -> None:
    text = _text(ctx)
    line, _col, lines = _line_col(text, _offset(ctx))
    for i in range(line, min(len(lines), line + max(1, count))):
        if dir == ">":
            lines[i] = "  " + lines[i]
        else:
            lines[i] = lines[i][2:] if lines[i].startswith("  ") else lines[i].lstrip() if lines[i].startswith("\t") else lines[i]
    _call(ctx, "setText", "\n".join(lines))
    _call(ctx, "setOffset", _line_start(lines, line))
    _record(ctx, {"type": "indent", "dir": dir, "count": count})


def executeOpenLine(direction: str, ctx: Any) -> None:
    text = _text(ctx)
    line, _col, lines = _line_col(text, _offset(ctx))
    insert_at = line + 1 if direction == "below" else line
    new_lines = lines[:insert_at] + [""] + lines[insert_at:]
    _call(ctx, "setText", "\n".join(new_lines))
    _call(ctx, "enterInsert", _line_start(new_lines, insert_at))
    _record(ctx, {"type": "openLine", "direction": direction})


def executeOperatorG(op: str, count: int, ctx: Any) -> None:
    motion = "G"
    executeOperatorMotion(op, motion, count, ctx)


def executeOperatorGg(op: str, count: int, ctx: Any) -> None:
    executeOperatorMotion(op, "gg", count, ctx)


def _find_char(text: str, offset: int, find_type: str, char: str, count: int) -> int | None:
    if find_type in {"f", "t"}:
        pos = offset
        for _ in range(max(1, count)):
            pos = text.find(char, pos + 1)
            if pos == -1:
                return None
        return max(offset, pos - 1) if find_type == "t" else pos
    pos = offset
    for _ in range(max(1, count)):
        pos = text.rfind(char, 0, pos)
        if pos == -1:
            return None
    return min(offset, pos + 1) if find_type == "T" else pos
