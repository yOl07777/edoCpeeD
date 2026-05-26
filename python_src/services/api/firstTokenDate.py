"""First-token date helper for DeepSeek migration compatibility."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


async def fetchAndStoreClaudeCodeFirstTokenDate(path: str | Path | None = None, value: str | None = None) -> dict[str, Any]:
    """Store the first token date locally.

    The original name is preserved for API compatibility; this migration does
    not call Claude services.
    """

    target = Path(path or os.getenv("DEEPSEEK_FIRST_TOKEN_DATE_PATH", ".deepseek_first_token_date")).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and value is None:
        stored = target.read_text(encoding="utf-8").strip()
    else:
        stored = value or datetime.now(timezone.utc).isoformat()
        target.write_text(stored, encoding="utf-8")
    return {"path": str(target), "first_token_date": stored}

