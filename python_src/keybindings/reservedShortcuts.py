"""Reserved shortcut definitions and normalization."""

from __future__ import annotations

import platform

NON_REBINDABLE = [
    {"key": "ctrl+c", "reason": "Cannot be rebound - used for interrupt/exit (hardcoded)", "severity": "error"},
    {"key": "ctrl+d", "reason": "Cannot be rebound - used for exit (hardcoded)", "severity": "error"},
    {"key": "ctrl+m", "reason": "Cannot be rebound - identical to Enter in terminals", "severity": "error"},
]

TERMINAL_RESERVED = [
    {"key": "ctrl+z", "reason": "Unix process suspend (SIGTSTP)", "severity": "warning"},
    {"key": "ctrl+\\", "reason": "Terminal quit signal (SIGQUIT)", "severity": "error"},
]

MACOS_RESERVED = [
    {"key": "cmd+c", "reason": "macOS system copy", "severity": "error"},
    {"key": "cmd+v", "reason": "macOS system paste", "severity": "error"},
    {"key": "cmd+x", "reason": "macOS system cut", "severity": "error"},
    {"key": "cmd+q", "reason": "macOS quit application", "severity": "error"},
    {"key": "cmd+w", "reason": "macOS close window/tab", "severity": "error"},
    {"key": "cmd+tab", "reason": "macOS app switcher", "severity": "error"},
    {"key": "cmd+space", "reason": "macOS Spotlight", "severity": "error"},
]


def getReservedShortcuts() -> list[dict[str, str]]:
    reserved = [*NON_REBINDABLE, *TERMINAL_RESERVED]
    if platform.system().lower() == "darwin":
        reserved.extend(MACOS_RESERVED)
    return reserved


def _normalize_step(step: str) -> str:
    modifiers: list[str] = []
    main = ""
    for part in step.split("+"):
        lower = part.strip().lower()
        if lower in {"ctrl", "control", "alt", "opt", "option", "meta", "cmd", "command", "shift"}:
            if lower == "control":
                modifiers.append("ctrl")
            elif lower in {"option", "opt"}:
                modifiers.append("alt")
            elif lower in {"command", "cmd"}:
                modifiers.append("cmd")
            else:
                modifiers.append(lower)
        elif lower:
            main = lower
    modifiers.sort()
    return "+".join([*modifiers, main])


def normalizeKeyForComparison(key: str) -> str:
    return " ".join(_normalize_step(step) for step in key.strip().split())
