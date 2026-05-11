from __future__ import annotations

from typing import Any

from python_src.services.compact.prompt import formatCompactSummary
from python_src.utils.messages.mappers import toSDKMessages


ERROR_MESSAGE_INCOMPLETE_RESPONSE = "Cannot compact an incomplete response."
ERROR_MESSAGE_NOT_ENOUGH_MESSAGES = "Not enough messages to compact."
ERROR_MESSAGE_PROMPT_TOO_LONG = "Compact prompt is too long."
ERROR_MESSAGE_USER_ABORT = "Compact aborted by user."
POST_COMPACT_MAX_FILES_TO_RESTORE = 8
POST_COMPACT_MAX_TOKENS_PER_FILE = 2_000
POST_COMPACT_MAX_TOKENS_PER_SKILL = 1_000
POST_COMPACT_SKILLS_TOKEN_BUDGET = 4_000
POST_COMPACT_TOKEN_BUDGET = 16_000


def _message_text(message: dict[str, Any]) -> str:
    content = message.get("content", "")
    if isinstance(content, str):
        return content
    return str(content)


async def stripImagesFromMessages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    stripped = []
    for message in messages:
        item = dict(message)
        content = item.get("content")
        if isinstance(content, list):
            item["content"] = [part for part in content if not (isinstance(part, dict) and part.get("type") in {"image", "image_url"})]
        stripped.append(item)
    return stripped


async def stripReinjectedAttachments(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [m for m in messages if not m.get("reinjected")]


async def truncateHeadForPTLRetry(messages: list[dict[str, Any]], keep_last: int = 8) -> list[dict[str, Any]]:
    return list(messages[-keep_last:])


async def annotateBoundaryWithPreservedSegment(messages: list[dict[str, Any]], boundary_index: int) -> list[dict[str, Any]]:
    annotated = [dict(m) for m in messages]
    if 0 <= boundary_index < len(annotated):
        annotated[boundary_index]["compact_boundary"] = True
    return annotated


async def mergeHookInstructions(*instructions: str | None) -> str:
    return "\n\n".join(item.strip() for item in instructions if item and item.strip())


async def compactConversation(
    messages: list[dict[str, Any]],
    *,
    preserve_last: int = 6,
    max_summary_chars: int = 6_000,
) -> dict[str, Any]:
    sdk_messages = await toSDKMessages(await stripImagesFromMessages(messages))
    if len(sdk_messages) <= preserve_last:
        return {"compacted": False, "messages": sdk_messages, "summary": "", "reason": ERROR_MESSAGE_NOT_ENOUGH_MESSAGES}
    older = sdk_messages[:-preserve_last]
    recent = sdk_messages[-preserve_last:]
    summary_lines = []
    for message in older:
        role = message.get("role", "user")
        text = str(message.get("content", "")).strip().replace("\n", " ")
        if text:
            summary_lines.append(f"{role}: {text}")
    summary = "\n".join(summary_lines)[:max_summary_chars]
    summary_message = {
        "role": "system",
        "content": await formatCompactSummary(summary, {"compacted_messages": len(older)}),
        "metadata": {"compact": True},
    }
    return {"compacted": True, "messages": [summary_message, *recent], "summary": summary}


async def partialCompactConversation(messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
    return await compactConversation(messages, preserve_last=kwargs.pop("preserve_last", 3), **kwargs)


async def buildPostCompactMessages(summary: str, recent_messages: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    return [{"role": "system", "content": await formatCompactSummary(summary)}, *(recent_messages or [])]


async def createPostCompactFileAttachments(files: list[str] | None = None, **_: Any) -> list[dict[str, Any]]:
    return [{"type": "file", "path": path} for path in (files or [])[:POST_COMPACT_MAX_FILES_TO_RESTORE]]


async def createSkillAttachmentIfNeeded(skill: dict[str, Any] | None = None) -> dict[str, Any] | None:
    return {"type": "skill", **skill} if skill else None


async def createPlanAttachmentIfNeeded(plan: dict[str, Any] | None = None) -> dict[str, Any] | None:
    return {"type": "plan", **plan} if plan else None


async def createPlanModeAttachmentIfNeeded(active: bool = False) -> dict[str, Any] | None:
    return {"type": "plan_mode", "active": True} if active else None


async def createAsyncAgentAttachmentsIfNeeded(agents: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    return [{"type": "agent", **agent} for agent in (agents or [])]


async def createCompactCanUseTool(allowed: bool = True) -> dict[str, bool]:
    return {"can_use_tool": allowed}
