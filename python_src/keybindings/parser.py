"""Keybinding parser utilities."""

from __future__ import annotations

from typing import Any

ParsedKeystroke = dict[str, Any]
Chord = list[ParsedKeystroke]


def parseKeystroke(input: str) -> ParsedKeystroke:
    parts = input.split("+")
    stroke: ParsedKeystroke = {"key": "", "ctrl": False, "alt": False, "shift": False, "meta": False, "super": False}
    for part in parts:
        lower = part.strip().lower()
        if lower in {"ctrl", "control"}:
            stroke["ctrl"] = True
        elif lower in {"alt", "opt", "option"}:
            stroke["alt"] = True
        elif lower == "shift":
            stroke["shift"] = True
        elif lower == "meta":
            stroke["meta"] = True
        elif lower in {"cmd", "command", "super", "win"}:
            stroke["super"] = True
        elif lower == "esc":
            stroke["key"] = "escape"
        elif lower == "return":
            stroke["key"] = "enter"
        elif lower == "space":
            stroke["key"] = " "
        elif lower in {"up", "uparrow"}:
            stroke["key"] = "up"
        elif lower in {"down", "downarrow"}:
            stroke["key"] = "down"
        elif lower in {"left", "leftarrow"}:
            stroke["key"] = "left"
        elif lower in {"right", "rightarrow"}:
            stroke["key"] = "right"
        else:
            stroke["key"] = lower
    return stroke


def parseChord(input: str) -> Chord:
    if input == " ":
        return [parseKeystroke("space")]
    return [parseKeystroke(part) for part in input.strip().split() if part]


def _display_key(key: str) -> str:
    return {
        "escape": "Esc",
        " ": "Space",
        "enter": "Enter",
        "backspace": "Backspace",
        "delete": "Delete",
        "up": "Up",
        "down": "Down",
        "left": "Left",
        "right": "Right",
        "pageup": "PageUp",
        "pagedown": "PageDown",
        "home": "Home",
        "end": "End",
    }.get(key, key)


def keystrokeToString(ks: ParsedKeystroke) -> str:
    parts: list[str] = []
    if ks.get("ctrl"):
        parts.append("ctrl")
    if ks.get("alt"):
        parts.append("alt")
    if ks.get("shift"):
        parts.append("shift")
    if ks.get("meta"):
        parts.append("meta")
    if ks.get("super"):
        parts.append("cmd")
    parts.append(_display_key(str(ks.get("key", ""))))
    return "+".join(parts)


def chordToString(chord: Chord) -> str:
    return " ".join(keystrokeToString(ks) for ks in chord)


def keystrokeToDisplayString(ks: ParsedKeystroke, platform: str = "linux") -> str:
    parts: list[str] = []
    if ks.get("ctrl"):
        parts.append("ctrl")
    if ks.get("alt") or ks.get("meta"):
        parts.append("opt" if platform == "macos" else "alt")
    if ks.get("shift"):
        parts.append("shift")
    if ks.get("super"):
        parts.append("cmd" if platform == "macos" else "super")
    parts.append(_display_key(str(ks.get("key", ""))))
    return "+".join(parts)


def chordToDisplayString(chord: Chord, platform: str = "linux") -> str:
    return " ".join(keystrokeToDisplayString(ks, platform) for ks in chord)


def parseBindings(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    bindings: list[dict[str, Any]] = []
    for block in blocks:
        for key, action in (block.get("bindings") or {}).items():
            bindings.append({"chord": parseChord(str(key)), "action": action, "context": block.get("context")})
    return bindings
