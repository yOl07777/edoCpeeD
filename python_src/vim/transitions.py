from __future__ import annotations

from typing import Any

from python_src.vim.motions import resolveMotion
from python_src.vim.operators import (
    executeIndent,
    executeJoin,
    executeLineOp,
    executeOpenLine,
    executeOperatorFind,
    executeOperatorG,
    executeOperatorGg,
    executeOperatorMotion,
    executeOperatorTextObj,
    executePaste,
    executeReplace,
    executeToggleCase,
    executeX,
)
from python_src.vim.types import (
    FIND_KEYS,
    MAX_VIM_COUNT,
    OPERATORS,
    SIMPLE_MOTIONS,
    TEXT_OBJ_SCOPES,
    TEXT_OBJ_TYPES,
    isOperatorKey,
    isTextObjScopeKey,
)


def transition(state: dict[str, Any], input: str, ctx: Any) -> dict[str, Any]:
    kind = state.get("type", "idle")
    if kind == "idle":
        return _from_idle(input, ctx)
    if kind == "count":
        return _from_count(state, input, ctx)
    if kind == "operator":
        return _from_operator(state, input, ctx)
    if kind == "operatorCount":
        return _from_operator_count(state, input, ctx)
    if kind == "operatorFind":
        return {"execute": lambda: executeOperatorFind(state["op"], state["find"], input, state["count"], ctx)}
    if kind == "operatorTextObj":
        if input in TEXT_OBJ_TYPES:
            return {"execute": lambda: executeOperatorTextObj(state["op"], state["scope"], input, state["count"], ctx)}
        return {"next": {"type": "idle"}}
    if kind == "find":
        return {"execute": lambda: _execute_find(state["find"], input, state["count"], ctx)}
    if kind == "g":
        return _from_g(state, input, ctx)
    if kind == "operatorG":
        if input == "g":
            return {"execute": lambda: executeOperatorGg(state["op"], state["count"], ctx)}
        if input in {"j", "k"}:
            return {"execute": lambda: executeOperatorMotion(state["op"], f"g{input}", state["count"], ctx)}
        return {"next": {"type": "idle"}}
    if kind == "replace":
        return {"next": {"type": "idle"}} if input == "" else {"execute": lambda: executeReplace(input, state["count"], ctx)}
    if kind == "indent":
        if input == state["dir"]:
            return {"execute": lambda: executeIndent(state["dir"], state["count"], ctx)}
        return {"next": {"type": "idle"}}
    return {"next": {"type": "idle"}}


def _get(ctx: Any, key: str, default: Any = None) -> Any:
    return ctx.get(key, default) if isinstance(ctx, dict) else getattr(ctx, key, default)


def _call(ctx: Any, key: str, *args: Any) -> None:
    fn = _get(ctx, key)
    if callable(fn):
        fn(*args)
    elif isinstance(ctx, dict) and key == "setOffset":
        ctx["offset"] = args[0]


def _cursor(ctx: Any) -> dict[str, Any]:
    cursor = _get(ctx, "cursor")
    if isinstance(cursor, dict):
        return cursor
    return {"text": _get(ctx, "text", ""), "offset": _get(cursor, "offset", _get(ctx, "offset", 0))}


