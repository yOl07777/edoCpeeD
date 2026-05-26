"""Resolve key input to configured actions."""

from __future__ import annotations

from typing import Any

from .match import getKeyName, matchesBinding
from .parser import chordToString


def keystrokesEqual(a: dict[str, Any], b: dict[str, Any]) -> bool:
    return (
        a.get("key") == b.get("key")
        and bool(a.get("ctrl")) == bool(b.get("ctrl"))
        and bool(a.get("shift")) == bool(b.get("shift"))
        and bool(a.get("alt") or a.get("meta")) == bool(b.get("alt") or b.get("meta"))
        and bool(a.get("super")) == bool(b.get("super"))
    )


def resolveKey(input: str, key: dict[str, Any] | Any, activeContexts: list[str], bindings: list[dict[str, Any]]) -> dict[str, Any]:
    ctx = set(activeContexts)
    match = None
    for binding in bindings:
        if len(binding.get("chord") or []) != 1 or binding.get("context") not in ctx:
            continue
        if matchesBinding(input, key, binding):
            match = binding
    if match is None:
        return {"type": "none"}
    if match.get("action") is None:
        return {"type": "unbound"}
    return {"type": "match", "action": match["action"]}


def getBindingDisplayText(action: str, context: str, bindings: list[dict[str, Any]]) -> str | None:
    for binding in reversed(bindings):
        if binding.get("action") == action and binding.get("context") == context:
            return chordToString(binding.get("chord") or [])
    return None


def _build_keystroke(input: str, key: dict[str, Any] | Any) -> dict[str, Any] | None:
    name = getKeyName(input, key)
    if not name:
        return None
    get = key.get if isinstance(key, dict) else lambda n, d=False: getattr(key, n, d)
    effective_meta = False if bool(get("escape", False)) else bool(get("meta", False))
    return {
        "key": name,
        "ctrl": bool(get("ctrl", False)),
        "alt": effective_meta,
        "shift": bool(get("shift", False)),
        "meta": effective_meta,
        "super": bool(get("super", False)),
    }


def _prefix_matches(prefix: list[dict[str, Any]], binding: dict[str, Any]) -> bool:
    chord = binding.get("chord") or []
    return len(prefix) < len(chord) and all(keystrokesEqual(prefix[i], chord[i]) for i in range(len(prefix)))


def _exact_matches(chord: list[dict[str, Any]], binding: dict[str, Any]) -> bool:
    target = binding.get("chord") or []
    return len(chord) == len(target) and all(keystrokesEqual(chord[i], target[i]) for i in range(len(chord)))


def resolveKeyWithChordState(
    input: str,
    key: dict[str, Any] | Any,
    activeContexts: list[str],
    bindings: list[dict[str, Any]],
    pending: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    is_escape = key.get("escape", False) if isinstance(key, dict) else getattr(key, "escape", False)
    if is_escape and pending is not None:
        return {"type": "chord_cancelled"}
    current = _build_keystroke(input, key)
    if current is None:
        return {"type": "chord_cancelled"} if pending is not None else {"type": "none"}
    test_chord = [*(pending or []), current]
    context_bindings = [b for b in bindings if b.get("context") in set(activeContexts)]
    chord_winners: dict[str, Any] = {}
    for binding in context_bindings:
        if _prefix_matches(test_chord, binding):
            chord_winners[chordToString(binding.get("chord") or [])] = binding.get("action")
    if any(action is not None for action in chord_winners.values()):
        return {"type": "chord_started", "pending": test_chord}
    exact = None
    for binding in context_bindings:
        if _exact_matches(test_chord, binding):
            exact = binding
    if exact is not None:
        return {"type": "unbound"} if exact.get("action") is None else {"type": "match", "action": exact["action"]}
    return {"type": "chord_cancelled"} if pending is not None else {"type": "none"}
