from __future__ import annotations

import re
import secrets
from typing import Any


UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)


def validateUuid(maybeUuid: Any) -> str | None:
    return maybeUuid if isinstance(maybeUuid, str) and UUID_RE.match(maybeUuid) else None


def createAgentId(label: str | None = None) -> str:
    suffix = secrets.token_hex(8)
    return f"a{label}-{suffix}" if label else f"a{suffix}"
