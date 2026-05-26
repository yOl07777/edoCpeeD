"""Keybinding matching helpers."""

from __future__ import annotations

from typing import Any


def _flag(key: Any, name: str) -> bool:
    if isinstance(key, dict):
        return bool(key.get(name, False))
    return bool(getattr(key, name, False))


def getKeyName(input: str, key: dict[str, Any] | Any) -> str | None:
    flag_map = [
        ("escape", "escape"),
        ("return", "enter"),
        ("tab", "tab"),
        ("backspace", "backspace"),
        ("delete", "delete"),
        ("upArrow", "up"),
        ("downArrow", "down"),
        ("leftArrow", "left"),
        ("rightArrow", "right"),
        ("pageUp", "pageup"),
        ("pageDown", "pagedown"),
        ("wheelUp", "wheelup"),
        ("wheelDown", "wheeldown"),
        ("home", "home"),
        ("end", "end"),
    ]
    for flag, name in flag_map:
        if _flag(key, flag):
            return name
    if len(input) == 1:
        return input.lower()
    return None


def _modifiers_match(key: dict[str, Any] | Any, target: dict[str, Any], *, ignore_meta: bool = False) -> bool:
    if _flag(key, "ctrl") != bool(target.get("ctrl")):
        return False
    if _flag(key, "shift") != bool(target.get("shift")):
        return False
    target_needs_meta = bool(target.get("alt") or target.get("meta"))
    if (False if ignore_meta else _flag(key, "meta")) != target_needs_meta:
        return False
    if _flag(key, "super") != bool(target.get("super")):
        return False
    return True


def matchesKeystroke(input: str, key: dict[str, Any] | Any, target: dict[str, Any]) -> bool:
    if getKeyName(input, key) != target.get("key"):
        return False
    return _modifiers_match(key, target, ignore_meta=_flag(key, "escape"))


def matchesBinding(input: str, key: dict[str, Any] | Any, binding: dict[str, Any]) -> bool:
    chord = binding.get("chord") or []
    return len(chord) == 1 and matchesKeystroke(input, key, chord[0])
