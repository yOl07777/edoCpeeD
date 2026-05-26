"""Lightweight Python port of the color-diff native shim.

The TS implementation does syntax highlighting and word-level coloring. For
Python migration we keep the public classes and return stable, readable diff
lines without requiring highlight.js or native modules.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any

RESET = "\x1b[0m"
DIM = "\x1b[2m"
GREEN = "\x1b[32m"
RED = "\x1b[31m"
CYAN = "\x1b[36m"


@dataclass(frozen=True)
class SyntaxTheme:
    theme: str
    source: str | None = None

    def as_dict(self) -> dict[str, str | None]:
        return {"theme": self.theme, "source": self.source}


def _default_syntax_theme_name(theme_name: str) -> str:
    if "ansi" in theme_name:
        return "ansi"
    if "dark" in theme_name:
        return "Monokai Extended"
    return "GitHub"


def _line_number_width(hunk: dict[str, Any]) -> int:
    old_end = max(0, int(hunk.get("oldStart", 1)) + int(hunk.get("oldLines", 0)) - 1)
    new_end = max(0, int(hunk.get("newStart", 1)) + int(hunk.get("newLines", 0)) - 1)
    return len(str(max(old_end, new_end, 1)))


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def _clip(text: str, width: int) -> str:
    plain_len = len(_strip_ansi(text))
    if width <= 0 or plain_len <= width:
        return text
    return _strip_ansi(text)[: max(1, width - 1)] + "…"


class ColorDiff:
    def __init__(
        self,
        hunk: dict[str, Any],
        firstLine: str | None,
        filePath: str,
        prefixContent: str | None = None,
    ) -> None:
        self.hunk = hunk
        self.firstLine = firstLine
        self.filePath = filePath
        self.prefixContent = prefixContent

    def render(self, themeName: str = "dark", width: int = 120, dim: bool = False) -> list[str] | None:
        max_digits = _line_number_width(self.hunk)
        old_line = int(self.hunk.get("oldStart", 1))
        new_line = int(self.hunk.get("newStart", 1))
        out: list[str] = []

        for raw in list(self.hunk.get("lines", [])):
            raw = str(raw)
            marker = raw[:1] if raw[:1] in {"+", "-", " "} else " "
            code = raw[1:] if raw[:1] in {"+", "-", " "} else raw
            if marker == "+":
                number = new_line
                new_line += 1
                color = GREEN
            elif marker == "-":
                number = old_line
                old_line += 1
                color = DIM if dim else RED
            else:
                number = new_line
                old_line += 1
                new_line += 1
                color = ""
            prefix = f"{number:>{max_digits}} {marker} "
            line = f"{prefix}{color}{code}{RESET if color else ''}"
            out.append(_clip(line, width))
        return out


class ColorFile:
    def __init__(self, code: str, filePath: str) -> None:
        self.code = code
        self.filePath = filePath

    def render(self, themeName: str = "dark", width: int = 120, dim: bool = False) -> list[str] | None:
        lines = self.code.splitlines()
        digits = len(str(max(1, len(lines))))
        rendered = []
        for index, line in enumerate(lines, start=1):
            prefix = f"{CYAN}{index:>{digits}}{RESET}  "
            rendered.append(_clip(prefix + line, width))
        return rendered


def getSyntaxTheme(themeName: str = "dark") -> dict[str, str | None]:
    env_theme = os.environ.get("DEEPSEEK_CODE_SYNTAX_HIGHLIGHT") or os.environ.get(
        "CLAUDE_CODE_SYNTAX_HIGHLIGHT"
    ) or os.environ.get("BAT_THEME")
    return SyntaxTheme(theme=env_theme or _default_syntax_theme_name(themeName), source=None).as_dict()


def getNativeModule() -> dict[str, Any]:
    return {"ColorDiff": ColorDiff, "ColorFile": ColorFile, "getSyntaxTheme": getSyntaxTheme}


__test = {"strip_ansi": _strip_ansi, "defaultSyntaxThemeName": _default_syntax_theme_name}

__all__ = [
    "ColorDiff",
    "ColorFile",
    "SyntaxTheme",
    "__test",
    "getNativeModule",
    "getSyntaxTheme",
]