def _normal(input: str, count: int, ctx: Any) -> dict[str, Any] | None:
    if isOperatorKey(input):
        return {"next": {"type": "operator", "op": OPERATORS[input], "count": count}}
    if input in SIMPLE_MOTIONS:
        return {"execute": lambda: _call(ctx, "setOffset", resolveMotion(input, _cursor(ctx), count)["offset"])}
    if input in FIND_KEYS:
        return {"next": {"type": "find", "find": input, "count": count}}
    if input == "g":
        return {"next": {"type": "g", "count": count}}
    if input == "r":
        return {"next": {"type": "replace", "count": count}}
    if input in {">", "<"}:
        return {"next": {"type": "indent", "dir": input, "count": count}}
    if input == "~":
        return {"execute": lambda: executeToggleCase(count, ctx)}
    if input == "x":
        return {"execute": lambda: executeX(count, ctx)}
    if input == "J":
        return {"execute": lambda: executeJoin(count, ctx)}
    if input in {"p", "P"}:
        return {"execute": lambda: executePaste(input == "p", count, ctx)}
    if input == "D":
        return {"execute": lambda: executeOperatorMotion("delete", "$", 1, ctx)}
    if input == "C":
        return {"execute": lambda: executeOperatorMotion("change", "$", 1, ctx)}
    if input == "Y":
        return {"execute": lambda: executeLineOp("yank", count, ctx)}
    if input == "i":
        return {"execute": lambda: _call(ctx, "enterInsert", _cursor(ctx)["offset"])}
    if input == "o":
        return {"execute": lambda: executeOpenLine("below", ctx)}
    if input == "O":
        return {"execute": lambda: executeOpenLine("above", ctx)}
    if input == ".":
        return {"execute": lambda: (_get(ctx, "onDotRepeat") or (lambda: None))()}
    if input == "u":
        return {"execute": lambda: (_get(ctx, "onUndo") or (lambda: None))()}
    return None


def _operator_input(op: str, count: int, input: str, ctx: Any) -> dict[str, Any] | None:
    if isTextObjScopeKey(input):
        return {"next": {"type": "operatorTextObj", "op": op, "count": count, "scope": TEXT_OBJ_SCOPES[input]}}
    if input in FIND_KEYS:
        return {"next": {"type": "operatorFind", "op": op, "count": count, "find": input}}
    if input in SIMPLE_MOTIONS:
        return {"execute": lambda: executeOperatorMotion(op, input, count, ctx)}
    if input == "G":
        return {"execute": lambda: executeOperatorG(op, count, ctx)}
    if input == "g":
        return {"next": {"type": "operatorG", "op": op, "count": count}}
    return None


def _from_idle(input: str, ctx: Any) -> dict[str, Any]:
    if input.isdigit() and input != "0":
        return {"next": {"type": "count", "digits": input}}
    if input == "0":
        return {"execute": lambda: _call(ctx, "setOffset", resolveMotion("0", _cursor(ctx), 1)["offset"])}
    return _normal(input, 1, ctx) or {}


def _from_count(state: dict[str, Any], input: str, ctx: Any) -> dict[str, Any]:
    if input.isdigit():
        digits = str(min(int(state["digits"] + input), MAX_VIM_COUNT))
        return {"next": {"type": "count", "digits": digits}}
    return _normal(input, int(state["digits"]), ctx) or {"next": {"type": "idle"}}


def _from_operator(state: dict[str, Any], input: str, ctx: Any) -> dict[str, Any]:
    if input == state["op"][0]:
        return {"execute": lambda: executeLineOp(state["op"], state["count"], ctx)}
    if input.isdigit():
        return {"next": {"type": "operatorCount", "op": state["op"], "count": state["count"], "digits": input}}
    return _operator_input(state["op"], state["count"], input, ctx) or {"next": {"type": "idle"}}


def _from_operator_count(state: dict[str, Any], input: str, ctx: Any) -> dict[str, Any]:
    if input.isdigit():
        return {"next": {**state, "digits": str(min(int(state["digits"] + input), MAX_VIM_COUNT))}}
    return _operator_input(state["op"], state["count"] * int(state["digits"]), input, ctx) or {"next": {"type": "idle"}}


def _from_g(state: dict[str, Any], input: str, ctx: Any) -> dict[str, Any]:
    if input in {"j", "k"}:
        return {"execute": lambda: _call(ctx, "setOffset", resolveMotion(f"g{input}", _cursor(ctx), state["count"])["offset"])}
    if input == "g":
        return {"execute": lambda: _call(ctx, "setOffset", resolveMotion("gg", _cursor(ctx), 1)["offset"])}
    return {"next": {"type": "idle"}}


def _execute_find(find: str, char: str, count: int, ctx: Any) -> None:
    from python_src.vim.operators import _find_char

    cursor = _cursor(ctx)
    result = _find_char(cursor["text"], cursor["offset"], find, char, count)
    if result is not None:
        _call(ctx, "setOffset", result)
        _call(ctx, "setLastFind", find, char)
