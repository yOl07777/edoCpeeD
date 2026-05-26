from __future__ import annotations

import difflib
from typing import Any

from ._basic import first_mapping, pick


async def useTurnDiffs(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    before = str(pick(options, "before", "old", default=""))
    after = str(pick(options, "after", "new", default=""))
    diff = list(difflib.unified_diff(before.splitlines(), after.splitlines(), lineterm=""))
    return {
        "provider": "deepseek",
        "diff": "\n".join(diff),
        "additions": sum(1 for line in diff if line.startswith("+") and not line.startswith("+++")),
        "removals": sum(1 for line in diff if line.startswith("-") and not line.startswith("---")),
    }
