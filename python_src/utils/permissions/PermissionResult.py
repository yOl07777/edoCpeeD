from __future__ import annotations


async def getRuleBehaviorDescription(behavior: str) -> str:
    return {
        "allow": "允许该工具调用，无需再次询问。",
        "ask": "调用该工具前需要询问用户确认。",
        "deny": "拒绝该工具调用。",
    }.get(behavior, "未知权限行为。")
