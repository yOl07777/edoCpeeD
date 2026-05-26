"""JSON serialization safe for one-message-per-line transports."""

from __future__ import annotations

import json
from typing import Any


def ndjsonSafeStringify(value: Any) -> str:
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"), default=str)
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
