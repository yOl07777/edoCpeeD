"""Environment expansion helpers for migrated MCP configuration."""

from __future__ import annotations

import os
import re
from typing import Mapping

_ENV_RE = re.compile(r"\$(\w+)|\$\{([^}:]+)(?::-(.*?))?\}|%([^%]+)%")


async def expandEnvVarsInString(value: str, env: Mapping[str, str] | None = None) -> str:
    """Expand shell-style and Windows-style environment references.

    Supported forms are ``$NAME``, ``${NAME}``, ``${NAME:-fallback}``, and
    ``%NAME%``. Unknown variables expand to an empty string unless a fallback
    is supplied.
    """

    source = env or os.environ

    def replace(match: re.Match[str]) -> str:
        key = match.group(1) or match.group(2) or match.group(4) or ""
        default = match.group(3)
        if key in source:
            return str(source[key])
        return "" if default is None else default

    return _ENV_RE.sub(replace, value or "")
