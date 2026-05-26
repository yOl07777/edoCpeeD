from __future__ import annotations

from pathlib import Path
from typing import Any


_state: dict[str, Any] = {"seenCount": 0, "complete": False}


def getSteps(cwd: str | None = None) -> list[dict[str, Any]]:
    root = Path(cwd or Path.cwd())
    return [
        {"id": "trust", "title": "确认工作目录", "complete": root.exists()},
        {"id": "readme", "title": "读取项目说明", "complete": (root / "README.md").exists()},
        {"id": "deepseek", "title": "配置 DeepSeek", "complete": bool((root / ".env").exists() or (root / ".env.example").exists())},
    ]


def isProjectOnboardingComplete(cwd: str | None = None) -> bool:
    return bool(_state["complete"] or all(step["complete"] for step in getSteps(cwd)))


def maybeMarkProjectOnboardingComplete(cwd: str | None = None) -> bool:
    complete = isProjectOnboardingComplete(cwd)
    _state["complete"] = complete
    return complete


def incrementProjectOnboardingSeenCount() -> int:
    _state["seenCount"] += 1
    return int(_state["seenCount"])


def shouldShowProjectOnboarding(cwd: str | None = None) -> bool:
    return not isProjectOnboardingComplete(cwd) and int(_state["seenCount"]) < 3
