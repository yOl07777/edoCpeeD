from __future__ import annotations

import os
from typing import Any

ADDITIONAL_HYPERLINK_TERMINALS = {"vscode", "cursor", "windsurf", "iterm.app", "wezterm", "kitty"}


async def supportsHyperlinks(*args: Any, **kwargs: Any) -> Any:
    env = kwargs.get("env") or os.environ
    term_program = str(kwargs.get("termProgram", env.get("TERM_PROGRAM", ""))).lower()
    term = str(kwargs.get("term", env.get("TERM", ""))).lower()
    return term_program in ADDITIONAL_HYPERLINK_TERMINALS or "xterm" in term or "kitty" in term
